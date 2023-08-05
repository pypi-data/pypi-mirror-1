/*************************************************************************
 *                                                                       *
 * asterisk.c -- Embedded Python Interpreter for Asterisk                *
 *                                                                       *
 * Copyright (C) 2004, 2005 by William Waites <ww@groovy.net>            *
 * Copyright (C) 2004, 2005 by Consultants Ars Informatica S.A.R.F.      *
 *                                                                       *
 * This program is free software; you can redistribute it and*or modify  *
 * it under the terms of the GNU Library General Public License as       *
 * published by the Free Software Foundation; either version 2 of the    *
 * License, or (at your option) any later version.                       *
 *                                                                       *
 * This program is distributed in the hope that it will be useful,       *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 * GNU General Public License for more details.                          *
 *                                                                       *
 * You should have received a copy of the GNU Library General Public     *
 * License along with this program; if not, write to the                 *
 * Free Software Foundation, Inc.,                                       *
 * 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
 *                                                                       *
 *************************************************************************/

#include <Python.h>
#include <pthread.h>

#include <asterisk/app.h>
#include <asterisk/pbx.h>
#include <asterisk/config.h>
#include <asterisk/channel.h>
#include <asterisk/module.h>
#include <asterisk/logger.h>
#include <asterisk/lock.h>

#include "pyastre.h"

#define PYASTRE_NAME "pyastre"

#ifdef ASTERISK_1_0
#define ast_pthread_create pthread_create
#endif

static char mod_desc[] = "A Python in the DialPlan";
static pthread_t interp_thread;
static PyInterpreterState *interp = NULL;
static PyObject *cdr_func = NULL;
static PyObject *start_func = NULL;
static PyObject *stop_func = NULL;
static PyObject *pdb_obj = NULL;

STANDARD_LOCAL_USER;
LOCAL_USER_DECL;

/*
 * The Python application callable from the dialplan
 */
static char app[] = "Python";
static char app_synopsis[] = "Execute a python script";
static char app_ldesc[] =
"  Python(args)\n\n"
"This will cause the embedded python interpreter to import the\n"
"execute() method from the 'foo' module which must be in sys.path\n"
"The method is called as foo.execute(chan, args) where args are\n"
"optionally passed in the dialplan as above, and chan is the name\n"
"of the channel that can be used as a key in the Pyastre API\n";
static int app_python(struct ast_channel *chan, void *data)
{
    PyThreadState *tstate;
    PyObject *module_name, *module, *dict, *func, *chanp, *datap, *arglist;
    PyObject *err;
    int res = 0;
    char script[256], *arg;

    /* we can't run apps without an interpreter */
    if(!interp)
	return -1;

    /* tell asterisk we are in use */
    /* res = LOCAL_USER_ADD(u);
    if(res)
	return res;
    */

    /* extract the script name from our arguments */
    memset(script, 0, sizeof(script));
    arg = strchr((char *)data, '|');
    if(arg) {
	int len = arg - (char *)data;
	strncpy(script, data, len < sizeof(script) ? len : sizeof(script));
    } else {
	strncpy(script, data, sizeof(script));
    }

    /* make a new thread for us */
    tstate = PyThreadState_New(interp);
    if(!tstate) {
	//	LOCAL_USER_REMOVE(u);
	return -1;
    }

    /* acquire the thread state */
    PyEval_AcquireThread(tstate); 

    /* get the module name */
    module_name = PyString_FromString(script);
    if(!module_name) {
	ast_log(LOG_ERROR, "Python cannot allocate string\n");
	res = -1;
	goto cleanup;
    }

    /* import the module, after we don't need the nmae anymore */
    module = PyImport_Import(module_name);
    Py_DECREF(module_name);

    if(!module) {
	ast_log(LOG_ERROR, "Unable to import %s\n", script);
	res = -1;
	goto cleanup;
    }

    /* get dictionary of symbols for module -- dict ref is borrowed */
    dict = PyModule_GetDict(module);
    if(!dict) {
	ast_log(LOG_ERROR, "Unable to get module dictionary for %s\n", script);
	Py_DECREF(module);
	res = -1;
	goto cleanup;
    }

    /* look for the execute function -- func ref is borrowed */
    func = PyDict_GetItemString(dict, "execute");
    if(!func || !PyCallable_Check(func)) {
	ast_log(LOG_ERROR, "%s.execute does not exist or is not callable\n", script);
	Py_DECREF(module);
	res = -1;
	goto cleanup;
    }

    /* build the arguments to the function */
    if(arg)
	arglist = PyTuple_New(2);
    else
	arglist = PyTuple_New(1);
    
    if(!arglist) {
	ast_log(LOG_ERROR, "Cannot allocate arguments\n");
	Py_DECREF(module);
	res = -1;
	goto cleanup;
    }

    chanp = Pyastre_BuildChannelObj(chan);
    if(!chanp) {
	ast_log(LOG_ERROR, "Cannot allocate Python channel object\n");
	Py_DECREF(arglist);
	Py_DECREF(module);
	res = -1;
	goto cleanup;
    }
    /* borrows reference to chanp */
    PyTuple_SetItem(arglist, 0, chanp);

    if(arg) {
	/* because of the strchr above, arg should be pointing to the
	 * comma in the argument list from the dialplan. eat the !.
	 */
	arg++;
	/* eat whitespace */
	while(isspace(*arg))
	    arg++;
	datap = PyString_FromString(arg);
	if(!datap) {
	    Py_DECREF(arglist);
	    Py_DECREF(module);
	    res = -1;
	    goto cleanup;
	}
	PyTuple_SetItem(arglist, 1, datap);
    }
  
    /* finally, run the function */
    PyObject_CallObject(func, arglist);
    
    err = PyErr_Occurred();
    if(err) {
	PyErr_Print();
	res = -1;
    }

    Py_DECREF(arglist);
    Py_DECREF(module);

 cleanup:
    PyEval_ReleaseThread(tstate);
    PyThreadState_Delete(tstate);

    //LOCAL_USER_REMOVE(u);
    return res;
}

