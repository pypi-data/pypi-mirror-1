# -*- coding: UTF-8 -*-
"""Standard TurboGears request filters for handling dynamic application roots
and nested form variables."""

__all__ = [
    'NestedVariablesFilter',
    'VirtualPathFilter',
]

import logging

from cherrypy import NotFound, request
from formencode.variabledecode import NestedVariables


log = logging.getLogger('turbogears.filters')


class VirtualPathFilter(object):
    """Filter that makes CherryPy ignorant of a URL root path.

    That is, you can mount your app so the URI "/users/~rdel/myapp/" maps to
    the root object "/".

    """
    def __init__(self, webpath=''):
        webpath = webpath.rstrip('/')
        if webpath and not webpath.startswith('/'):
             webpath = '/' + webpath
        self.webpath = webpath

    def before_request_body(self):
        """Determine the relevant path info by stripping of prefixes.

        Strips webpath and SCRIPT_NAME from request.object_path and
        sets request.path_info (since CherryPy 2 does not set it).

        """
        webpath = self.webpath
        try:
            webpath += request.wsgi_environ['SCRIPT_NAME'].rstrip('/')
        except (AttributeError, KeyError):
            pass
        if webpath:
            if request.object_path.startswith(webpath):
                request.object_path = request.object_path[len(webpath):] or '/'
            if request.path.startswith(webpath):
                request.path_info = request.path[len(webpath):] or '/'
            else:
                request.path_info = request.path
                # check for webpath only if not forwarded
                try:
                    if not request.wsgi_environ['HTTP_X_FORWARDED_SERVER']:
                        raise KeyError
                except (AttributeError, KeyError):
                    raise NotFound(request.path)
        else:
            request.path_info = request.path


class NestedVariablesFilter(object):
    """Request filter that turns request params with names in special dotted
    notation into nested dictionaries via FormEncode's NestedVariables
    validator.

    """
    def before_main(self):
        if hasattr(request, 'params'):
            request.params = NestedVariables.to_python(request.params or {})
