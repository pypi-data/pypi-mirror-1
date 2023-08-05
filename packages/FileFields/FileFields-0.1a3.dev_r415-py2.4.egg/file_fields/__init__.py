import cherrypy

import widgets

import logging

from controllers import FileServer, PicServer

from turbogears import config

__all__ = []

log = logging.getLogger("file_fields")

def start_extension():
    if not config.get("file_field_server.on", False):
        return
    if hasattr(cherrypy.root, 'pic_server'):
        raise 'The path /pic_viewer is already taken'
    cherrypy.root.pic_server = PicServer()
    cherrypy.root.file_server = FileServer()

def stop_extension():
    if not config.get("file_field_server.on", False):
        return
    if upc_server is None:
        return
    delattr(cherrypy.root, 'pic_server')
    delattr(cherrypy.root, 'file_server')
