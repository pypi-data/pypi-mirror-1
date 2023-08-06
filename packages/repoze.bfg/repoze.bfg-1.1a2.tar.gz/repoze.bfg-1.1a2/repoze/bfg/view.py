import cgi
import os
import inspect
import mimetypes

# See http://bugs.python.org/issue5853 which is a recursion bug
# that seems to effect Python 2.6, Python 2.6.1, and 2.6.2 (a fix
# has been applied on the Python 2 trunk).  This workaround should
# really be in Paste if anywhere, but it's easiest to just do it
# here and get it over with to avoid needing to deal with any
# fallout.

if hasattr(mimetypes, 'init'):
    mimetypes.init()

from webob import Response

from paste.urlparser import StaticURLParser

from zope.component import queryUtility
from zope.component import providedBy
from zope.component import getSiteManager

from zope.interface import implements

from zope.deprecation import deprecated

from repoze.bfg.interfaces import IResponseFactory
from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import IMultiView

from repoze.bfg.path import caller_package

from repoze.bfg.static import PackageURLParser

from repoze.bfg.templating import renderer_from_path
from repoze.bfg.templating import _auto_reload

deprecated('view_execution_permitted',
    "('from repoze.bfg.view import view_execution_permitted' was  "
    "deprecated as of repoze.bfg 1.0; instead use 'from "
    "repoze.bfg.security import view_execution_permitted')",
    )

_marker = object()

def render_view_to_response(context, request, name='', secure=True):
    """ Render the view named ``name`` against the specified
    ``context`` and ``request`` to an object implementing
    ``repoze.bfg.interfaces.IResponse`` or ``None`` if no such view
    exists.  This function will return ``None`` if a corresponding
    view cannot be found.  If ``secure`` is ``True``, and the view is
    protected by a permission, the permission will be checked before
    calling the view function.  If the permission check disallows view
    execution (based on the current security policy), a
    ``repoze.bfg.security.Unauthorized`` exception will be raised; its
    ``args`` attribute explains why the view access was disallowed.
    If ``secure`` is ``False``, no permission checking is done."""
    provides = map(providedBy, (context, request))
    sm = getSiteManager()
    view = sm.adapters.lookup(provides, IView, name=name)
    if view is None:
        return None

    if not secure:
        # the view will have a __permissive_view__ attribute if it's
        # secured; otherwise it won't.
        view = getattr(view, '__call_permissive__', view)

    # if this view is secured, it will raise an Unauthorized
    # appropriately if the executing user does not have the proper
    # permission
    return view(context, request)

def render_view_to_iterable(context, request, name='', secure=True):
    """ Render the view named ``name`` against the specified
    ``context`` and ``request``, and return an iterable representing
    the view response's ``app_iter`` (see the interface named
    ``repoze.bfg.interfaces.IResponse``).  This function will return
    ``None`` if a corresponding view cannot be found.  Additionally,
    this function will raise a ``ValueError`` if a view function is
    found and called but the view does not return an object which
    implements ``repoze.bfg.interfaces.IResponse``.  You can usually
    get the string representation of the return value of this function
    by calling ``''.join(iterable)``, or just use ``render_view``
    instead.  If ``secure`` is ``True``, and the view is protected by
    a permission, the permission will be checked before calling the
    view function.  If the permission check disallows view execution
    (based on the current security policy), a
    ``repoze.bfg.security.Unauthorized`` exception will be raised; its
    ``args`` attribute explains why the view access was disallowed.
    If ``secure`` is ``False``, no permission checking is done."""
    response = render_view_to_response(context, request, name, secure)
    if response is None:
        return None
    return response.app_iter

