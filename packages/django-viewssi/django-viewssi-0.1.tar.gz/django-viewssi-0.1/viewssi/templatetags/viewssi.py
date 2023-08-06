from django import http, template
from django.conf import settings
from django.core import urlresolvers, exceptions
from django.core.handlers import base as basehandler
from django.utils import datastructures, safestring, encoding


register = template.Library()


class HttpResponseProxy(dict):
    def __init__(self, status_code, headers, content):
        self.status_code = str(status_code)
        for header_name, header_value in headers.items():
            self[header_name.lower().replace('-', '_')] = header_value
        self.content = safestring.mark_safe(content)

    def __unicode__(self):
        return self.content


class ViewSsiNode(template.Node):
    def __init__(self, view_func, args, kwargs, get_query, asvar):
        self.view_func = view_func
        self.args = args
        self.kwargs = kwargs
        self.get_query = get_query
        self.asvar = asvar

    def get_callable(self, view_func):
        module_path = view_func
        attnames = []
        while True:
            try:
                module = __import__(module_path, {}, {}, [''])
                if not attnames:
                    return module
                attr = module
                for attname in attnames:
                    attr = getattr(attr, attname)
                return attr
            except ImportError:
                bits = module_path.rsplit('.', 1)
                module_path = bits[0]
                attnames.insert(0, bits[1])

    def get_response(self, view_func, request, args, kwargs, get_query):
        # clone request
        subrequest = http.HttpRequest()
        for attname, attvalue in vars(request).items():
            setattr(subrequest, attname, attvalue)
        subrequest.method = 'GET'
        subrequest.GET = get_query
        subrequest.REQUEST = get_query

        # if this view_func has an URL, set the path info
        # to reflect what the url should be
        try:
            subrequest.path = subrequest.path_info = urlresolvers.reverse(
                view_func, args=args, kwargs=kwargs)
        except urlresolvers.NoReverseMatch:
            subrequest.path = subrequest.path_info = '/'

        # since we've cloned the request, we need to apply
        # the middleware to the cloned request
        handler = basehandler.BaseHandler()
        handler.load_middleware()

        # apply request middleware
        for middleware_method in handler._request_middleware:
            response = middleware_method(subrequest)
            if response:
                return response

        # apply view middleware
        for middleware_method in handler._view_middleware:
            response = middleware_method(request, view_func, args, kwargs)
            if response:
                return response

        max_depth = 100
        subrequest.viewssi_depth = getattr(subrequest, 'viewssi_depth', 0) + 1
        if hasattr(settings, 'VIEWSSI_MAX_RECURSION_DEPTH'):
            max_depth = settings.VIEWSSI_MAX_RECURSION_DEPTH
        if subrequest.viewssi_depth > max_depth:
            if hasattr(settings, 'VIEWSSI_ERROR_MESSAGE'):
                error_message = settings.VIEWSSI_ERROR_MESSAGE
            else:
                error_message = '<!-- viewssi include error -->'
            return http.HttpResponse(error_message, status='500')

        else:
            try:
                response = view_func(subrequest, *args, **kwargs)
            except Exception, e:
                # If the view raised an exception, run it through exception
                # middleware, and if the exception middleware returns a
                # response, use that. Otherwise, reraise the exception.
                for middleware_method in handler._exception_middleware:
                    response = middleware_method(subrequest, e)
                    if response:
                        return response
                raise
            # Complain if the view returned None (a common error).
            if response is None:
                try:
                    view_name = view_func.func_name
                except AttributeError:
                    view_name = view_func.__class__.__name__ + '.__call__'
                raise ValueError(
                    "The view %s.%s didn't return an HttpResponse object." % (
                            view_func.__module__, view_name))
            return response
            
    def render(self, context):
        if 'request' not in context:
            raise exceptions.ImproperlyConfigured(
                '\'django.core.context_processors.request\' '
                'must be in your TEMPLATE_CONTEXT_PROCESSORS setting')

        request = context['request']
        view_func = self.get_callable(self.view_func)
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict(
            [(encoding.smart_str(k,'ascii'), v.resolve(context))
             for k, v in self.kwargs.items()])

        get_query = datastructures.MultiValueDict()
        for key, value_list in self.get_query.lists():
            merged_value_list = []
            for value in value_list:
                value = value.resolve(context)
                if hasattr(value, '__iter__'):
                    merged_value_list += map(
                        lambda v: encoding.smart_unicode(v), value)
                else:
                    merged_value_list.append(encoding.smart_unicode(value))
            get_query.setlist(key, merged_value_list)

        response = self.get_response(
            view_func, request, args, kwargs, get_query)
        responseproxy = HttpResponseProxy(
            response.status_code, response._headers, response.content)

        if self.asvar:
            context[self.asvar] = responseproxy
            return ''
        else:
            return responseproxy.content


def viewssi(parser, token):
    """
    Get a response from a view for inclusion in the template.

    Variations of usage of ``viewssi``::

        {% viewssi path.to.view %}
        {% viewssi path.to.view arg,arg2,kwarg=val %}
        {% viewssi path.to.view arg,arg2,kwarg=val as var %}
        {% viewssi path.to.view arg,arg2,kwarg=val get p1=v1,p2=v2 as var %}

    The first argument is the path to a view function to call. If the
    view requires ``args`` and/or ``kwargs``, pass them as the second
    token in the tag. ``args`` and the values of ``kwargs`` are
    resolved to template variables unless they are quoted.

    The view doesn't have to be exposed in a URL
    configuration. Essentially any function can be called that accepts
    one argument (the request) and returns a
    ``django.http.HttpResponse`` object.

    You can pass a GET query string by including a ``get`` token in
    the tag followed by ``key=value`` pairs. Parameter values are also
    resolved to template variables unless they are quoted.

    If the ``as <template-variable-name`` token of the tag is
    provided, the view's response is assigned to the given template
    variable. Otherwise, the response content is returned in place.

    When the response is assigned to a template variable, the http
    response is represented as a ``HttpResponseProxy`` object which
    contains a template-useable interface for fetching the response
    code, headers, and content. Examples::

        {% ifequal response.status_code "200" %}
        {{ response }}
        {% endifequal %}

    ``HttpResponseProxy`` behaves is a dict-like object. The http
    response headers are set as the dict items and their names are
    transposed for use in templates, i.e. 'Content-type' becomes
    'content_type'. For example::

        {% ifequal response.content_type "text/html" %}
        {% endifequal %}
    """
    bits = token.contents.split(' ')
    if len(bits) < 2:
        raise TemplateSyntaxError(
            "'%s' takes at least one argument (path to a view)" % bits[0])
    view_func = bits[1]
    args = []
    kwargs = {}
    asvar = None
    in_get_query = False
    get_query = datastructures.MultiValueDict()
        
    if len(bits) > 2:
        bits = iter(bits[2:])
        for bit in bits:
            if bit == 'get':
                in_get_query = True

            if bit == 'as':
                asvar = bits.next()
                break
            elif in_get_query:
                in_get_query = True
                for bit in bits:
                    if bit == 'as':
                        asvar = bits.next()
                        break
                    for arg in bit.split(','):
                        k, v = arg.split('=', 1)
                        get_query.appendlist(
                            k.strip(), parser.compile_filter(v))
            else:
                for arg in bit.split(","):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        args.append(parser.compile_filter(arg))
    return ViewSsiNode(view_func, args, kwargs, get_query, asvar)


viewssi = register.tag(viewssi)
