##
## An example pyastre macro that you can put in your site-python
## directory.
## 
## You run it from the dialplan like this:
##
## exten => s,1,Python(setvar,foo=bar)
##
from pyastre.channel import Channel
from twisted.python.log import debug, err

def execute(c, args):
    sp = args.split('=',1)
    try:
	key, value = sp
    except IndexError:
        err("Argument Parse Error: '%s' should be 'foo=bar'" % (args,))
	return

    debug("setvar: setting chan[%s] = %s" % (key, value))

    chan = Channel(c)
    chan[key] = value
