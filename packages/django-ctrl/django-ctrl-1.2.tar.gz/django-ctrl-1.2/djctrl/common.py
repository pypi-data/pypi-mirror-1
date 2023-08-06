# -*- coding: utf-8 -*-

"""Commonly-used controller types."""

import django.http

import core


__all__ = ['AjaxController', 'ResourceController', 'AuthController', 'FormController']


class AjaxController(core.ControllerType):
    
    """
    Controller type which distinguishes between normal and AJAX requests.
    
    If a request is coming through a normal browser or HTTP client, the `web()`
    method is called. If it is an AJAX request, as detected by an HTTP header
    which most popular JavaScript frameworks will send, the `ajax()` method is
    called.
    """
    
    def _view_function(cls, request, *args, **kwargs):
        if request.is_ajax():
            return cls.ajax(request, *args, **kwargs)
        return cls.web(request, *args, **kwargs)


class ResourceController(core.ControllerType):
    
    """
    Controller type which dispatches on the HTTP request method.
    
    Valid methods include 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE',
    'OPTIONS' and 'CONNECT'. These may be changed by overriding the
    ``VALID_METHODS`` class attribute, setting it to a list of valid HTTP
    methods.
    
    When a request arrives, the controller does this:
        
        * Have I got a method defined on this controller that matches the HTTP
          request method? This is done by case-insensitive search (so method
          names should be lower-case). If so, call that method and return the
          result.
        
        * Otherwise, build a list of the methods defined on this class which are
          *also* present in the list of valid methods. Return this list as part
          of a 405 'Method Not Allowed' response.
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
        if request.method.upper() not in cls.defined_methods():
            return django.http.HttpResponseNotAllowed(cls.defined_methods())
        return cls.get_method(request.method)(request, *args, **kwargs)
    
    @classmethod
    def get_method(cls, http_method):
        """Case-insensitive search for the corresponding controller method."""
        
        for name in dir(cls):
            if name.lower() == http_method.lower():
                return getattr(cls, name)
    
    @classmethod
    def defined_methods(cls):
        """Return a list of methods defined on the ResourceController."""
        
        methods = set()
        for name in dir(cls):
            if name.upper() in cls.VALID_METHODS:
                if getattr(cls, name, NotImplemented) is not NotImplemented:
                    methods.add(name.upper())
        return sorted(list(methods))


class AuthController(core.ControllerType):
    
    """
    Controller type which distinguishes between auth'd and anonymous requests.
    
    The process goes something like this::
        
        Authenticated?
            Active?
                Superuser?
                    Do I have a 'superuser' method?
                        --> superuser()
                Staff?
                    Do I have a 'staff' method?
                        --> staff()
                Do I have an 'active' method?
                    --> active()
            Inactive?
                Do I have an 'inactive' method?
                    --> inactive()
            If all else fails, --> authenticated()
        Otherwise, --> anonymous()
    """
    
    def _view_function(cls, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.user.is_active:
                if request.user.is_superuser:
                    if cls._has_method('superuser'):
                        return cls.superuser(request, *args, **kwargs)
                elif request.user.is_staff:
                    if cls._has_method('staff'):
                        return cls.staff(request, *args, **kwargs)
                if cls._has_method('active'):
                    return cls.active(request, *args, **kwargs)
            else:
                if cls._has_method('inactive'):
                    return cls.inactive(request, *args, **kwargs)
            return cls.authenticated(request, *args, **kwargs)
        else:
            return cls.anonymous(request, *args, **kwargs)


class FormController(core.ControllerType):
    
    """
    Controller type which handles various cases for a single form.
    
    Subclasses should provide a ``form`` class attribute (a Django ``Form``
    *class*, not instance), and optionally a ``form_method`` attribute, which
    defaults to 'POST', specifying the HTTP method by which the form should be
    submitted.
    
    The process goes something like this:
        
        Has data been submitted?
            Is this data valid?
                --> valid()
            --> invalid()
        --> unbound()
    
    These methods will be called with form instances as the second argument
    (after ``request``, before the URLconf arguments).
    """
    
    form_method = 'POST'
    form = NotImplemented
    
    def _view_function(cls, request, *args, **kwargs):
        submitted_data = getattr(request, cls.form_method, {})
        if not submitted_data:
            return cls.unbound(request, cls.form(), *args, **kwargs)
        
        form_instance = cls.form(submitted_data, request.FILES)
        if form_instance.is_valid():
            return cls.valid(request, form_instance, *args, **kwargs)
        
        return cls.invalid(request, form_instance, *args, **kwargs)
