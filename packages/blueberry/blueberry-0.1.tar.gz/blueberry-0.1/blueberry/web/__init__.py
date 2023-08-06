# blueberry - Yet another Python web framework.
#
#       http://code.google.com/p/blueberrypy
#
# Copyright 2009 David Reynolds
#
# Use and distribution licensed under the BSD license. See
# the LICENSE file for full text.

import re
import logging
import traceback
from Cookie import BaseCookie
from wsgiref.headers import Headers
import datetime
import time
import cgi
import sys
import base64
import binascii
import hmac
import urlparse

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from hashlib import sha1
except ImportError:
    import sha as sha1

import webob
import webob.exc

import blueberry
from blueberry import log, config

RE_FIND_GROUPS = re.compile('\(.*?\)')

def _utf8(s):
    if isinstance(s, unicode):
        return s.encode('utf-8')
    assert isinstance(s, str)
    return s

class Request(webob.Request):

    def signed_cookie(self, name, secret=None):
        if not secret:
            secret = config['app'].get('secret', 'secret')
        cookie = self.str_cookies.get(name)
        if not cookie:
            return

        try:
            sig, pickled = cookie[:40], base64.decodestring(cookie[40:])
        except binascii.Error:
            return
        if hmac.new(secret, pickled, sha1).hexdigest() == sig:
            return pickle.loads(pickled)

    def _protocol(self):
        p = self.environ.get('HTTP_X_FORWARDED_PROTO')
        if p:
            return p

        p = self.environ.get('HTTP_X_FORWARDED_SSL')
        if p:
            return p

        return self.scheme
    protocol = property(_protocol)

    def _subdomain(self):
        # very bad...
        domain_match = config['app'].get('domain', '')
        host = self.environ['HTTP_HOST'].split(':')[0]
        match = re.compile('^(.+?)\.%s$' % domain_match)
        subdomain = re.sub(match, r'\1', host)
        return subdomain
    subdomain = property(_subdomain)

# from webob
def _serialize_cookie_date(dt):
    if dt is None:
        return None
    if isinstance(dt, unicode):
        dt = dt.encode('ascii')
    if isinstance(dt, datetime.timedelta):
        dt = datetime.datetime.now() + dt
    if isinstance(dt, (datetime.datetime, datetime.date)):
        dt = dt.timetuple()
    return time.strftime('%a, %d-%b-%Y %H:%M:%S GMT', dt)

class Response(object):

    def __init__(self):
        self._wsgi_headers = []
        self.headers = Headers(self._wsgi_headers)

        self.charset = 'utf-8'
        self.content_type = 'text/html'

        self.headers['Content-Type'] = '; '.join([self.content_type, self.charset])
        self.headers['Cache-Control'] = 'no-cache'
        self.headers['Pragma'] = 'no-cache'

        self.out = StringIO()
        self.set_status(200)

    def set_cookie(self, key, value='', max_age=None,
                   path='/', domain=None, secure=None, httponly=False,
                   version=None, comment=None, expires=None):
        if isinstance(value, unicode):
            value = value.encode(self.charset)
        value = value.replace('\n', '')

        cookies = BaseCookie()
        cookies[key] = value

        if isinstance(max_age, datetime.timedelta):
            max_age = max_age.seconds + max_age.days * 24 * 60 * 60
        if max_age is not None and expires is None:
            expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age)
        if isinstance(expires, datetime.timedelta):
            expires = datetime.datetime.utcnow() + expires
        if isinstance(expires, datetime.datetime):
            expires = _serialize_cookie_date(expires)

        for k, v in [('max_age', max_age),
                     ('path', path),
                     ('domain', domain),
                     ('secure', secure),
                     ('HttpOnly', httponly),
                     ('version', version),
                     ('comment', comment),
                     ('expires', expires)]:
            if v is not None and v is not False:
                cookies[key][k.replace('_', '-')] = str(v)
        self._wsgi_headers.append(('Set-Cookie', cookies[key].OutputString(None)))

    def delete_cookie(self, key, path='/', domain=None):
        self.set_cookie(key, '', path=path, domain=domain,
                        max_age=0, expires=datetime.timedelta(days=-5))

    def unset_cookie(self, key):
        existing = self.headers.get_all('Set-Cookie')
        if not existing:
            raise KeyError('No cookies have been set')

        del self.headers['Set-Cookie']
        found = False

        for header in existing:
            cookies = BaseCookie()
            cookies.load(header)
            if key in cookies:
                found = True
                del cookies[key]
                header = cookies.output(header='').lstrip()
            if header:
                if header.endswith(';'):
                    header = header[:-1]
                self.headers.add_header('Set-Cookie', header)

        if not found:
            raise KeyError('No cookie has been set with the name %r' % key)

    def signed_cookie(self, name, data, secret=None, **kwargs):
        if not secret:
            secret = config['app'].get('secret', 'secret')
        pickled = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        sig = hmac.new(secret, pickled, sha1).hexdigest()
        self.set_cookie(name, sig + base64.encodestring(pickled), **kwargs)

    def clear(self):
        self.out.seek(0)
        self.out.truncate(0)

    def set_status(self, code, msg=None):
        if not msg:
            msg = Response.http_status_message(code)
        self._status = (code, msg)

    @staticmethod
    def http_status_message(code):
        if not Response._HTTP_STATUS_MESSAGES.has_key(code):
            raise Exception('Invalid HTTP status code: %d' % code)
        return Response._HTTP_STATUS_MESSAGES[code]

    _HTTP_STATUS_MESSAGES = {
        100: 'Continue',
        101: 'Switching Protocols',
        200: 'OK',
        201: 'Created',
        202: 'Accepted',
        203: 'Non-Authoritative Information',
        204: 'No Content',
        205: 'Reset Content',
        206: 'Partial Content',
        300: 'Multiple Choices',
        301: 'Moved Permanently',
        302: 'Found',
        303: 'See Other',
        304: 'Not Modified',
        305: 'Use Proxy',
        306: 'Unused',
        307: 'Temporary Redirect',
        400: 'Bad Request',
        401: 'Unauthorized',
        402: 'Payment Required',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        406: 'Not Acceptable',
        407: 'Proxy Authentication Required',
        408: 'Request Time-out',
        409: 'Conflict',
        410: 'Gone',
        411: 'Length Required',
        412: 'Precondition Failed',
        413: 'Request Entity Too Large',
        414: 'Request-URI Too Large',
        415: 'Unsupported Media Type',
        416: 'Request Range Not Satisfiable',
        417: 'Expectation Failed',
        500: 'Internal Server Error',
        501: 'Not Implemented',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        504: 'Gateway Time-out',
        505: 'HTTP Version not supported'
    }

    def __call__(self, environ, start_response):
        body = self.out.getvalue()
        self.out.close()

        if isinstance(body, unicode):
            body = body.encode('utf-8')
        elif self.headers.get('Content-Type', '').endswith('charset=utf-8'):
            try:
                body.decode('utf-8')
            except UnicodeError, e:
                logging.warning('Response written is not utf-8: %s', e)

        self.headers['Content-Length'] = str(len(body))
        write = start_response('%d %s' % self._status, self._wsgi_headers)
        write(body)
        return ['']

