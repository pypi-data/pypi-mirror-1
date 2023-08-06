from webob import Response

from zope.component import queryUtility
from zope.interface import implements

from repoze.bfg.interfaces import IResponseFactory
from repoze.bfg.interfaces import ITemplateRenderer

from chameleon.zpt.template import PageTemplateFile

from repoze.bfg.renderers import template_renderer_factory
from repoze.bfg.settings import get_settings

def renderer_factory(path, level=4):
    return template_renderer_factory(path, ZPTTemplateRenderer, level=4)

class ZPTTemplateRenderer(object):
    implements(ITemplateRenderer)
    def __init__(self, path):
        settings = get_settings()
        auto_reload = settings and settings['reload_templates']
        self.template = PageTemplateFile(path, auto_reload=auto_reload)

    def implementation(self):
        return self.template
    
    def __call__(self, kw):
        return self.template(**kw)

def get_renderer(path):
    """ Return a callable ``ITemplateRenderer`` object representing a
    ``chameleon.zpt`` template at the package-relative path (may also
    be absolute). """
    return renderer_factory(path)

def get_template(path):
    """ Return a ``chameleon.zpt`` template at the package-relative
    path (may also be absolute).  """
    renderer = renderer_factory(path)
    return renderer.implementation()

def render_template(path, **kw):
    """ Render a ``chameleon.zpt`` template at the package-relative
    path (may also be absolute) using the kwargs in ``*kw`` as
    top-level names and return a string."""
    renderer = renderer_factory(path)
    return renderer(kw)

def render_template_to_response(path, **kw):
    """ Render a ``chameleon.zpt`` template at the package-relative
    path (may also be absolute) using the kwargs in ``*kw`` as
    top-level names and return a Response object with the body as the
    template result. """
    renderer = renderer_factory(path)
    result = renderer(kw)
    response_factory = queryUtility(IResponseFactory, default=Response)
    return response_factory(result)

