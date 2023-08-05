
%{
    /*************************************************************************
     *                                                                       *
     * helpers_cdr.i -- SWIG Interface definition for                        *
     *                  Embedded Python Interpreter for Asterisk             *
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
     * Helper function to convert an ast_cdr pointer to a python
     * object for use in cdr_python.c
     */
    PyObject * Pyastre_BuildCdrObj(struct ast_cdr *cdr) {
	PyObject *resultobj;
	resultobj = SWIG_NewPointerObj((void *)cdr, SWIGTYPE_p_ast_cdr, 0);
	return resultobj;
    }
%}

%inline %{

    char *ast_cdr_get_accountcode(struct ast_cdr *cdr) {
	if(!cdr) return NULL;
	return cdr->accountcode;
    }

    char *ast_cdr_get_src(struct ast_cdr *cdr) {
	if(!cdr) return NULL;
	return cdr->src;
    }
    
    char *ast_cdr_get_dst(struct ast_cdr *cdr) {
	if(!cdr) return NULL;
	return cdr->dst;
    }

    char *ast_cdr_get_dcontext(struct ast_cdr *cdr) {
	if(!cdr) return NULL;
	return cdr->dcontext;
    }

    char *ast_cdr_get_clid(struct ast_cdr *cdr) {
	if(!cdr) return NULL;
	return cdr->clid;
    }

    char *ast_cdr_get_channel(struct ast_cdr *cdr) {
	if(!cdr) return NULL;
	return cdr->channel;
    }

    char *ast_cdr_get_dstchannel(struct ast_cdr *cdr) {
	if(!cdr) return NULL;
	return cdr->dstchannel;
    }

    char *ast_cdr_get_lastapp(struct ast_cdr *cdr) {
	if(!cdr) return NULL;
	return cdr->lastapp;
    }
    
    char *ast_cdr_get_lastdata(struct ast_cdr *cdr) {
	if(!cdr) return NULL;
	return cdr->lastdata;
    }

    int ast_cdr_get_start(struct ast_cdr *cdr) {
	if(!cdr) return -1;
	return cdr->start.tv_sec;
    }

    int ast_cdr_get_answer(struct ast_cdr *cdr) {
	if(!cdr) return -1;
	return cdr->answer.tv_sec;
    }

    int ast_cdr_get_finish(struct ast_cdr *cdr) {
	if(!cdr) return -1;
	return cdr->end.tv_sec;
    }

    int ast_cdr_get_duration(struct ast_cdr *cdr) {
	if(!cdr) return -1;
	return cdr->duration;
    }

    int ast_cdr_get_billsec(struct ast_cdr *cdr) {
	if(!cdr) return -1;
	return cdr->billsec;
    }

    char *ast_cdr_get_disposition(struct ast_cdr *cdr) {
	if(!cdr) return NULL;
	return ast_cdr_disp2str(cdr->disposition);
    }

    char *ast_cdr_get_amaflags(struct ast_cdr *cdr) {
	if(!cdr) return NULL;
	return ast_cdr_flags2str(cdr->amaflags);
    }

    char *ast_cdr_get_uniqueid(struct ast_cdr *cdr) {
	if(!cdr) return NULL;
	return cdr->uniqueid;
    }
    
    char *ast_cdr_get_userfield(struct ast_cdr *cdr) {
	if(!cdr) return NULL;
	return cdr->userfield;
    }

#ifdef ASTERISK_CDR_HAS_CHANNEL
    struct ast_channel *ast_cdr_get_channelp(struct ast_cdr *cdr) {
	if(!cdr) return NULL;
	return cdr->channelp;
    }
#endif

%}