def render_view(context, request, name='', secure=True):
    """ Render the view named ``name`` against the specified
    ``context`` and ``request``, and unwind the the view response's
    ``app_iter`` (see the interface named
    ``repoze.bfg.interfaces.IResponse``) into a single string.  This
    function will return ``None`` if a corresponding view cannot be
    found.  Additionally, this function will raise a ``ValueError`` if
    a view function is found and called but the view does not return
    an object which implements ``repoze.bfg.interfaces.IResponse``.
    If ``secure`` is ``True``, and the view is protected by a
    permission, the permission will be checked before calling the view
    function.  If the permission check disallows view execution (based
    on the current security policy), a
    ``repoze.bfg.security.Unauthorized`` exception will be raised; its
    ``args`` attribute explains why the view access was disallowed.
    If ``secure`` is ``False``, no permission checking is done."""
    iterable = render_view_to_iterable(context, request, name, secure)
    if iterable is None:
        return None
    return ''.join(iterable)

def is_response(ob):
    """ Return True if ``ob`` implements the
    ``repoze.bfg.interfaces.IResponse`` interface, False if not.  Note
    that this isn't actually a true Zope interface check, it's a
    duck-typing check, as response objects are not obligated to
    actually implement a Zope interface."""
    # response objects aren't obligated to implement a Zope interface,
    # so we do it the hard way
    if ( hasattr(ob, 'app_iter') and hasattr(ob, 'headerlist') and
         hasattr(ob, 'status') ):
        if ( hasattr(ob.app_iter, '__iter__') and
             hasattr(ob.headerlist, '__iter__') and
             isinstance(ob.status, basestring) ) :
            return True
    return False

class static(object):
    """ An instance of this class is a callable which can act as a BFG
    view; this view will serve static files from a directory on disk
    based on the ``root_dir`` you provide to its constructor.

    The directory may contain subdirectories (recursively); the static
    view implementation will descend into these directories as
    necessary based on the components of the URL in order to resolve a
    path into a response.

    You may pass an absolute or relative filesystem path to the
    directory containing static files directory to the constructor as
    the ``root_dir`` argument.

    If the path is relative, and the ``package`` argument is ``None``,
    it will be considered relative to the directory in which the
    Python file which calls ``static`` resides.  If the ``package``
    name argument is provided, and a relative ``root_dir`` is
    provided, the ``root_dir`` will be considered relative to the
    Python package specified by ``package_name`` (a dotted path to a
    Python package).

    ``cache_max_age`` influences the Expires and Max-Age response
    headers returned by the view (default is 3600 seconds or five
    minutes).  ``level`` influences how relative directories are
    resolved (the number of hops in the call stack), not used very
    often.

    .. note:: If the ``root_dir`` is relative to a package, the BFG
       ``resource`` ZCML directive can be used to override resources
       within the named ``root_dir`` package-relative directory.
       However, if the ``root_dir`` is absolute, the ``resource``
       directive will not be able to override the resources it
       contains.
    """
    def __init__(self, root_dir, cache_max_age=3600, level=2,
                 package_name=None):
        # package_name is for bw compat; it is preferred to pass in a
        # package-relative path as root_dir
        # (e.g. ``anotherpackage:foo/static``).
        if os.path.isabs(root_dir):
            self.app = StaticURLParser(root_dir, cache_max_age=cache_max_age)
            return
        # not os.path.isabs below for windows systems
        if (':' in root_dir) and (not os.path.isabs(root_dir)):
            package_name, root_dir = root_dir.split(':', 1)
        else:
            if package_name is None:
                package_name = caller_package().__name__

        self.app = PackageURLParser(package_name, root_dir,
                                    cache_max_age=cache_max_age)

    def __call__(self, context, request):
        subpath = '/'.join(request.subpath)
        request_copy = request.copy()
        # Fix up PATH_INFO to get rid of everything but the "subpath"
        # (the actual path to the file relative to the root dir).
        request_copy.environ['PATH_INFO'] = '/' + subpath
        # Zero out SCRIPT_NAME for good measure.
        request_copy.environ['SCRIPT_NAME'] = ''
        return request_copy.get_response(self.app)

