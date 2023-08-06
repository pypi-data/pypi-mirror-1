import threading
import itertools

from paste.wsgiwrappers import WSGIRequest, WSGIResponse
from paste.urlmap import URLMap

import tw
from tw.core.view import Renderable
from tw.core.exceptions import WidgetException

class FeederException(WidgetException):
    pass

_feeder_serial = itertools.count()

class BaseFeeder(Renderable):
    """WSGI app used to feed a widget.

    The ``mimetype`` attribute will be used to set the Content-Type
    header.

    Feeders can be used as basic Renderables to feed the widget manually if
    neccesary.

    The ``url`` property can be accessed obtain a url where the Feeder can
    be reached. 

    The Feeder can also be registered by calling its `register` method.

    THIS PART OF THE API IS EXPERIMENTAL AND SUBJECT TO CHANGE OR EVEN 
    DISAPPEAR!
    """
    # Makes Pylons' WSGIController delegate to this app when returned by
    # by a controller method
    wsgi_response = True
    mimetype = "text/plain"
    _url = None

    def register(self, name=None):
        if name is None:
            name = "feeder-%d" % _feeder_serial.next()
        self._url = registry.register(self, name)
        return self

    @property
    def registered(self):
        return bool(self._url)

    @property
    def url(self):
        if not self.registered:
            raise AttributeError("The feeder %r is not registered" % self)
        return tw.framework.url(self._url)

    def get_parameters(self, environ):
        """Returns parameters for the feed method from the request's environment
        This method is only used when the feeder acts as a WSGI app."""
        return dict(WSGIRequest(environ).params)

    def feed(self):
        """This method is the "controller" method that should return the data
        to feed the widget.

        Usually by building a dict and passing it to self.render

        Its signature can be whatever makes sense for the given feeder.

        If the feeder is used as a WSGI app, the call will be adapted from 
        request params (both GET/POST) a la CherryPy, with the expception that
        unexpected parameters will be simply discarded (to avoid raising 
        expections from those random parameters async calls tend to include to
        fool even fooler IE's caching.)"""
        raise NotImplementedError("This method needs to be overriden")

    def _adapt_call(self, params):
        func = self.feed.im_func
        args, kw = adapt_call(func, (), params)
        return args, kw

        
    def wsgi_app(self, environ, start_response):
        """WSGI app that feeds the widget. This method should be overrided
        instead of __call__ so middleware can be wrapped when initializing the
        feeder."""
        #TODO: Make encoding configurable and set appropiate Content-Type header
        params = self.get_parameters(environ)
        args, kw = self._adapt_call(params)
        output = self.feed(*args, **kw).encode('utf-8') or ""
        mimetype = self.mimetype
        return WSGIResponse(output, mimetype=mimetype)(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


class FeederApp(object):
    def __init__(self, prefix='/feeder'):
        self._feeders = URLMap()
        self._lock = threading.Lock()
        self.prefix = prefix

    def register(self, feeder, name):
        modname = feeder.__class__.__module__
        clsname = feeder.__class__.__name__
        key = '/'.join(['', modname, clsname, name])
        self._lock.acquire()
        try:
            if key in self._feeders:
                raise FeederException("Feeder already registered at %r" % key)
            self._feeders[key] = feeder
        finally:
            self._lock.release()
        key = key.lstrip('/')
        return '/'.join([self.prefix, key])
    
    def __call__(self, environ, start_response):
        return self._feeders(environ, start_response)

registry = FeederApp()

        
###
#  Stolen from turbogears.util. Thanks Simon ;)
###

import inspect
from itertools import islice, chain, imap
from operator import isSequenceType

def adapt_call(func, args, kw, start=0):
    """Remove excess arguments."""
    argnames, varargs, kwargs, defaults = inspect.getargspec(func)
    defaults = ensure_sequence(defaults)
    del argnames[:start]
    if kwargs is None:
        remove_keys(kw, [key for key in kw.iterkeys() if key not in argnames])
    if varargs is None:
        args = args[:len(argnames) - len(defaults)]
    else:
        pivot = len(argnames) - len(defaults)
        args = tuple(chain(islice(args, pivot), imap(kw.pop, islice(
                        argnames, pivot, None)), islice(args, pivot, None)))
    return args, kw

def ensure_sequence(obj):
    """Construct a sequence from object."""
    if obj is None:
        return []
    elif isSequenceType(obj):
        return obj
    else:
        return [obj]

def remove_keys(dict_, seq):
    """Gracefully remove keys from dict."""
    for key in seq:
        dict_.pop(key, None)
    return dict_
