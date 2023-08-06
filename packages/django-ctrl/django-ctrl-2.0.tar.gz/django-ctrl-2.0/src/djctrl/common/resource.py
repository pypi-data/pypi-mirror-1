# -*- coding: utf-8 -*-

import djctrl.core


class ResourceController(djctrl.core.ControllerType):
    
    """
    Controller type which dispatches on the HTTP request method.
    
    The recognized methods are 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE',
    'OPTIONS' and 'CONNECT'. These may be changed by overriding the
    `VALID_METHODS` class attribute, setting it to a list of valid HTTP
    methods.
    
    Incoming requests are handled as follows:
        
    *   A case-insensitive search is performed to find the method on the class
        which corresponds to the request method. So for example, a `GET` request
        will translate into a call to a `get()` method.
    
    *   If no method is found on the controller, a list is built of those
        methods which *are* defined, and this list is returned via a HTTP 405
        "Method Not Allowed" response.
    
    An exemplary resource definition might look like this:
    
        class MyResource(ResourceController):
            
            def get(request):
                return render_to_response('app/new_object.html')
            
            def post(request):
                object = Object(**request.POST)
                object.save()
                return redirect_to('view-object', id=object.id)
    
    This will handle both `GET` and `POST` requests; anything else will result
    in a 405.
    """
    
    VALID_METHODS = set([
        'GET',
        'HEAD',
        'POST',
        'PUT',
        'DELETE',
        'TRACE',
        'OPTIONS',
        'CONNECT'
    ])
    
    def _view_function(cls, request, *args, **kwargs):
        """Dispatch on the request HTTP method."""
        
        return cls._get_method(request.method)(request, *args, **kwargs)
    
    @classmethod
    def _get_method(cls, http_method):
        """Case-insensitive search for the corresponding controller method."""
        
        for name in dir(cls):
            if name.lower() == http_method.lower():
                return getattr(cls, name)
        return cls._fallback
    
    @classmethod
    def _fallback(cls, request, *args, **kwargs):
        return django.http.HttpResponseNotAllowed(cls._defined_methods())
    
    @classmethod
    def _defined_methods(cls):
        """Return a list of methods defined on the ResourceController."""
        
        methods = set()
        for name in dir(cls):
            if name.upper() in cls.VALID_METHODS:
                if getattr(cls, name, NotImplemented) is not NotImplemented:
                    methods.add(name.upper())
        return sorted(list(methods))
