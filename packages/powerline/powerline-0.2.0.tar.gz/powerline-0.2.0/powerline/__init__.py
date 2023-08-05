# powerline - Simple, easy, computer reservations system
# (c) 2008 Pianohacker, licensed under the GPLv3

from __future__ import absolute_import

import cherrypy
from powerline import output, database, json
from os import path

location = path.abspath(path.dirname(__file__))
output.template_dir = path.join(location, 'templates')

from powerline import manager, xmlrpc

cherrypy.config.namespaces.update(database = lambda k, v: setattr(database, k, v), output = lambda k, v: setattr(output, k, v))


__all__ = ['location', 'output', 'database', 'json', 'manager', 'xmlrpc']
