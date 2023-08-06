from tw.core.view import EngineManager
from tw.core.util import RequestLocalDescriptor
from tw.core.registry import StackedObjectProxy, Registry

__all__ = ["HostFramework"]

class RequestLocal(object):
    def __init__(self, environ):
        self.environ = environ
        self.resources = {}

class HostFramework(object):
    """
    This class is the interface between TGWidgets and the framework that's
    using them.

    The an instance of this class should be passed as second argument to
    TGWidgetsMiddleware which will call its 'start_request' method at the
    beginning of every request and 'end_request' when the request is over.

    An app-local StackedObjectProxy of the configured instance is placed at
    ``tw.framework`` for convenient access.

    Parameters:

    `engines`
      An initialized EngineManager with the framework's settings and all 
      needed plugins loaded.

    `default_view`
      The name of the template engine used by default in the container app's
      templates. It's used by ``Widget.display`` to determine what conversion
      is neccesary when displaying root widgets on a template. 

    `translator`
      Function used to translate strings.
    """
    request_local = StackedObjectProxy(name="ToscaWidgets per-request storage")
    request_local_class = RequestLocal

    default_view = RequestLocalDescriptor('default_view', 'toscawidgets')

    def __init__(self, engines=None, default_view='toscawidgets',
                 translator=lambda s: s):
        """
        HostFramework should be initialized once per app setup and passed
        to TGWidgetsMiddleware so it provides it in each app's context.
        """
        if engines is None:
            engines = EngineManager()
        self.engines = engines
        self._default_view = default_view
        self.translator = translator
    
    def start_request(self, environ):
        registry = environ['paste.registry']
        registry.register(self.request_local, self.request_local_class(environ))
        self.request_local.default_view = self._default_view

    def end_request(self, environ):
        pass

    def url(self, url):
        """
        Returns the absolute path for the given url.
        """
        prefix = self.request_local.environ['toscawidgets.prefix']
        script_name = self.request_local.environ['SCRIPT_NAME']
        return ''.join([script_name, prefix, url])

    def register_resources(self, resources):
        """
        Registers resources for injection in the current request.
        """
        from tw.api import merge_resources
        merge_resources(self.request_local.resources, resources)

    def pop_resources(self):
        """
        Returns returns the resources that have been registered for this
        request and removes them from request-local
        """
        resources =  self.request_local.resources.copy()
        self.request_local.resources.clear()
        return resources
