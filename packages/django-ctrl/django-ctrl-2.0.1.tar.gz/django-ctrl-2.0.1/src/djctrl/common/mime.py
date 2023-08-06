# -*- coding: utf-8 -*-

import mimetypes

from django.conf import settings
import djctrl.core
import webob.acceptparse


class MIMEController(djctrl.core.ControllerType):
    
    """
    A controller type to dispatch on the HTTP `Accept` header.
    
    HTTP clients often send `Accept` headers to let the server know what type
    of content they're looking for. This controller allows you to serve
    different types of content for the same resource, based on the `Accept`
    header.
    
    Example
    -------
    
    Simply define different methods to handle different content types:
    
        class MyController(MIMEController):
            
            def xhtml(request):
                return render_to_response('app/template.html', {})
            
            def json(request):
                response = django.http.HttpResponse()
                response.content = simplejson.dumps(some_obj)
                response['content-type'] = 'application/json'
                return response
    
    Parsing of the `Accept` header is handled by `webob.acceptparse.MIMEAccept`;
    for more information, see the docs at
    <http://pythonpaste.org/webob/modules/webob.html>.
    
    Content-Type Resolution
    -----------------------
    
    To resolve methods into content-types, the `_get_content_type()` static
    method on this controller is called. Given a name, it should return a valid
    MIME content-type. The default implementation is relatively sound:
    
        >>> MIMEController._get_content_type('json')
        'application/json'
        >>> MIMEController._get_content_type('html')
        'text/html'
        >>> MIMEController._get_content_type('xhtml')
        'application/xhtml+xml'
    
    It uses `mimetypes.guess_type()` to resolve these names into full content-
    type strings. You can also explicitly specify that a function handles a set
    of content-types:
    
        class MyController(MIMEController):
            
            @content_type('application/json')
            @content_type('application/javascript')
            @content_type('text/javascript')
            def ajax(request):
                return JSONResponse(callback='callback', obj={'a': 1, 'b': 2})
    
    The method object will get a `content_types` attribute containing a set of
    mimetypes for which to call the method.
    """
    
    DEFAULT_CONTENT_TYPE = getattr(settings, DEFAULT_CONTENT_TYPE, 'text/html')
    
    def _view_function(cls, request, *args, **kwargs):
        accept = request.META.get('HTTP_ACCEPT', '')
        if not accept:
            accept = cls.DEFAULT_CONTENT_TYPE
        accept = webob.acceptparse.MIMEAccept('Accept', accept)
        
        methods = cls.defined_methods()
        match = accept.best_match(methods)
        if match is not None:
            return methods[match](request, *args, **kwargs)
        
        # If no match was found, return a 406 "Not Acceptable".
        response = django.http.HttpResponse()
        del response['content-type']
        response.status_code = 406 # Not Acceptable
        return response
    
    @staticmethod
    def _get_content_type(name):
        """Resolve a given method name into a MIME content-type."""
        
        # Example: `file.xhtml` => `application/xhtml+xml`.
        return mimetypes.guess_type('file.' + name)[0]
    
    @classmethod
    def _defined_methods(cls):
        """Retrieve a dictionary of Content-Type to method mappings."""
        
        methods = {}
        for name in dir(cls):
            if name.startswith('_'):
                continue
            
            method = getattr(cls, name)
            if hasattr(method, 'content_types'):
                content_types = method.content_types
            else:
                # Example: `xhtml` => `application/xhtml+xml`.
                content_types = filter(None, [cls.get_content_type(name)])
            
            if content_types:
                for content_type in content_types:
                    methods[content_type] = getattr(cls, name)
        return methods


def content_type(content_type_):
    """Declare that a decorated function produces a given content type."""
    
    def decorator(function):
        if not hasattr(function, 'content_types'):
            function.content_types = set()
        function.content_types.add(content_type_)
        return function
    return decorator
