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

def verbose(s):
    """
    For some unknown reason, the ast_verbose function
    does not append a carriage return.
    """
    try:
        from asterisk import ast_verbose
        return ast_verbose(s + '\n')
    except ImportError:
        print s

def astRoute(route, dest, dialargs = None):
        """
        Upon being called, this class and its decendents return a string
        suitable for passing to the Dial application in Asterisk. Dialargs
        are optionally appended.
        """
        if route.proto == 'h323':
            dialstr = 'OH323/' + route.prefix + dest[route.strip:] + '@' + route.name
        else:
            from string import upper
            dialstr = upper(route.proto) + '/' + route.name + '/' + route.prefix + dest[route.strip:]
        if dialargs:
            dialstr = dialstr + '|' + dialargs
        return dialstr
       
class AsteriskFunction:
    def __init__(self, chan, func):
        self.chan = chan.__channel__
        self.func = func
    def __getitem__(self, key):
        from asterisk import ast_func_readp
        inval = "%s(%s)" % (self.func, key)
        return ast_func_readp(self.chan, inval)
    def __setitem__(self, key, value):
        from asterisk import ast_func_write
        inval = "%s(%s)" % (self.func, key)
        ast_func_write(self.chan, inval, value)
