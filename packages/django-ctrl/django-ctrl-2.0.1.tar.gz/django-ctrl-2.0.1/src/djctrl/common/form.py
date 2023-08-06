# -*- coding: utf-8 -*-

import djctrl.core


class FormController(djctrl.core.ControllerType):
    
    """
    Controller type which handles various cases for a single form.
    
    Subclasses should provide a `form` class attribute (a `django.forms.Form`
    *class*, not instance), and optionally a `form_method` attribute, which
    defaults to 'POST', specifying the HTTP method by which the form should be
    submitted.
    
    The process for handling requests is as follows:
    
    *   Check if some data has been submitted via the specified form method. If
        not, call the `unbound()` method.
    
    *   If data has been submitted, instantiate the form attached to this
        `FormController`, and check if it's valid (via
        `form_instance.is_valid()`). If it is, call the `valid()` method on this
        controller.
    
    *   Otherwise, call the `invalid()` method on this controller.
    
    Controller methods are always called with the HTTP request, followed by
    a form instance, followed by any additional positional or keyword arguments
    (such as from the URLconf).
    
    An example of what a `FormController` might look like:
    
        class CreateObject(FormController):
            
            form_method = 'POST'
            form = NewObjectForm
            
            def unbound(request, form, *args, **kwargs):
                return render_to_response('app/new_object.html', {
                    'form': form
                })
            
            def invalid(request, form, *args, **kwargs):
                response = CreateObject.unbound(request, form, *args, **kwargs)
                response.status_code = 403 # Forbidden
                return response
            
            def valid(request, form, *args, **kwargs):
                obj = form.save()
                return render_to_response('app/new_object_success.html', {
                    'obj': obj
                })
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
