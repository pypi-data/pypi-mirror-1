# blueberry - Yet another Python web framework.
#
#       http://code.google.com/p/blueberrypy
#
# Copyright 2009 David Reynolds
#
# Use and distribution licensed under the BSD license. See
# the LICENSE file for full text.

import urllib
import urlparse
from blueberry import request

def url_for(path, **kwargs):
    host = kwargs.pop('host', request.host)
    protocol = kwargs.pop('protocol', request.protocol)
    url = ''

    params = urllib.urlencode(kwargs)

    url += protocol + '://'
    url += host

    url = urlparse.urljoin(url, path)
    if params:
        url += '?%s' % params

    return url
