#!/usr/bin/python2.4
import pkg_resources
pkg_resources.require("TurboGears")

from os.path import *
import os
import sys


def start():
    from turbogears import update_config, start_server
    import cherrypy
    cherrypy.lowercase_api = True

    # first look on the command line for a desired config file,
    # if it's not on the command line, then
    # look for setup.py in the current working directory. If it's not there,
    #  this script is probably installed
    if len(sys.argv) > 1:
        update_config(configfile=sys.argv[1],
                      modulename="fosswallproxy.config")
    elif exists(join(os.getcwd(), "setup.py")):
        update_config(configfile="dev.cfg",modulename="fosswallproxy.config")
    else:
        update_config(configfile="prod.cfg",modulename="fosswallproxy.config")

    from fosswallproxy.controllers import Root

    start_server(Root())

