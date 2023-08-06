from urllib import unquote

import pkg_resources

from webob import Request
from tw.core.registry import RegistryManager

import tw
from tw.mods import base
from tw.core import resources
from tw.core.util import asbool

__all__ = ["ToscaWidgetsMiddleware", "make_middleware"]
    
class ToscaWidgetsMiddleware(object):
    def __init__(self, application, host_framework, prefix='/toscawidgets',
                 inject_resources=True):
        self.host_framework = host_framework
        self.prefix = prefix

        self.application = application

        if inject_resources:
            from tw.core.resource_injector import injector_middleware
            self.application = injector_middleware(self.application)

        self.wsgi_app = RegistryManager(self.wsgi_app)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ, start_response):
        self.host_framework.start_request(environ)
        environ['toscawidgets.prefix'] = self.prefix
        environ['paste.registry'].register(tw.framework, self.host_framework)
        environ.setdefault('toscawidgets.framework', self.host_framework)

        req = Request(environ)
        try:
            if req.path_info.startswith(self.prefix):
                req.path_info = req.path_info[len(self.prefix):]
                req.script_name += self.prefix
                reg = resources.registry
                if req.path_info.startswith(reg.prefix):
                    req.path_info = req.path_info[len(reg.prefix):]
                    req.script_name += reg.prefix
                    return req.get_response(reg)(environ, start_response)
            return req.get_response(self.application)(environ, start_response)
        finally:
            self.host_framework.end_request(environ)

#TODO: Wrap to issue deprecation warnings
TGWidgetsMiddleware = ToscaWidgetsMiddleware

def _load_from_entry_point(name):
    for ep in pkg_resources.iter_entry_points('toscawidgets.host_frameworks'):
        if ep.name == name:
            return ep
        
def _extract_args(args, prefix, adapters={}):
    l = len(prefix)
    nop = lambda v: v
    return dict((k[l:], adapters.get(k[l:], nop)(v))
                for k,v in args.iteritems() if k.startswith(prefix))
    
def _load_host_framework(host_framework):
    if ':' not in host_framework:
        ep = _load_from_entry_point(host_framework)
    else:
        ep = pkg_resources.EntryPoint.parse("hf="+host_framework)
    if ep:
        hf = ep.load(False)
    else:
        hf = None
    if not hf:
        raise LookupError("Could not load %s" % host_framework)
    return hf

def make_middleware(app, config=None):
    config = (config or {}).copy()
    host_framework = config.pop('toscawidgets.framework', 'wsgi')
    if isinstance(host_framework, basestring):
        host_framework = _load_host_framework(host_framework)
    middleware_args = _extract_args(config, 'toscawidgets.middleware.', {
        'inject_resources': asbool,
        })
    hf_args = _extract_args(config, 'toscawidgets.framework.')
    return ToscaWidgetsMiddleware(app, host_framework=host_framework(**hf_args),
                                  **middleware_args)
