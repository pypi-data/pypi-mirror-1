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

class CallDetailRecord:
    """
    class CallDetailRecord

    This is a wrapper class to represent a Call Detail Record
    so it can be easily accessed without resorting to the lower
    level api defined in the PyAsterisk C module.
    """
    def __init__(self, cdr):
        import asterisk

        for field in ["accountcode", "src", "dst", "dcontext", "clid",
                      "dstchannel", "lastapp", "lastdata", "disposition",
		      "channel",
                      "start", "answer", "finish", "duration", "billsec", 
                      "amaflags", "uniqueid", "userfield"]:
            func = getattr(asterisk, "ast_cdr_get_" + field)
            setattr(self, field, func(cdr))
        try:
	    from pyastre.channel import Channel
            self.channel = Channel(asterisk.ast_cdr_get_channelp(cdr))
	except AttributeError:
	    pass
