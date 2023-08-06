# blueberry - Yet another Python web framework.
#
#       http://code.google.com/p/blueberrypy
#
# Copyright 2009 David Reynolds
#
# Use and distribution licensed under the BSD license. See
# the LICENSE file for full text.

from configuration import config
from utils import ObjectProxy

__all__ = ['request', 'response', 'simple_cache']

request = ObjectProxy('request')
response = ObjectProxy('response')
simple_cache = {}
