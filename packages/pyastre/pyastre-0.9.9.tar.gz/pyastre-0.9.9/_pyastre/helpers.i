
%{
    /*************************************************************************
     *                                                                       *
     * helpers.i -- SWIG Interface definition for                            *
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

    /*
     * Helper function to convert an ast_channel pointer to a python
     * object, mostly for use in app_python.c
     */
    PyObject *Pyastre_BuildChannelObj(struct ast_channel *c)
	{
	    PyObject *resultobj;
	    resultobj = SWIG_NewPointerObj((void *)c, SWIGTYPE_p_ast_channel, 0);
	    return resultobj;
	}
%}

%inline %{

    int ast_originate(char *src,
		      char *outctx, char *outext, int outprio,
		      char *cid, char *cidname, char *account, struct ast_variable *vars, int timeout)
	{
	    int reason = 0, ret;

	    if(!src || !outctx || !outext)
		return -1;
	    if(!timeout) timeout = 30000;
	    if(!vars) vars = NULL;
	    
	    ast_verbose("Calling %s/%s from %s as %s for %s\n",
			outctx, outext, src, cid, account);

	    Py_BEGIN_ALLOW_THREADS
		ret = ast_pbx_outgoing_exten("Local", AST_FORMAT_SLINEAR, src, timeout,
					     outctx, outext, outprio,
					     &reason, 2, cid, cidname, vars, account, NULL); 

	    Py_END_ALLOW_THREADS;
            return ret;
	}

%}
