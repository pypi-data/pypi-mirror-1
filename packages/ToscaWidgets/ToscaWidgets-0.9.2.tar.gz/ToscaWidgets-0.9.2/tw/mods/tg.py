import pprint
from pkg_resources import require
require("TurboGears>=1.0")

import os, logging

from tw.core.registry import Registry
import turbogears, cherrypy
from cherrypy.filters.basefilter import BaseFilter
from turbogears.i18n.tg_gettext import gettext
from turbogears import util as tg_util
from turbogears.view import stdvars

import tw
from tw.core import view, resource_injector, resources
from tw.mods.base import HostFramework
from tw.core.util import RequestLocalDescriptor, install_framework

install_framework()

log = logging.getLogger(__name__)

class Turbogears(HostFramework):

    @property
    def request_local(self):
        try:
            rl = cherrypy.request.tw_request_local
        except AttributeError:
            rl = self.request_local_class(cherrypy.request.wsgi_environ)
            cherrypy.request.tw_request_local = rl
        return rl

    def start_request(self, environ):
        self.request_local.default_view = self._default_view

    def url(self, url):
        """
        Returns the absolute path for the given url.
        """
        prefix = self.request_local.environ['toscawidgets.prefix']
        # make sure we only have a single slash at the beginning of the URL
        return '/' + turbogears.url(prefix+url).lstrip('/')

def _extract_config():
    from cherrypy.config import configs
    c = configs.get('global', {}).copy()
    c.update(configs['/'])
    return c

class TWInitFilter(BaseFilter):
    """Sort-of-emulates TWWidgetsMiddleware + Paste's RegsitryManager. Takes
    care of preparing the hostframework for a request."""

    def __init__(self, host_framework, prefix='/toscawidgets',
                 serve_files=True):
        self.serve_files = serve_files
        self.prefix = prefix
        self.host_framework = host_framework

    def on_start_resource(self):
        log.debug("TWFilter: on_start_resource")
        environ = cherrypy.request.wsgi_environ
        registry = environ.setdefault('paste.registry', Registry())
        environ['toscawidgets.prefix'] = self.prefix
        registry.prepare()
        registry.register(tw.framework, self.host_framework)
        self.host_framework.start_request(environ)

    def before_main(self):
        """Intercepts requests for static files and serves them."""
        if not self.serve_files:
            return
        req, resp = cherrypy.request, cherrypy.response
        path = req.path
        if path.startswith(self.host_framework.webpath):
            path = path[len(self.host_framework.webpath):]        
        if path.startswith(self.prefix):
            reg = resources.registry
            path = path[len(self.prefix)+len(reg.prefix):]
            stream, ct, enc = reg.get_stream_type_encoding(path)
            if stream:
                resp.body = stream
                if ct:
                    if enc:
                        ct += '; charset=' + enc
                    resp.headers['Content-Type'] = ct
                req.execute_main = False


    def before_finalize(self):
        # Injects resources
        log.debug("TWFilter: before_finalize")
        response = cherrypy.response
        ct = response.headers.get('content-type', 'text/html').lower()
        if 'html' in ct:
            cs = resource_injector.find_charset(ct)
            html = ''.join(response.body)
            resources = tw.framework.pop_resources()
            log.debug("Injecting Resources:")
            map(log.debug, pprint.pformat(resources).split('\n'))

            html = resource_injector.inject_resources(html=html,
                                                     resources=resources,
                                                     encoding=cs)
            response.body = [html]
            # Delete Content-Length header so finalize() recalcs it.
            response.headers.pop("Content-Length", None)
        
    def on_end_resource(self):
        log.debug("TWFilter: on_end_resource")
        try:
            environ = cherrypy.request.wsgi_environ
            self.host_framework.end_request(environ)
        finally:
            registry = environ['paste.registry']
            registry.cleanup()

def start_extension():
    if turbogears.config.get('toscawidgets.on', False):
        engines = view.EngineManager()
        engines.load_all(_extract_config(), stdvars)
        host_framework = Turbogears(
            engines = engines,
            default_view = turbogears.config.get('tg.defaultview', 'kid'),
            translator = gettext,
            )
        prefix = turbogears.config.get('toscawidgets.prefix', '/toscawidgets')
        host_framework.prefix = prefix
        host_framework.webpath = turbogears.config.get('server.webpath', '')
        log.info("Loaded TurboGears HostFramework")
        filter_args = dict(
            prefix = prefix,
            serve_files = turbogears.config.get('toscawidgets.serve_files', 1)
            )
        cherrypy.root._cp_filters.append(TWInitFilter(host_framework,
                                                      **filter_args))
        log.info("Added TWInitFilter")
