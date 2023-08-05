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

from twisted.internet import reactor
from twisted.web import xmlrpc

class PyastreXMLRPC(xmlrpc.XMLRPC):
    """
    The Pyastre XMLRPC interface.

    Supported functions:

    doc("function")
    originate("source", "dest")
    """
    cidname = "Auto Call"
    def xmlrpc_doc(self, what = None):
        """
        doc("function")

        Show the documentation for the given function
        """
        
        if not what:
            return self.__doc__
        if hasattr(self, "xmlrpc_" + what):
            return getattr(self, "xmlrpc_" + what).__doc__ or ""
        
    def xmlrpc_originate(self, source, dest):
        """
        originate("source", "dest")
        
        Originate both legs of a call from source to dest.
        source must be a number in the anon context, i.e.
        chargeable to us. That phone will ring, and the call
        will be billed to that number.
        """
        from pyastre import asterisk
        reactor.callInThread(asterisk.ast_originate,
                             "%s@anon" % source,
                             "E.164", dest, 1,
                             source, self.cidname,
                             source, "", 120000)
        return 0
                   
                      