/*
 * The Python Pluggable DB Function
 */
static char * function_pdb_read(struct ast_channel *chan, char *cmd, char *data, char *buf, size_t len)
{
    PyThreadState *tstate;
    PyObject *p_family, *p_key, *p_ktuple, *p_value;
    PyObject *err;
    int argc;
    char *args;
    char *argv[2];
    char *family;
    char *key;

    if(!pdb_obj)
	return buf;
    
    if(!interp)
	return buf;

    if (ast_strlen_zero(data)) {
	ast_log(LOG_WARNING, "PDB requires an argument, PDB(<family>/<key>)\n");
	return buf;
    }

    args = ast_strdupa(data);
    argc = ast_app_separate_args(args, '/', argv, sizeof(argv) / sizeof(argv[0]));

    if (argc > 1) {
	family = argv[0];
	key = argv[1];
    } else {
	ast_log(LOG_WARNING, "PDB requires an argument, PDB(<family>/<key>)\n");
	return buf;
    }

    tstate = PyThreadState_New(interp);
    if(!tstate) {
	return buf;
    }

    PyEval_AcquireThread(tstate);
    
    p_family = PyString_FromString(family);
    if(!p_family) goto cleanup;

    p_key = PyString_FromString(key);
    if(!p_key) { Py_DECREF(p_family); goto cleanup; }

    p_ktuple = PyTuple_New(2);
    if(!p_ktuple) { Py_DECREF(p_family); Py_DECREF(p_key); goto cleanup; }

    PyTuple_SetItem(p_ktuple, 0, p_family);
    PyTuple_SetItem(p_ktuple, 1, p_key);

    p_value = PyDict_GetItem(pdb_obj, p_ktuple);
    Py_DECREF(p_ktuple);

    if(p_value) {
	strncpy(buf, PyString_AsString(p_value), len);
	pbx_builtin_setvar_helper(chan, "DB_RESULT", buf);
    }

 cleanup:
    err = PyErr_Occurred();
    if(err) {
	PyErr_Print();
    }
    
    PyEval_ReleaseThread(tstate);
    PyThreadState_Delete(tstate);

    return buf;
}

static void function_pdb_write(struct ast_channel *chan, char *cmd, char *data, const char *value)
{
    PyThreadState *tstate;
    PyObject *p_family, *p_key, *p_ktuple, *p_value;
    PyObject *err;
    int argc;
    char *args;
    char *argv[2];
    char *family;
    char *key;

    if(!pdb_obj)
	return;
    
    if(!interp)
	return;

    if (ast_strlen_zero(data)) {
	ast_log(LOG_WARNING, "PDB requires an argument, PDB(<family>/<key>)=<value>\n");
	return;
    }

    args = ast_strdupa(data);
    argc = ast_app_separate_args(args, '/', argv, sizeof(argv) / sizeof(argv[0]));

    if (argc > 1) {
	family = argv[0];
	key = argv[1];
    } else {
	ast_log(LOG_WARNING, "PDB requires an argument, PDB(<family>/<key>)=value\n");
	return;
    }

    tstate = PyThreadState_New(interp);
    if(!tstate) {
	return;
    }

    PyEval_AcquireThread(tstate);
    
    p_family = PyString_FromString(family);
    if(!p_family) goto cleanup;

    p_key = PyString_FromString(key);
    if(!p_key) { Py_DECREF(p_family); goto cleanup; }

    p_ktuple = PyTuple_New(2);
    if(!p_ktuple) { Py_DECREF(p_family); Py_DECREF(p_key); goto cleanup; }

    PyTuple_SetItem(p_ktuple, 0, p_family);
    PyTuple_SetItem(p_ktuple, 1, p_key);

    p_value = PyString_FromString(value);

    if(p_value) {
	PyDict_SetItem(pdb_obj, p_ktuple, p_value);
	Py_DECREF(p_value);
    }
    Py_DECREF(p_ktuple);

 cleanup:
    err = PyErr_Occurred();
    if(err) {
	PyErr_Print();
    }
    
    PyEval_ReleaseThread(tstate);
    PyThreadState_Delete(tstate);

    return;
}

