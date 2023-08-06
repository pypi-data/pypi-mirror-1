# -*- coding: utf-8 -*-

import djctrl.core


class AjaxController(djctrl.core.ControllerType):
    
    """
    Controller type which distinguishes between normal and AJAX requests.
    
    If a request is coming through a normal browser or HTTP client, the `web()`
    method is called. If it is an AJAX request, as detected by an HTTP header
    which most popular JavaScript frameworks will send, the `ajax()` method is
    called.
    
    This uses the `is_ajax()` method on the request, which will check for the
    `X-Requested-With: XMLHttpRequest` header. Most popular JavaScript
    frameworks will send this. For more information, consult
    <http://docs.djangoproject.com/en/dev/ref/request-response/>.
    """
    
    def _view_function(cls, request, *args, **kwargs):
        if request.is_ajax():
            return cls.ajax(request, *args, **kwargs)
        return cls.web(request, *args, **kwargs)
