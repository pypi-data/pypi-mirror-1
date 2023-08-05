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

###
### Configuration Elements
###
dbconfig = {
    'database' : 'magicphone',
    'host' : 'localhost',
    'user': 'magicphone',
    'password' : 'changeme',
   }
debug = 5

###
### Initialization
###
from random import seed
from time import time
seed(time())

from twisted.internet import reactor
#reactor.suggestThreadPoolSize(self, 16)

from twisted.python import log
logfile = open("/var/log/softswitch.log", "a")
log.startLogging(logfile)

#from twisted.enterprise import adbapi
#dbpool = adbapi.ConnectionPool("pyPgSQL.PgSQL", **dbconfig)

#from magicphone.fabric import Switch
#switch = Switch(dbpool, debug)

from twisted.manhole import telnet
shellf = telnet.ShellFactory()
class Shell(telnet.Shell):
    def welcomeMessage(self):
        return """

        ************************
        * Telekommunisten !BUG *
        ************************

"""


shellf.protocol = Shell
shellf.username = "user"
shellf.password = "password"
manhole = reactor.listenTCP(5560, shellf, interface = "127.0.0.1")
manhole.interface = "127.0.0.1"

pdb = { ('f', 'k'): 'hello world' }

def cdr(c):
    """
    Handle a posted CDR
    """

def run():
    """
    Start the machinery going
    """
    from twisted.internet import reactor
    reactor.run()

def stop():
    """
    Shut the machinery down
    """
    from twisted.internet import reactor
    reactor.stop()
