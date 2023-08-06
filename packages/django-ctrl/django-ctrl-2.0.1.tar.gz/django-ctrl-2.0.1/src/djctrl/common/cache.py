# -*- coding: utf-8 -*-

import datetime
import operator
import rfc822 # A very versatile date/time parser.
import time

import django.http
import djctrl.core
import webob.etag


__all__ = ['CacheController']


class CacheController(djctrl.core.ControllerType):
    
    """
    Controller type which allows you to leverage HTTP caching headers.
    
    CacheController handles the boilerplate of dealing with HTTP caching
    headers, via entity tags and modification timestamps, letting you optimise
    your views.
    
    You only need to define three methods: `etag`, `last_modified` and `view`.
    Each should accept the request, and any additional URLconf arguments which
    may be passed.
    
    `etag()` is used to generate an entity tag for a HTTP request. It should
    return a simple string which uniquely identifies the requested resource at
    the current point in time. Possible values include a hash of the complete
    view output, or a hash of the model information which a request refers to.
    
    `last_modified()` should return the last modification timestamp of the
    requested resource. This should be a `datetime.datetime` instance, and will
    be compared against the provided dates in the HTTP request to determine
    whether the representation of the resource needs to be re-sent.
    
    If either of these is calculated prior to the view processing, the value
    returned from the method will be attached to the request object (as `etag`
    or `last_modified`). If you end up carrying out any other computationally
    intensive calculations on the request in either `etag()` or
    `last_modified()`, you can store the results of these calculations on the
    request object, making them available later on for the main view.
    
    `view()` should be your main view (if it is a function, it will
    automatically be made into a static method if you do not specify otherwise).
    If you want to use another controller here, you can just do:
        
        class MyController(djctrl.CacheController):
            class view(djctrl.AjaxController):
                ...
    
    Note that if you do not provide `etag()` or `last_modified()`, the
    controller will simply ignore the relevant HTTP request headers.
    """
    
    def _view_function(cls, request, *args, **kwargs):
        # Some simple shortcut functions.
        def etag():
            if not hasattr(request, 'etag'):
                request.etag = cls.etag(request, *args, **kwargs)
            return request.etag
        
        def last_modified():
            if not hasattr(request, 'last_modified'):
                request.last_modified = cls.last_modified(request, *args, **kwargs)
            return request.last_modified
        
        # The big sequence of conditionals. For more information on the defined
        # behaviour, consult RFC 2616:
        #   <http://www.w3.org/Protocols/rfc2616/rfc2616.html>
        if 'HTTP_IF_MATCH' in request.META and cls._has_method('etag'):
            etags = webob.etag.ETagMatcher.parse(request.META['HTTP_IF_MATCH'])
            if etag() not in etags:
                return precondition_failed()
        
        if 'HTTP_IF_MODIFIED_SINCE' in request.META and cls._has_method('last_modified'):
            try:
                timestamp = parse_date(request.META['HTTP_IF_MODIFIED_SINCE'])
            except:
                pass
            else:
                if last_modified() <= timestamp:
                    return not_modified()
        
        if 'HTTP_IF_NONE_MATCH' in request.META and cls._has_method('etag'):
            etags = webob.etag.ETagMatcher.parse(request.META['HTTP_IF_NONE_MATCH'])
            if etag() in etags:
                if request.method in ('GET', 'HEAD'):
                    return not_modified()
                return precondition_failed()
        
        if 'HTTP_IF_UNMODIFIED_SINCE' in request.META and cls._has_method('last_modified'):
            try:
                timestamp = parse_date(request.META['HTTP_IF_UNMODIFIED_SINCE'])
            except:
                pass
            else:
                if last_modified() > timestamp:
                    return precondition_failed()
        
        return cls.view(request, *args, **kwargs)
    
    def view(request, *args, **kwargs):
        # No-op.
        resp = django.http.HttpResponse(status=204) # No Content.
        del resp['content-type']
        return resp


def precondition_failed():
    resp = django.http.HttpResponse(status=412)
    del resp['content-type']
    return resp


def not_modified():
    resp = django.http.HttpResponse(status=304)
    del resp['content-type']
    return resp


def parse_date(date_string):
    """Parse an RFC822 timestamp string into a datetime object."""
    
    return datetime.datetime(*rfc822.parsedate(date_string)[:7])


def format_date(timestamp):
    """Format a datetime object as an RFC822 timestamp string."""
    
    time_tuple_types = tuple
    if hasattr(time, 'struct_time'):
        time_tuple_types = (tuple, time.struct_time)
    
    if isinstance(timestamp, datetime.datetime):
        timestamp = time.mktime(timestamp.utctimetuple())
    elif isinstance(timestamp, time_tuple_types):
        timestamp = time.mktime(timestamp)
    
    return rfc822.formatdate(timestamp)
