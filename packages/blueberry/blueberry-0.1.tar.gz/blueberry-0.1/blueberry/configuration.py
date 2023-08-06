# blueberry - Yet another Python web framework.
#
#       http://code.google.com/p/blueberrypy
#
# Copyright 2009 David Reynolds
#
# Use and distribution licensed under the BSD license. See
# the LICENSE file for full text.

from ConfigParser import RawConfigParser
import logging.config
import logging

class _Parser(RawConfigParser):

    def as_dict(self):
        result = {}
        sections = self.sections()
        for section in sections:
            items = self.items(section)
            result[section] = dict(items)

        return result

    def dict_from_file(self, filename):
        self.read(filename)
        return self.as_dict()

class BlueBerryConfig(dict):

    defaults = {
        'blueberry.paths': {
            'root': None,
            'static_files': None,
            'templates': []
        },
        'blueberry.h': None,
        'server': {
            'host': '0.0.0.0',
            'port': 3000,
            'name': 'Blueberry'
        }
    }

    def __init__(self):
        self.reset()

    def reset(self):
        self.clear()
        dict.update(self, self.defaults)

    def update(self, config):
        filename = None
        if isinstance(config, basestring):
            filename = config
            config = _Parser().dict_from_file(config)
        elif isinstance(config, dict):
            config = config.copy()

        dict.update(self, config)

        if filename and config.has_key('loggers'):
            logging.config.fileConfig(filename)

config = BlueBerryConfig()
