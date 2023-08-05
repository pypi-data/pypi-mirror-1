############################################################################
#    Copyright (C) 2004, 2005, 2006 by William Waites <ww@haagenti.com>    #
#    Copyright (C) 2004, 2005, 2006 Consultants Ars Informatica S.A.R.F.   #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU Library General Public License as       #
#    published by the Free Software Foundation; either version 2 of the    #
#    License, or (at your option) any later version.                       #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU Library General Public     #
#    License along with this program; if not, write to the                 #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################


from pyastre import ast_db_getitem, ast_db_setitem

class AsteriskDatabase(dict):
    def __getitem__(self, key):
        try: f,k = key
        except IndexError:
            raise KeyError, key
        return ast_db_getitem(f, k)
    
    def __setitem__(self, key, value):
        try: f,k = key
        except IndexError:
            raise KeyError, key
        return ast_db_setitem(f, k, value)