class bfg_view(object):
    """ Function or class decorator which allows Python code to make
    view registrations instead of using ZCML for the same purpose.

    E.g. in the module ``views.py``::

      from models import IMyModel
      from repoze.bfg.interfaces import IRequest

      @bfg_view(name='my_view', request_type=IRequest, for_=IMyModel,
                permission='read', route_name='site1'))
      def my_view(context, request):
          return render_template_to_response('templates/my.pt')

    Equates to the ZCML::

      <view
       for='.models.IMyModel'
       view='.views.my_view'
       name='my_view'
       permission='read'
       route_name='site1'
       />

    The following arguments are supported: ``for_``, ``permission``,
    ``name``, ``request_type``, ``route_name``, ``request_method``,
    ``request_param``, and ``containment``.

    If ``for_`` is not supplied, the interface
    ``zope.interface.Interface`` (matching any context) is used.

    If ``permission`` is not supplied, no permission is registered for
    this view (it's accessible by any caller).

    If ``name`` is not supplied, the empty string is used (implying
    the default view name).

    If ``attr`` is not supplied, ``None`` is used (implying the
    function itself if the view is a function, or the ``__call__``
    callable attribute if the view is a class).

    If ``template`` is not supplied, ``None`` is used (meaning that no
    template is associated with this view).

    If ``request_type`` is not supplied, the interface
    ``repoze.bfg.interfaces.IRequest`` is used, implying the standard
    request interface type.

    If ``route_name`` is not supplied, the view declaration is
    considered to be made against a URL that doesn't match any defined
    :term:`route`.  The use of a ``route_name`` is an advanced
    feature, useful only if you're using :term:`url dispatch`.

    If ``request_method`` is not supplied, this view will match a
    request with any HTTP ``REQUEST_METHOD``
    (GET/POST/PUT/HEAD/DELETE).  If this parameter *is* supplied, it
    must be a string naming an HTTP ``REQUEST_METHOD``, indicating
    that this view will only match when the current request has a
    ``REQUEST_METHOD`` that matches this value.

    If ``request_param`` is not supplied, this view will be called
    when a request with any (or no) request GET or POST parameters is
    encountered.  If the value is present, it must be a string.  If
    the value supplied to the parameter has no ``=`` sign in it, it
    implies that the key must exist in the ``request.params``
    dictionary for this view to'match' the current request.  If the value
    supplied to the parameter has a ``=`` sign in it, e.g.
    ``request_params="foo=123"``, then the key (``foo``) must both exist
    in the ``request.params`` dictionary, and the value must match the
    right hand side of the expression (``123``) for the view to "match" the
    current request.

    If ``containment`` is not supplied, this view will be called when
    the context of the request has any location lineage.  If
    ``containment`` *is* supplied, it must be a class or :term:`interface`,
    denoting that the view 'matches' the current request only if any graph
    lineage node possesses this class or interface.

    Any individual or all parameters can be omitted.  The simplest
    bfg_view declaration then becomes::

        @bfg_view()
        def my_view(...):
            ...

    Such a registration implies that the view name will be
    ``my_view``, registered for models with the
    ``zope.interface.Interface`` interface, using no permission,
    registered against requests which implement the default IRequest
    interface when no urldispatch route matches, with any
    REQUEST_METHOD, any set of request.params values, in any lineage
    containment.

    The ``bfg_view`` decorator can also be used as a class decorator
    in Python 2.6 and better (Python 2.5 and below do not support
    class decorators)::

        from webob import Response
        from repoze.bfg.view import bfg_view

        @bfg_view()
        class MyView(object):
            def __init__(self, context, request):
                self.context = context
                self.request = request
            def __call__(self):
                return Response('hello from %s!' % self.context)

    In Python 2.5 and below, the bfg_view decorator can still be used
    against a class, although not in decorator form::

        from webob import Response
        from repoze.bfg.view import bfg_view

        class MyView(object):
            def __init__(self, context, request):
                self.context = context
                self.request = request
            def __call__(self):
                return Response('hello from %s!' % self.context)

        MyView = bfg_view()(MyView)

    .. note:: When a view is a class, the calling semantics are
              different than when it is a function or another
              non-class callable.  See :ref:`class_as_view` for more
              information.

    .. warning:: Using a class as a view is a new feature in 0.8.1+.

    To make use of any bfg_view declaration, you *must* insert the
    following boilerplate into your application registry's ZCML::
    
      <scan package="."/>
    """
    def __init__(self, name='', request_type=None, for_=None, permission=None,
                 route_name=None, request_method=None, request_param=None,
                 containment=None, attr=None, template=None):
        self.name = name
        self.request_type = request_type
        self.for_ = for_
        self.permission = permission
        self.route_name = route_name
        self.request_method = request_method
        self.request_param = request_param
        self.containment = containment
        self.attr = attr
        self.template = template

    def __call__(self, wrapped):
        _bfg_view = map_view(wrapped, self.attr, self.template)
        _bfg_view.__is_bfg_view__ = True
        _bfg_view.__permission__ = self.permission
        _bfg_view.__for__ = self.for_
        _bfg_view.__view_name__ = self.name
        _bfg_view.__request_type__ = self.request_type
        _bfg_view.__route_name__ = self.route_name
        _bfg_view.__request_method__ = self.request_method
        _bfg_view.__request_param__ = self.request_param
        _bfg_view.__containment__ = self.containment
        return _bfg_view

