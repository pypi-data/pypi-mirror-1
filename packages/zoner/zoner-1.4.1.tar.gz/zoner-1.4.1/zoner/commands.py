# -*- coding: utf-8 -*-
"""This module contains functions called from console script entry points."""

import getopt
import os
import sys

from os.path import dirname, exists, join

import pkg_resources

import turbogears
import cherrypy

from zoner.user_manage import user_add, user_delete

cherrypy.lowercase_api = True

class ConfigurationError(Exception):
    pass

def start():
    """Start the CherryPy application server."""
    
    pkg_resources.require("TurboGears >= 1.0.4")
    pkg_resources.require("SQLAlchemy >= 0.3.10")
    pkg_resources.require("easyzone >= 1.2.0")
    pkg_resources.require("TGBooleanFormWidget")
    pkg_resources.require("TGExpandingFormWidget")
    
    setupdir = dirname(dirname(__file__))
    curdir = os.getcwd()
    
    # First look on the command line for a desired config file,
    # if it's not on the command line, then look for 'setup.py'
    # in the current directory. If there, load configuration
    # from a file called 'dev.cfg'. If it's not there, the project
    # is probably installed and we'll look first for a file called
    # 'prod.cfg' in the current directory and then for a default
    # config file called 'default.cfg' packaged in the egg.
    if len(sys.argv) > 1:
        configfile = sys.argv[1]
    elif exists(join(setupdir, "setup.py")):
        configfile = join(setupdir, "dev.cfg")
    elif exists(join(curdir, "prod.cfg")):
        configfile = join(curdir, "prod.cfg")
    else:
        try:
            configfile = pkg_resources.resource_filename(
              pkg_resources.Requirement.parse("zoner"),
                "config/default.cfg")
        except pkg_resources.DistributionNotFound:
            raise ConfigurationError("Could not find default configuration.")

    turbogears.update_config(configfile=configfile,
        modulename="zoner.config")
    
    # Replace tg_flash with my preferred implementation
    from zoner.better_flash import flash, _get_flash
    from turbogears import controllers
    controllers.flash = flash
    controllers._get_flash = _get_flash
    
    from zoner.controllers import Root

    turbogears.start_server(Root())


# ---- zoner_users command handler ----

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
    


help_message = '''
The help message goes here.
'''


def error(msg=''):
    if msg:
        print >> sys.stderr, "error: %s" % msg
    print >> sys.stderr, sys.argv[0] + " -c file.cfg [options] command"
    print >> sys.stderr, "\t Commands are:"
    print >> sys.stderr, "\t\t add <username> <email> <displayname> <password>"
    print >> sys.stderr, "\t\t delete <username>"
    print >> sys.stderr, "\t for help use --help"
    sys.exit(2)


def user_manage(argv=None):
    config = None
    
    if argv is None:
        argv = sys.argv
    
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hc:v", ["help", "config="])
        except getopt.error, msg:
            raise Usage(msg)
        
        # option processing
        for option, value in opts:
            if option == "-v":
                verbose = True
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option in ("-c", "--config"):
                config = value
    
    except Usage, err:
        error(str(err.msg))
    
    if len(args) < 1:
        error()
    
    if config:
        turbogears.update_config(configfile=config, modulename="zoner.config")
    else:
        error('No config file specified (eg: "-c dev.cfg")')
    
    command = args[0]
    
    if command == 'add':
        user_add(*args[1:])
    
    elif command == 'delete':
        user_delete(*args[1:])
    
    else:
        error("Unknown command '%s'" % command)