def http_error(status):
    status = '%d %s' % status

    blueberry.response.out.write("""
    <html>
        <head>
            <title>%s</title>
        </head>
        <body>
            <h1>%s</h1>
        </body>
    </html>
    """ % (status, status))

class RequestHandler(object):

    def __init__(self):
        pass

    def get(self, *args):
        self.error(405)

    def post(self, *args):
        self.error(405)

    @property
    def cookies(self):
        if not hasattr(self, '_cookies'):
            self._cookies = BaseCookie()
            if 'Cookie' in blueberry.request.headers:
                try:
                    self._cookies.load(blueberry.request.headers['Cookie'])
                except:
                    self.clear_all_cookies()
        return self._cookies

    def clear_cookie(self, name):
        blueberry.request.delete_cookie(name)

    def clear_all_cookies(self):
        for name in self.cookies.iterkeys():
            self.clear_cookie(name)

    def error(self, code):
        blueberry.response.set_status(code)
        blueberry.response.clear()
        http_error(blueberry.response._status)

    def handle_exception(self, exception, debug):
        self.error(500)
        logging.exception(exception)
        if debug:
            lines = ''.join(traceback.format_exception(*sys.exc_info()))
            blueberry.response.clear()
            blueberry.response.out.write('<pre>%s</pre>' % (cgi.escape(lines, quote=True)))

    def redirect(self, url, code=302):
        blueberry.response.set_status(code)
        abs_url = urlparse.urljoin(blueberry.request.url, url)
        blueberry.response.headers['Location'] = str(abs_url)
        blueberry.response.clear()

    def abort(self, code=None, detail='', headers=None, comment=None):
        blueberry.response.set_status(code)
        blueberry.response.clear()
        http_error(blueberry.response._status)

class WSGIApplication(object):

    def __init__(self, url_mapping, debug=False, ignore_subdomains=None):
        self._init_url_mappings(url_mapping)
        self.debug = debug
        self.ignore_subdomains = ignore_subdomains or []
        self.current_request_args = ()

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = Response()

        # set the thread-local request/response objects
        blueberry.request.set(request)
        blueberry.response.set(response)

        handler = None
        groups = ()

# for subdomains... kind of buggy for apps without them, so I'm disabling right now
#        subdomain = request.subdomain
#        if subdomain and subdomain not in self.ignore_subdomains:
#            mapping = self._url_mapping_with_subdomains
#        else:
#            mapping = self._url_mapping_without_subdomains

        mapping = self._url_mapping

        for regexp, handler_class, kw in mapping:
            match = regexp.match(request.path)
            if match:
                handler = handler_class()
                groups = match.groups()
                break

        self.current_request_args = groups

        result = None

        if handler:
            try:
                method = environ['REQUEST_METHOD']
                if method == 'GET':
                    result = handler.get(*groups)
                elif method == 'POST':
                    result = handler.post(*groups)
                else:
                    handler.error(501)
            except Exception, e:
                handler.handle_exception(e, self.debug)
        else:
            response.set_status(404)
            http_error(response._status)

        response.out.write(result or '')

        return response(environ, start_response)

    def _init_url_mappings(self, handler_tuples):
        handler_map = {}
        pattern_map = {}
        url_mapping = []

        for tup in handler_tuples:
            regexp = tup[0]
            handler = tup[1]
            kwargs = {}
            if len(tup) > 2:
                kwargs = tup[2]

            handler_map[handler.__name__] = handler

            if not regexp.startswith('^'):
                regexp = '^'+regexp
            if not regexp.endswith('$'):
                regexp += '$'

            compiled = re.compile(regexp)
            url_mapping.append((compiled, handler, kwargs))

            num_groups = len(RE_FIND_GROUPS.findall(regexp))
            handler_patterns = pattern_map.setdefault(handler, [])
            handler_patterns.append((compiled, num_groups))

        self._handler_map = handler_map
        self._pattern_map = pattern_map
        self._url_mapping = url_mapping

        # for subdomains
        #self._url_mapping_with_subdomains = filter(lambda x: x[2].has_key('subdomain'), self._url_mapping)
        #self._url_mapping_without_subdomains = filter(lambda x: not x[2].has_key('subdomain'), self._url_mapping)