struct ast_custom_function pdb_function = {
    .name = "PDB",
    .synopsis = "Read or Write from/to a pluggable back-end database",
    .syntax = "PDB(<family>/<key>)",
    .desc = "This function will read or write a value from/to an arbitrary\n"
            "back-end databse. PDB(...) will read a value from the database\n"
            "while PDB(...)=value will write it to the database. On a read this\n"
            "function returns the value from the database, or NULL if it does\n"
            "not exist. On a write this function will always return NULL. Reading\n"
            "a database value will also set the channel variable DB_RESULT.\n\n"
            "The back-end database is implemented by an object instance that\n"
            "must be importable as 'from softswitch import pdb' and must support\n"
            "the python __getitem__ and __setitem__ special methods.\n",
    .read = function_pdb_read,
    .write = function_pdb_write,
};

/*
 * The handler for Call Detail Records
 */
static char *cdr_name = "cdr_python";
static char *cdr_desc = "Python CDR Backend";
static int cdr_python(struct ast_cdr *cdr)
{
    PyThreadState *tstate;
    PyObject *cdrobj, *args;
    PyObject *err;
    int res = 0;
    
    if(!cdr_func)
	return -1;
    
    if(!interp)
	return -1;

    tstate = PyThreadState_New(interp);
    if(!tstate) {
	return -1;
    }

    PyEval_AcquireThread(tstate);
    
    cdrobj = Pyastre_BuildCdrObj(cdr);
    if(!cdrobj) {
	ast_log(LOG_ERROR, "Could not build CDR object\n");
	res = -1;
	goto cleanup;
    }

    args = PyTuple_New(1);
    if(!args) {
	ast_log(LOG_ERROR, "Could not build tuple\n");
	res = -1;
	Py_DECREF(cdrobj);
	goto cleanup;
    }
    PyTuple_SetItem(args, 0, cdrobj);
    
    PyObject_CallObject(cdr_func, args);

    err = PyErr_Occurred();
    if(err) {
	res = -1;
	PyErr_Print();
    }

    Py_DECREF(args);
    
 cleanup:
    
    PyEval_ReleaseThread(tstate);
    PyThreadState_Delete(tstate);

    return res;
}


/*
 * Initialize the python interpreter and top level
 * objects
 */
