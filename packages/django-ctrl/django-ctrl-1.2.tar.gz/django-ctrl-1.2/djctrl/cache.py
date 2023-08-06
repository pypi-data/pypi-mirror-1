# -*- coding: utf-8 -*-

import operator

import core
import http
import http.responses as res


__all__ = ['CacheController']


def parse_etags(etags_string):
    """Parse out the etags as they appear in an `If-None-Match` HTTP header."""
    
    raw_etags = map(operator.methodcaller('strip'), etags_string.split(','))
    if '*' in raw_etags:
        return '*'
    
    etags = []
    for etag in raw_etags:
        if etag.startswith('W/'):
            etag = etag.replace('W/', '', 1)
        etags.append(etag.strip('"'))
    return etags


def etags_match(calculated_etag, given_etags):
    """Determine whether the calculated etag matches any of the given etags."""
    
    if given_etags == '*':
        return calculated_etag is not None
    return calculated_etag in given_etags


class CacheController(core.ControllerType):
    
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
        if 'HTTP_IF_MATCH' in request.META and cls._has_method('etag'):
            given_etags = parse_etags(request.META['HTTP_IF_MATCH'])
            request.etag = getattr(request, 'etag', None) or cls.etag(request, *args, **kwargs)
            
            if not etags_match(request.etag, given_etags):
                return res.PreconditionFailed()
        
        if 'HTTP_IF_MODIFIED_SINCE' in request.META and cls._has_method('last_modified'):
            try:
                timestamp = http.parse_date(request.META['HTTP_IF_MODIFIED_SINCE'])
            except:
                pass
            else:
                request.last_modified = cls.last_modified(request, *args, **kwargs)
                if request.last_modified <= timestamp:
                    return res.NotModified()
        
        if 'HTTP_IF_NONE_MATCH' in request.META and cls._has_method('etag'):
            given_etags = parse_etags(request.META['HTTP_IF_NONE_MATCH'])
            request.etag = getattr(request, 'etag', None) or cls.etag(request, *args, **kwargs)
            
            if etags_match(request.etag, given_etags):
                if request.method in ('GET', 'HEAD'):
                    return res.NotModified()
                return res.PreconditionFailed()
        
        if 'HTTP_IF_UNMODIFIED_SINCE' in request.META and cls._has_method('last_modified'):
            try:
                timestamp = http.parse_date(request.META['HTTP_IF_UNMODIFIED_SINCE'])
            except:
                pass
            else:
                request.last_modified = cls.last_modified(request, *args, **kwargs)
                if request.last_modified > timestamp:
                    return res.PreconditionFailed()
        
        return cls.view(request, *args, **kwargs)
    
    def view(request, *args, **kwargs):
        return res.NoContent() # No-op.
