# -*- coding: utf-8 -*-
"""
    Object Based Dispatching
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Colubrid inspired object based dispatching.

    :copyright: Copyright 2008 by Armin Ronacher.
    :license: GNU GPL.
"""
import inspect
from werkzeug import Request, Response, responder, redirect
from werkzeug.exceptions import HTTPException, NotFound


def fix_slash(request, is_container):
    path = request.path
    new_path = None
    ends_with_slash = path.endswith('/')
    if ends_with_slash and not is_container:
        new_path = path.rstrip('/')
    elif not ends_with_slash and is_container:
        new_path = path + '/'
    if new_path is not None:
        qs = request.environ.get('QUERY_STRING')
        if qs:
            new_path += '?' + qs
        return redirect(new_path)


class Controller(object):

    def __init__(self, request):
        self.request = request


class ObjectApplication(object):

    root = None

    def dispatch_request(self, request):
        handler = self.root
        container = None
        args = []
        for part in request.path.strip('/').split('/'):
            if part.startswith('_'):
                raise NotFound()
            node = getattr(handler, part, None)
            if node is None:
                if part:
                    args.append(part)
            else:
                handler = node

        if inspect.ismethod(handler):
            if handler.__name__ == 'index':
                container = False
        else:
            index = getattr(handler, 'index', None)
            if index is not None:
                if not hasattr(index, '_is_container'):
                    container = True
                handler = index
            else:
                raise NotFound()

        if container is None and hasattr(handler, '_is_container'):
            container = handler._is_container

        handler_args, varargs, _, defaults = inspect.getargspec(handler)
        if defaults is None:
            defaults = 0
        else:
            defaults = len(defaults)

        max_len = len(handler_args) - 1
        min_len = max_len - defaults
        cur_len = len(args)
        if varargs:
            max_len = -1

        # check if the number of arguments fits our handler
        if max_len < 0:
            if cur_len < min_len:
                raise NotFound()
        elif min_len <= cur_len <= max_len:
            if container is None:
                container = cur_len < max_len
        else:
            raise NotFound()

        # redirect if necessary
        response = fix_slash(request, container)
        if response is not None:
            return response

        # call handler
        return handler(handler.im_class(request), *args)

    @responder
    def __call__(self, environ, start_response):
        request = Request(environ)
        try:
            rv = self.dispatch_request(request)
            if isinstance(rv, basestring):
                rv = Response(rv, mimetype='text/html')
            return rv
        except HTTPException, e:
            return e


class BlogController(Controller):

    def index(self):
        return 'Hello World'


class AdminController(Controller):

    def hello(self, name='World'):
        times = self.request.args['times']
        return 'Hello %s (%s times)!' % (name, times)


application = ObjectApplication()
application.root = BlogController
application.root.admin = AdminController


if __name__ == '__main__':
    from werkzeug import run_simple
    run_simple('localhost', 4000, application, use_reloader=True)
