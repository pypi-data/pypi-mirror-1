# -*- coding: UTF-8 -*-
"""TurboFeed utility functions."""
__docformat__ = 'restructuredtext'

__all__ = [
    'absolute_url',
    'xml_stylesheet',
]

import cherrypy
import turbogears

from kid import ProcessingInstruction

def absolute_url(suffix='', params=None, **kw):
    """Returns the absolute URL to this server, appending 'suffix' if given."""

    aurl = 'http://%s/' % cherrypy.request.headers['Host']
    if suffix:
        aurl += turbogears.url(suffix, params, **kw).lstrip('/')
    return aurl

def xml_stylesheet(href, type='text/css'):
    """Returns an xml-stylesheet processing instruction element for given URL.

    ``href`` can be a string with the URL to the stylesheet or a dict with
    members ``href`` and ``type`` (see below) or a callable returning either.

    ``type`` specifies the value of the "type" atribute of the PI.
    The default type is 'text/css'.
    """

    if callable(href):
        href = href()
    if isinstance(href, dict):
        href = href['href']
        type = href.get('type', type)
    return ProcessingInstruction('xml-stylesheet'
        ' type="%s" href="%s"' % (type, href))

