# blueberry - Yet another Python web framework.
#
#       http://code.google.com/p/blueberrypy
#
# Copyright 2009 David Reynolds
#
# Use and distribution licensed under the BSD license. See
# the LICENSE file for full text.

"""
Logging module similar to sqlalchemy.log.
"""

import logging
import sys

def instance_logger(instance):
    name = '%s.%s.%s' % (instance.__class__.__module__,
                         instance.__class__.__name__,
                         hex(id(instance)))

    logger = logging.getLogger(name)
    instance._should_log_info = logger.isEnabledFor(logging.INFO)
    instance._should_log_debug = logger.isEnabledFor(logging.DEBUG)
    return logger
