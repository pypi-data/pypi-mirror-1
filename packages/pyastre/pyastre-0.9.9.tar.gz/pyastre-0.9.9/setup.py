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

build_config = {
    'asterisk_include': '/usr/include/asterisk',
    'asterisk_modules': '/usr/lib/asterisk/modules',
}

from build import solibs
pkg_config = {
    'name': 'pyastre',
    'version': '0.9.9',
    'author': 'William Waites',
    'author_email': 'ww@styx.org',
    'url': 'http://www.telekommunisten.net/',
    'description': 'A Python in the Dialplan',
    'long_description': """
    This is an implementation of a Python interpreter embedded into a
    module for the Asterisk PBX, as well as some supporting Python classes
    for using it.

    This software is OBSOLETE.
    """,
    'license': 'LGPL',
    'packages': ["pyastre"],
    'platforms': ['all'],
    'ext_modules': solibs
    }

if __name__ == '__main__':
    from distutils.core import setup
    setup(**pkg_config)

    
