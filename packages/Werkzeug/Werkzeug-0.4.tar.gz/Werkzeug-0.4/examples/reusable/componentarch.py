from werkzeug import Request, Response


class Component(object):
    """Baseclass for all components."""

    def __init__(self, manager, app):
        self.manager = manager
        self.app = app


class ExtensionPoint(object):
    """A descriptor that provides a list of all components of a
    given type when accessed.
    """

    def __init__(self, component_type):
        self.component_type = component_type

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.manager.get_components(self.component_type)


class ComponentManager(object):
    """Manages components."""

    def __init__(self, app):
        self.components = {}
        self.app = app

    def get_component_types(self):
        return Component.__subclasses__()

    def get_components(self, component_type):
        if Component not in component_type.__bases__:
            raise TypeError('%r is not a component type' %
                            component_type.__name__)
        result = []
        for cls in component_type.__subclasses__():
            if cls not in self.components:
                self.components[cls] = cls(self, self.app)
            result.append(self.components[cls])
        return result


class RequestHandler(Component):
    """A component type for request handlers."""

    def match_request(self, request):
        return False

    def handle_request(self, request):
        raise NotImplementedError()


class MyRequestHandler(RequestHandler):

    def match_request(self, request):
        return request.path == '/'

    def handle_request(self, request):
        return Response('Hello World')


class Application(object):
    """The application."""
    request_handlers = ExtensionPoint(RequestHandler)

    def __init__(self, configuration=None):
        self.configuration = configuration or {}
        self.manager = ComponentManager(self)

    @Request.application
    def __call__(self, request):
        for handler in self.request_handlers:
            if handler.match_request(request):
                return handler.handle_request(request)
        return Response('Not Found', status=404)


if __name__ == '__main__':
    from werkzeug import run_simple
    application = Application()
    run_simple('localhost', 4000, application)