def default_view(context, request, status):
    try:
        msg = cgi.escape(request.environ['repoze.bfg.message'])
    except KeyError:
        msg = ''
    html = """
    <html>
    <title>%s</title>
    <body>
    <h1>%s</h1>
    <code>%s</code>
    </body>
    </html>
    """ % (status, status, msg)
    headers = [('Content-Length', str(len(html))),
               ('Content-Type', 'text/html')]
    response_factory = queryUtility(IResponseFactory, default=Response)
    return response_factory(status = status,
                            headerlist = headers,
                            app_iter = [html])

def default_forbidden_view(context, request):
    return default_view(context, request, '401 Unauthorized')

def default_notfound_view(context, request):
    return default_view(context, request, '404 Not Found')

class NotFound(Exception):
    pass

class MultiView(object):
    implements(IMultiView)

    def __init__(self, name):
        self.name = name
        self.views = []

    def add(self, view, score):
        self.views.append((score, view))
        self.views.sort()

    def match(self, context, request):
        for score, view in self.views:
            if not hasattr(view, '__predicated__'):
                return view
            if view.__predicated__(context, request):
                return view
        raise NotFound(self.name)

    def __permitted__(self, context, request):
        view = self.match(context, request)
        if hasattr(view, '__permitted__'):
            return view.__permitted__(context, request)
        return True

    def __call_permissive__(self, context, request):
        view = self.match(context, request)
        view = getattr(view, '__call_permissive__', view)
        return view(context, request)

    def __call__(self, context, request):
        for score, view in self.views:
            try:
                return view(context, request)
            except NotFound:
                continue
        raise NotFound(self.name)

def templated_response(template_name, response, view, context, request,
                       auto_reload=False):
    if is_response(response):
        return response
    renderer = renderer_from_path(template_name, auto_reload=auto_reload)
    kw = {'view':view, 'template_name':template_name, 'context':context,
          'request':request}
    try:
        kw.update(response)
    except TypeError:
        return response
    result = renderer(**kw)
    response_factory = queryUtility(IResponseFactory, default=Response)
    response = response_factory(result)
    content_type = kw.get('content_type_', None)
    if content_type is not None:
        response.content_type = content_type
    headerlist = kw.get('headerlist_', None)
    if headerlist is not None:
        for k, v in headerlist:
            response.headers.add(k, v)
    status = kw.get('status_', None)
    if status is not None:
        response.status = status
    charset = kw.get('charset_', None)
    if charset is not None:
        response.charset = charset
    cache_for = kw.get('cache_for_', None)
    if cache_for is not None:
        response.cache_expires = cache_for
    return response

