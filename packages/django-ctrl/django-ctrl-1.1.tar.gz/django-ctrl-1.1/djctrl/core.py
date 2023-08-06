# -*- coding: utf-8 -*-

"""Main classes used to define controller types."""

import inspect

__all__ = ['ControllerType']


class ControllerTypeMeta(type):
    
    """Metaclass for controller types which makes methods static by default."""
    
    def __new__(metacls, name, bases, attrs):
        for attr, value in attrs.items():
            # At this point, `attrs` will contain just functions, not
            # fully-fledged methods. `inspect.isfunction()` will not be true
            # for explicitly-decorated static- or class-methods.
            if inspect.isfunction(value) and not attr == '_view_function':
                attrs[attr] = staticmethod(value)
            
            # Correctly handle undecorated `_view_function()` definitions.
            elif attr == '_view_function':
                if not isinstance(value, (classmethod, staticmethod)):
                    attrs[attr] = classmethod(value)
        
        return type.__new__(metacls, name, bases, attrs)


class ControllerType(object):
    
    """Superclass for controller types."""
    
    __metaclass__ = ControllerTypeMeta
    
    def __new__(cls, request, *args, **kwargs):
        return cls._view_function(request, *args, **kwargs)
    
    def _view_function(cls):
        raise NotImplementedError
    
    @classmethod
    def _has_method(cls, method_name):
        return has_method(cls, method_name)


def has_method(cls, method_name):
    """Shortcut for determining if a method is defined on a class."""
    
    method = getattr(cls, method_name, None)
    
    if method and (
        inspect.ismethod(method) or
        inspect.isfunction(method) or
        inspect.isclass(method) or
        hasattr(method, '__call__')):
        return True
    
    return False
    
