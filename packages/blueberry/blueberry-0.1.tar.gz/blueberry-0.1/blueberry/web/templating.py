# blueberry - Yet another Python web framework.
#
#       http://code.google.com/p/blueberrypy
#
# Copyright 2009 David Reynolds
#
# Use and distribution licensed under the BSD license. See
# the LICENSE file for full text.

import blueberry

def mako_template(template_name):
    template = blueberry.config['template_lookup'].get_template(template_name)
    return template

def render_mako(template_name, **kwargs):
    template = mako_template(template_name)
    kwargs.update(dict(request=blueberry.request))

    return template.render(**kwargs)
