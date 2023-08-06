# -*- coding: utf-8 -*-

import djctrl.core


class AuthController(djctrl.core.ControllerType):
    
    """
    Controller type which distinguishes between auth'd and anonymous requests.
    
    The process for deciding which method to call, in order of precedence, is as
    follows:
    
    *   `superuser()` (if request.user.is_superuser)
    *   `staff()` (if request.user.is_staff)
    *   `active()` (if request.user.is_active)
    *   `inactive()` (if not request.user.is_active)
    *   `authenticated()` (if request.user.is_authenticated())
    *   `anonymous()` otherwise.
    
    Note that you should define at least `authenticated()` and `anonymous()`,
    because then every type of request can be fulfilled.
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
