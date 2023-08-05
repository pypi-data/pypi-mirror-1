%{
    /*************************************************************************
     *                                                                       *
     * helpers_channel.i -- SWIG Interface definition for                    *
     *                      Embedded Python Interpreter for Asterisk         *
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

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

%}

%inline %{

    char *ast_channel_get_name(struct ast_channel *c) {
	if(!c) return NULL;
	return c->name;
    }

    char *ast_channel_get_language(struct ast_channel *c) {
	if(!c) return NULL;
	return c->language;
    }

    char *ast_channel_get_type(struct ast_channel *c) {
	if(!c) return NULL;
	return c->tech->type;
    }

    struct ast_channel *ast_channel_get_masq(struct ast_channel *c) {
	if(!c) return NULL;
	return c->masq;
    }

    struct ast_channel *ast_channel_get_masqr(struct ast_channel *c) {
	if(!c) return NULL;
	return c->masqr;
    }

    char *ast_channel_get_app(struct ast_channel *c) {
	if(!c) return NULL;
	return c->appl;
    }
    
    char *ast_channel_get_data(struct ast_channel *c) {
	if(!c) return NULL;
	return c->data;
    }

//#ifdef ASTERISK_HEAD
    char *ast_channel_get_dnid(struct ast_channel *c) {
	if(!c) return NULL;
	return c->cid.cid_dnid;
    }

    char *ast_channel_get_callerid(struct ast_channel *c) {
	if(!c) return NULL;
	return c->cid.cid_num;
    }

    char *ast_channel_get_ani(struct ast_channel *c) {
	if(!c) return NULL;
	return c->cid.cid_ani;
    }

    char *ast_channel_get_rdnis(struct ast_channel *c) {
	if(!c) return NULL;
	return c->cid.cid_rdnis;
    }
//#endif /* ASTERISK_HEAD */

/*
#ifndef ASTERISK_HEAD
    char *ast_channel_get_dnid(struct ast_channel *c) {
	if(!c) return NULL;
	return c->dnid;
    }

    char *ast_channel_get_callerid(struct ast_channel *c) {
	if(!c) return NULL;
	return c->callerid;
    }

    char *ast_channel_get_ani(struct ast_channel *c) {
	if(!c) return NULL;
	return c->ani;
    }

    char *ast_channel_get_rdnis(struct ast_channel *c) {
	if(!c) return NULL;
	return c->rdnis;
    }

    int ast_channel_get_restrictcid(struct ast_channel *c) {
	if(!c) return -1;
	return c->restrictcid;
    }

    int ast_channel_get_callingpres(struct ast_channel *c) {
	if(!c) return -1;
	return c->callingpres;
    }
#endif
*/

    char *ast_channel_get_context(struct ast_channel *c) {
	if(!c) return NULL;
	return c->context;
    }

    char *ast_channel_get_exten(struct ast_channel *c) {
	if(!c) return NULL;
	return c->exten;
    }

    int ast_channel_get_priority(struct ast_channel *c) {
	if(!c) return -1;
	return c->priority;
    }

    char *ast_channel_get_macrocontext(struct ast_channel *c) {
	if(!c) return NULL;
	return c->macrocontext;
    }

    char *ast_channel_get_macroexten(struct ast_channel *c) {
	if(!c) return NULL;
	return c->macroexten;
    }

    int ast_channel_get_macropriority(struct ast_channel *c) {
	if(!c) return -1;
	return c->macropriority;
    }

    struct ast_cdr *ast_channel_get_cdr(struct ast_channel *c) {
	if(!c) return NULL;
	return c->cdr;
    }

    char *ast_channel_get_uniqueid(struct ast_channel *c) {
	if(!c) return NULL;
	return c->uniqueid;
    }

    char *ast_channel_get_accountcode(struct ast_channel *c) {
	if(!c) return NULL;
	return c->accountcode;
    }


    void ast_lock_channel(struct ast_channel *c) {
	if(!c) return;
	ast_mutex_lock(&c->lock);
    }

    void ast_unlock_channel(struct ast_channel *c) {
	if(!c) return;
	ast_mutex_unlock(&c->lock);
    }

    struct ast_channel *ast_channel_byname_locked(char *name) {
	struct ast_channel *c;
	if(!name) return NULL;
	c = ast_channel_walk_locked(NULL);
	while(c) {
	    if(!strcasecmp(c->name, name))
		return c;
	    ast_mutex_unlock(&c->lock);
	    c = ast_channel_walk_locked(c);
	}
	return NULL;
    }

    struct ast_channel *ast_channel_byname(char *name) {
	struct ast_channel *c;
	c = ast_channel_byname_locked(name);
	if(c)
	    ast_mutex_unlock(&c->lock);
	return c;
    }

    PyObject *ast_channel_keys(struct ast_channel *c) {
	PyObject *keys;
	struct ast_var_t *var;
	struct varshead *headp = &c->varshead;
	if(!c) return NULL;
	keys = PyList_New(0);
	if(!keys) return NULL;
	
	AST_LIST_TRAVERSE (headp,var,entries) {
	    PyObject *key = PyString_FromString(ast_var_name(var));
	    if(key)
		PyList_Append(keys, key);
	}
	
	return keys;
    }

#ifdef ASTERISK_HAS_GETPEER

    PyObject *ast_getpeer(struct ast_channel *c)
      {
	struct sockaddr_in *sin;
	char addr[128], *ap;
	PyObject *pyaddr, *pyport, *tup;

	if (!c || !c->tech || !c->tech->get_peer) {
	  Py_INCREF(Py_None);
	  return Py_None;
	}

	sin = c->tech->get_peer(c);

	if (!sin) {
	  Py_INCREF(Py_None);
	  return Py_None;
	}

	ast_inet_ntoa(addr, sizeof(addr), sin->sin_addr);
	pyaddr = PyString_FromFormat("%s", addr);
	pyport = PyInt_FromLong(sin->sin_port);

	tup = PyTuple_New(2);
	PyTuple_SetItem(tup, 0, pyaddr);
	PyTuple_SetItem(tup, 1, pyport);

	return tup;
      }
#endif /* ASTERISK_HAS_GETPEER */

%}

