#!/usr/bin/python
import pkg_resources
pkg_resources.require("TurboGears")

import cherrypy
import turbogears
from os.path import *
import sys

# first look on the command line for a desired config file,
# if it's not on the command line, then
# look for setup.py in this directory. If it's not there, this script is
# probably installed
if len(sys.argv) > 1:
    turbogears.update_config(configfile=sys.argv[1], 
        modulename="spider.config")
elif exists(join(dirname(__file__), "setup.py")):
    turbogears.update_config(configfile="dev.cfg",
        modulename="spider.config")
else:
    turbogears.update_config(configfile="prod.cfg",
        modulename="spider.config.app")

from spider.controllers import Root

cherrypy.root = Root()
cherrypy.server.start()

