# blueberry - Yet another Python web framework.
#
#       http://code.google.com/p/blueberrypy
#
# Copyright 2009 David Reynolds
#
# Use and distribution licensed under the BSD license. See
# the LICENSE file for full text.

from decorator import decorator
import formencode
from formencode import Invalid

from blueberry import request
from blueberry.utils.routing import url_for

def https(meth):
    def wrapper(self, *args, **kwargs):
        # replacement for request.scheme
        # that works with proxy headers
        proto = request.protocol
        if proto == 'https':
            return meth(self, *args, **kwargs)

        if request.method.lower() == 'post':
            # don't allow posts
            self.abort(405)

        self.redirect(url_for(request.path_info, protocol='https'))

    return wrapper

def validate(schema=None, form=None, error_handler=None, post_only=True):
    def wrapper(func, self, *args, **kwargs):
        if not valid(self,
                     schema=schema,
                     form=form,
                     post_only=post_only):
            if error_handler:
                f = getattr(self, error_handler)
                return f(*args, **kwargs)

        return func(self, *args, **kwargs)

    return decorator(wrapper)

def valid(action, schema=None, form=None, post_only=True):
    if post_only:
        params = request.POST.copy()
    else:
        params = request.params.copy()

    errors = {}
    values = {}

    if form:
        try:
            action.defaults = form.validate(params)
        except Invalid, e:
            errors = e.error_dict or e
            values = e.value

    if schema:
        try:
            action.defaults = schema.to_python(params)
        except Invalid, e:
            if errors:
                errors.update(e.error_dict or e)
            else:
                errors = e.error_dict or e

            if values:
                values.update(e.value)
            else:
                values = e.value

    if errors:
        action.defaults = values
        action.errors = errors

    return errors == {}
