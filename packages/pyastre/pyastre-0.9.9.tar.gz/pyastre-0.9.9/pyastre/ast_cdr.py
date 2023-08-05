############################################################################
#    Copyright (C) 2004, 2005 by William Waites <ww@groovy.net>            #
#    Copyright (C) 2004, 2005 Consultants Ars Informatica S.A.R.F.         #
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

from pyastre.cdr import CallDetailRecord
from twisted.enterprise import row

class AsteriskCallDetailRecord(CallDetailRecord, row.RowObject):
    """
    class AsteriskCallDetailRecord

    This is an object that can be inserted via a reflector into 
    a table defined in the standard Asterisk way.
    """
    rowTableName = "cdr"
    rowColumns = [
      ("src", "varchar"),
      ("dst", "varchar"),
      ("clid", "varchar"),
      ("channel", "varchar"),
      ("dstchannel", "varchar"),
      ("dcontext", "varchar"),
      ("calldate", "varchar"),
      ("duration", "int"),
      ("billsec", "int"),
      ("lastdata", "varchar"),
      ("lastapp", "varchar"),
      ("disposition", "varchar"),
      ("amaflags", "varchar"),
      ("accountcode", "varchar"),
      ("userfield", "varchar"),
      ("uniqueid", "varchar"),
      ]
