import cherrypy

import widgets

import logging

from controllers import ConfigServer

from turbogears import config

from model import create_models

log = logging.getLogger("config_admin")

mounted = False

def start_extension():
    global mounted
    if not config.get("config_server.on", False):
        return
    if hasattr(cherrypy.root, 'config_admin'):
        raise 'The path /conf_admin'
    create_models()
    cherrypy.root.config_admin = ConfigServer()
    mounted = True

def stop_extension():
    global mounted
    if not config.get("config_server.on", False):
        return
    if mounted:
        delattr(cherrypy.root, 'config_admin')

