"""
Usage intructions
=================

To activate pass True as the 'inject_resources' keyword argument when initializing
TGWidgetsMiddleware,

See the demo WSGI app at examples/wsgi_app.py for an example.

Note that this module is *not* required at the moment. Former mechanism of
resource inclusion still works and is preferred since this is experimental code although
it will become the default in the future (so you might as well try it and
give feedback at mailing list ;)

It's *not* recommended to mix both methods since the most probable outcome is
that resources will be included twice.
"""
import re
import logging

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from tw import framework
from tw.core.util import MultipleReplacer

log = logging.getLogger(__name__)


__all__ = ["inject_resources", "injector_middleware"]

def injector_middleware(app):
    """Middleware that injects resources into the page whenever the output
    is html (peeks into Content-Type header) and no errors occur in lower layers
    """
    def _injector(environ, start_response):
        context = {'inject':False, 'fileobj':StringIO()}
        def determine_response_type(status, headers, exc_info = None):
            """Wraps start_response to have a chance to inspect headers and
            determine if the respons is html."""
            if not exc_info:
                for name, val in headers:
                    if name.lower() == 'content-type' and 'html' in val.lower():
                        context['inject'] = True
                        context['charset'] = find_charset(val)
                        context['headers'] = headers
                        context['status'] = status
            if not context['inject']:
                writer = start_response(status, headers, exc_info)
            else:
                writer = context['fileobj'].write
            return writer
            
        app_iter = app(environ, determine_response_type)
        if context['inject']:
            #XXX check PEP 333 to see if this is correct behaviour
            html = context['fileobj'].getvalue() + ''.join(app_iter)
            if hasattr(app_iter, 'close'):
                app_iter.close()
            # Must try to inject resources after consuming app_iter
            html = inject_resources(html, encoding=context['charset'])
            # Set updated content-length
            headers = [h for h in context['headers']
                         if h[0].lower() != 'content-length']
            headers.append(('Content-Length', str(len(html))))
            start_response(context['status'], headers)
            app_iter = [html]
        return app_iter
    return _injector



class _ResourceInjector(MultipleReplacer):
    def __init__(self):
        return MultipleReplacer.__init__(self, {
            r'<head.*?>': self._injector_for_location('head'),
            r'<body.*?>': self._injector_for_location('bodytop'),
            r'</body.*?>': self._injector_for_location('bodybottom', False)
            }, re.I|re.M)

    def _injector_for_location(self, key, after=True):
        def inject(group, resources, encoding):
            inj = u'\n'.join(r.render() for r in resources.get(key, []))
            inj = inj.encode(encoding)
            if after:
                return group + inj
            return  inj + group
        return inject

    def __call__(self, html, resources=None, encoding=None):
        """Injects resources, if any, into html string.

        ``html`` must be a ``encoding`` encoded string. If ``encoding`` is not
        given it will be tried to be derived from a <meta http-equiv> tag.
        
        Resources for current request can be obtained by calling
        ``tw.framework.pop_resources()``. This will remove resources
        from request and a further call to ``pop_resources()`` will return an
        empty dict.
        """
        if resources is None:
            resources = framework.pop_resources()
        if resources:
            encoding = encoding or find_charset(html) or 'ascii'
            html = MultipleReplacer.__call__(self, html, resources, encoding)
        return html


inject_resources = _ResourceInjector()


_charset_re = re.compile(r"charset\s*=\s*(?P<charset>[\w-]+)([^\>])*",
                         re.I|re.M)
def find_charset(string):
    m = _charset_re.search(string)
    if m:
        return m.group('charset').lower()
