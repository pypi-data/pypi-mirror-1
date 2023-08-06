# blueberry - Yet another Python web framework.
#
#       http://code.google.com/p/blueberrypy
#
# Copyright 2009 David Reynolds
#
# Use and distribution licensed under the BSD license. See
# the LICENSE file for full text.

import uuid
import random
from string import letters, digits
import threading

def generate_uuid():
    return str(uuid.uuid4()).replace('-', '')

def generate_short_key(n=8):
    random.seed()
    return ''.join(random.sample(letters+digits, n))

# taken from paste.deploy.converters
def asbool(obj):
    if isinstance(obj, (str, unicode)):
        obj = obj.strip().lower()
        if obj in ['true', 'yes', 'on', 'y', 't', '1']:
            return True
        if obj in ['false', 'no', 'off', 'n', 'f', '0']:
            return False
        else:
            raise ValueError(
                "String is not true/false: %r" % obj)
    return bool(obj)

def asint(obj):
    try:
        return int(obj)
    except (TypeError, ValueError), e:
        raise ValueError(
            "Bad integer value: %r" % obj)

def aslist(obj, sep=None, strip=True):
    if isinstance(obj, (str, unicode)):
        lst = obj.split(sep)
        if strip:
            lst = [v.strip() for v in lst]
        return lst
    elif isinstance(obj, (list, tuple)):
        return obj
    elif obj is None:
        return []
    else:
        return [obj]

class AttribSafeContextObj(object):

    def __getattr__(self, name):
        try:
            return object.__getattr__(self, name)
        except AttributeError:
            return ''

class ObjectProxy(object):

    def __init__(self, name):
        self.__dict__['__name__'] = name
        self.__dict__['__local__'] = threading.local()

    def __getattr__(self, name):
        return getattr(self._obj(), name)

    def __setattr__(self, name, value):
        setattr(self._obj(), name, value)

    def __delattr__(self, name):
        delattr(self._obj(), name)

    def _obj(self):
        try:
            return getattr(self.__local__, self.__name__)
        except AttributeError:
            raise AttributeError("No object (name: %s) has been registered "
                                 "for this thread." % self.__name__)

    def set(self, obj):
        setattr(self.__local__, self.__name__, obj)
