%module asterisk

%{
/*************************************************************************
 *                                                                       *
 * pyastre.i -- SWIG Interface definition for                            *
 *              Embedded Python Interpreter for Asterisk                 *
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

#include <pthread.h>
#include <asterisk/pbx.h>
#include <asterisk/config.h>
#include <asterisk/channel.h>
#include <asterisk/module.h>
#include <asterisk/logger.h>
#include <asterisk/lock.h>
#include <asterisk/astdb.h>

%}

%include helpers.i
%include helpers_cdr.i
%include helpers_channel.i

void ast_verbose(char *);

/*
  struct ast_channel *ast_channel_alloc(int);
  void ast_channel_free(struct ast_channel *);
*/

struct ast_app *pbx_findapp(char *);
void ast_softhangup(struct ast_channel *, int);

char *pbx_builtin_getvar_helper(struct ast_channel *, char *);
void pbx_builtin_setvar_helper(struct ast_channel *, char *, char *);
void ast_func_write(struct ast_channel *chan, const char *in, const char *value);

void reload(void);

%inline %{
    int ast_db_setitem(const char *family, const char *key, char *value) {
	return ast_db_put(family, key, value);
    }

    PyObject *ast_db_getitem(char *family, char *key) {
	char buf[BUFSIZ];
	if(ast_db_get(family, key, buf, BUFSIZ))
	    return NULL;
	return PyString_FromString(buf);
    }

    int ast_exec(struct ast_channel *c, struct ast_app *app, char *args, int flags) {
	int ret;
	Py_BEGIN_ALLOW_THREADS
	    ret = pbx_exec(c, app, args, flags);
	Py_END_ALLOW_THREADS;
	return ret;
    }

    PyObject *ast_func_readp(struct ast_channel *chan, const char *in) {
        char buf[BUFSIZ];
	char *ret;
	ret = ast_func_read(chan, in, buf, BUFSIZ);
	if(!ret)
	    return NULL;
	return PyString_FromString(buf);
    }

%}