def map_view(view, attr=None, template=None):
    wrapped_view = view
    auto_reload = _auto_reload()

    if inspect.isclass(view):
        # If the object we've located is a class, turn it into a
        # function that operates like a Zope view (when it's invoked,
        # construct an instance using 'context' and 'request' as
        # position arguments, then immediately invoke the __call__
        # method of the instance with no arguments; __call__ should
        # return an IResponse).
        if requestonly(view, attr):
            # its __init__ accepts only a single request argument,
            # instead of both context and request
            def _bfg_class_requestonly_view(context, request):
                inst = view(request)
                if attr is None:
                    response = inst()
                else:
                    response = getattr(inst, attr)()
                if template:
                    response = templated_response(template, response, inst,
                                                  context, request, auto_reload)
                return response
            wrapped_view = _bfg_class_requestonly_view
        else:
            # its __init__ accepts both context and request
            def _bfg_class_view(context, request):
                inst = view(context, request)
                if attr is None:
                    response = inst()
                else:
                    response = getattr(inst, attr)()
                if template:
                    response = templated_response(template, response, inst,
                                                  context, request, auto_reload)
                return response
            wrapped_view = _bfg_class_view

    elif requestonly(view, attr):
        # its __call__ accepts only a single request argument,
        # instead of both context and request
        def _bfg_requestonly_view(context, request):
            if attr is None:
                response = view(request)
            else:
                response = getattr(view, attr)(request)

            if template:
                response = templated_response(template, response, view,
                                              context, request, auto_reload)
            return response
        wrapped_view = _bfg_requestonly_view

    elif attr:
        def _bfg_attr_view(context, request):
            response = getattr(view, attr)(context, request)
            if template:
                response = templated_response(template, response, view,
                                              context, request, auto_reload)
            return response
        wrapped_view = _bfg_attr_view

    elif template:
        def _templated_view(context, request):
            response = view(context, request)
            response = templated_response(template, response, view,
                                          context, request, auto_reload)
            return response
        wrapped_view = _templated_view

    decorate_view(wrapped_view, view)
    return wrapped_view

def requestonly(class_or_callable, attr=None):
    """ Return true of the class or callable accepts only a request argument,
    as opposed to something that accepts context, request """
    if attr is None:
        attr = '__call__'
    if inspect.isfunction(class_or_callable):
        fn = class_or_callable
    elif inspect.isclass(class_or_callable):
        try:
            fn = class_or_callable.__init__
        except AttributeError:
            return False
    else:
        try:
            fn = getattr(class_or_callable, attr)
        except AttributeError:
            return False

    try:
        argspec = inspect.getargspec(fn)
    except TypeError:
        return False

    args = argspec[0]
    defaults = argspec[3]

    if hasattr(fn, 'im_func'):
        # it's an instance method
        if not args:
            return False
        args = args[1:]
    if not args:
        return False

    if len(args) == 1:
        return True

    elif args[0] == 'request':
        if len(args) - len(defaults) == 1:
            return True

    return False

def decorate_view(wrapped_view, original_view):
    if wrapped_view is not original_view:
        wrapped_view.__module__ = original_view.__module__
        wrapped_view.__doc__ = original_view.__doc__
        try:
            wrapped_view.__name__ = original_view.__name__
        except AttributeError:
            wrapped_view.__name__ = repr(original_view)
        try:
            wrapped_view.__permitted__ = original_view.__permitted__
        except AttributeError:
            pass
        try:
            wrapped_view.__call_permissive__ = original_view.__call_permissive__
        except AttributeError:
            pass
        try:
            wrapped_view.__predicated__ = original_view.__predicated__
        except AttributeError:
            pass
        return True
    return False