static void *interp_proc(void *dummy)
	/* ARGUSED */
{
    PyThreadState *tstate;
    PyObject *module_name, *module, *dict, *args, *err;

    ast_verbose(">>> Initializing Python Interpreter.\n");
    ast_verbose(">>> Python %s %s\n", Py_GetPlatform(), Py_GetVersion());

    Py_SetProgramName(PYASTRE_NAME);
    PyEval_InitThreads();
    Py_Initialize();

    init_asterisk();

    /* Save the main thread... */
    tstate = PyEval_SaveThread();
    interp = tstate->interp;
    PyEval_RestoreThread(tstate);

    /* Set up the search path */
    PyRun_SimpleString("import sys\n"
		       "if '" SCRIPT_DIR "' not in sys.path:\n"
		       "    sys.path.append('" SCRIPT_DIR "')\n");
		       
    module_name = PyString_FromString(SOFTSWITCH_MODULE);
    if(!module_name) {
	ast_log(LOG_ERROR, "Unable to allocate string '" SOFTSWITCH_MODULE "'\n");
    } else {
	/* import hteh softswitch module */
	module = PyImport_Import(module_name);
	Py_DECREF(module_name);
	
	if(!module) {
	    ast_log(LOG_ERROR, "Unable to import " SOFTSWITCH_MODULE "\n");
	    err = PyErr_Occurred();
	    PyErr_Print();
	} else {
	    /* look in the module's dictionary for the cdr function */
	    dict = PyModule_GetDict(module);
	    /* dict is a borrowed reference */
	    if(!dict) {
		ast_log(LOG_ERROR, "Unable to get " SOFTSWITCH_MODULE ".__dict__\n");
		err = PyErr_Occurred();
		PyErr_Print();
	    } else {
		/*
		 * references to these callables are likewise 
		 * borrowed so we need to increase their reference
		 * count since we won't keep around the module 
		 * reference
		 */
		start_func = PyDict_GetItemString(dict, "run");
		if(start_func) {
		    if(PyCallable_Check(start_func))
			Py_INCREF(start_func);
		    else
			start_func = NULL;
		}
		
		stop_func = PyDict_GetItemString(dict, "stop");
		if(stop_func) {
		    if(PyCallable_Check(stop_func))
			Py_INCREF(stop_func);
		    else
			stop_func = NULL;
		}
		
		cdr_func = PyDict_GetItemString(dict, "cdr");
		if(cdr_func) {
		    if(PyCallable_Check(cdr_func)) {
			Py_INCREF(cdr_func);
			ast_cdr_register(cdr_name, cdr_desc, cdr_python);	
		    } else {
			cdr_func = NULL;
		    }
		}

		pdb_obj = PyDict_GetItemString(dict, "pdb");
		if(pdb_obj) {
		    if(PyDict_Check(pdb_obj)) {
			Py_INCREF(pdb_obj);
			ast_custom_function_register(&pdb_function);
		    } else {
			pdb_obj = NULL;
		    }
		}
	    }
	    Py_DECREF(module);
	}

	if(start_func) {
	    args = PyTuple_New(0);
	    PyObject_CallObject(start_func, args);
	    err = PyErr_Occurred();
	    Py_DECREF(args);
	    if(err)
		PyErr_Print();
	} else {
	    ast_log(LOG_WARNING, "No callable " SOFTSWITCH_MODULE ".run\n");
	}
	
	ast_log(LOG_NOTICE, "Main Python thread returned\n");
    }
    return NULL;
}


int load_module(void)
{
    int res;

    ast_verbose("\n\n>>> " PYASTRE_NAME " " PYASTRE_VERSION "\n"
		PYASTRE_COPYRIGHT "\n\n");

    if(ast_pthread_create(&interp_thread, NULL, interp_proc, NULL)) {
	ast_log(LOG_ERROR, "Unable to create python interpreter\n");
	return -1;
    }

    res = ast_register_application(app, app_python, app_synopsis, app_ldesc);

    return res;
}

int unload_module(void)
{
    PyThreadState *tstate;
    PyObject *args, *err;

    STANDARD_HANGUP_LOCALUSERS;

    /*
     * Take away the dialplan script handler
     */
    ast_unregister_application(app);

    ast_log(LOG_NOTICE, "Terminating Python Interpreter.\n");

    if(interp) {
	/* interp is your reference to an interpreter object. */
	tstate = PyThreadState_New(interp);
	PyEval_AcquireThread(tstate);

	if(stop_func) {
	    args = PyTuple_New(0);
	    PyObject_CallObject(stop_func, args);
	    err = PyErr_Occurred();
	    Py_DECREF(args);
	    if(err)
		PyErr_Print();
	} else {
	    ast_log(LOG_ERROR, "No callable " SOFTSWITCH_MODULE ".stop\n");
	}
  
	/*
	 * Time to clean up our entry points into the python
	 * code.
	 */
	if(start_func) {
	    Py_DECREF(start_func);
	    start_func = NULL;
	}

	if(stop_func) {
	    Py_DECREF(stop_func);
	    stop_func = NULL;
	}

	if(cdr_func) {
	    ast_cdr_unregister(cdr_name);
	    Py_DECREF(cdr_func);
	    cdr_func = NULL;
	}

	if(pdb_obj) {
	    ast_custom_function_unregister(&pdb_function);
	    Py_DECREF(pdb_obj);
	    pdb_obj = NULL;
	}

	/* Release the thread. No Python API allowed beyond this point. */
	PyEval_ReleaseThread(tstate);
	PyThreadState_Delete(tstate);
    }

    Py_Finalize();
    interp = NULL;

    ast_log(LOG_NOTICE, "\n>>> " PYASTRE_NAME " " PYASTRE_VERSION " unloaded.\n");
    return 0;
}

char *description(void)
{
    return mod_desc;
}

int usecount(void)
{
    int res;
    STANDARD_USECOUNT(res);
    return res;
}

char *key()
{
    return ASTERISK_GPL_KEY;
}
