/*************************************************************************
 *                                                                       *
 * pyastre.h -- SWIG Interface definition for                            *
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

#ifndef PYASTRE_H
#define PYASTRE_H

#define SOFTSWITCH_MODULE "softswitch"
#define PYASTRE_NAME "pyastre"
#define PYASTRE_VERSION "0.9.9"
#define PYASTRE_COPYRIGHT ">>>\tCopyright (c) 2004, 2005, 2006 Consultants Ars Informatica S.A.R.F.\n>>>\tCopyright (c) 2006 Haagenti Group Telekommunisten\n>>>\n>>>\tThis program is distributed in the hope that it will be useful\n>>>\tbut WITHOUT ANY WARRANTY without even the implied warranty of\n>>>\tMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the\n>>>\tGNU General Public License (Version 2) for more details"

PyObject *Pyastre_BuildCdrObj(struct ast_cdr *);
PyObject *Pyastre_BuildChannelObj(struct ast_channel *);

#endif /* PYASTRE_H */
