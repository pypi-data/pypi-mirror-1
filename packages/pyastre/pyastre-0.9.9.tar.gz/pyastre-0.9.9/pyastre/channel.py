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

from pyastre.utils import AsteriskFunction

class Channel:
    """
    @class Channel

    This is a wrapper class to represent an Asterisk
    channel. Channel variables are in particular supported
    via dictionary-like syntax. This is so you don't have
    to use the lower level get/set routines.
    """
    def __init__(self, chan, debug = False):
        from asterisk import ast_channel_get_name
        self.__channel__ = chan
        self.name = ast_channel_get_name(chan)
        self.verbose = debug
	self.clid = AsteriskFunction(self, 'CALLERID')

    def __getitem__(self, item):
        from asterisk import pbx_builtin_getvar_helper
        return pbx_builtin_getvar_helper(self.__channel__, str(item))

    def __setitem__(self, item, value):
        from asterisk import pbx_builtin_setvar_helper
        pbx_builtin_setvar_helper(self.__channel__, str(item), str(value))

    def __call__(self, appname, *args):
    	return self.pbx_exec(appname, *args)

    def authenticated(self):
        return True
    
    def pbx_exec(self, appname, *args):
	from pyastre.utils import verbose
        from asterisk import pbx_findapp, ast_exec
        app = pbx_findapp(appname)
        if not app:
            raise "No %s" % (appname, )
        if self.verbose: verbose("   >> %s(%s)" % (appname,  ', '.join((self.name,) + args)))
        return ast_exec(self.__channel__, app, '|'.join(args), 1)

    def hangup(self):
        return self.pbx_exec('Hangup')

    def congestion(self):
        return self.pbx_exec('Congestion')

    def dial(self, route, dest, dialargs):
        from pyastre.utils import astRoute
        dialstr = astRoute(route, dest, dialargs)
        status = self.pbx_exec('Dial', dialstr)
        return status

    def setAccount(self, value):
        return self.pbx_exec('SetAccount', value)
    
    def setCdrUserField(self, value):
        return self.pbx_exec('SetCDRUserField', "%s" % value)

    def setPolicy(self, policy):
        self.setAccount(policy.account)
        return policy
    
    def goto(self, *args):
        return self.pbx_exec('Goto', *map(str, args))

