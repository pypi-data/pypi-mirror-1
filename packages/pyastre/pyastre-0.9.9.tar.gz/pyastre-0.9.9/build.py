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

from distutils.core import Extension

###
### setup.py uses this list to build shared C extensions
### and modules
###
solibs = []

try:
    ###
    ### Try to determine if and how we should build the
    ### embedded python for Asterisk
    ###
    from os import stat
    stat('/usr/include/asterisk/pbx.h')

    ###
    ### Sometimes we need special linker flags to build
    ### an embedded module
    ###
    from distutils import sysconfig
    solink = sysconfig.get_config_var("LINKFORSHARED").split(' ')

    ###
    ### We have to link against libpython, this is how we
    ### calculate which libpython to use
    ###
    from sys import version_info
    pythonlib = 'python%d.%d' % version_info[:2]

    ###
    ### If all is well up till here, then make the extension object
    ### and save it so that it gets built
    ###
    ast_python = Extension("_pyastre",
                           ['_pyastre/pyastre.i', '_pyastre/asterisk.c'],
                           extra_compile_args = ['-Wall'],
                           extra_link_args = solink,
                           define_macros = [('SCRIPT_DIR', '"/etc/asterisk/site-python"')],
                           libraries = [pythonlib])
    solibs.append(ast_python)

except:
    print "Asterisk not found. Not building shared module."
