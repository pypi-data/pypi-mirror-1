# -*- coding: utf-8 -*-

import functools
import re

import django.http


STATUSES = {
    
    'INFORMATIONAL': {
        'CONTINUE': 100,
        'SWITCHING_PROTOCOLS': 101,
    },
    
    'SUCCESSFUL': {
        'OK': 200,
        'CREATED': 201,
        'ACCEPTED': 202,
        'NON_AUTHORITATIVE_INFORMATION': 203,
        'NO_CONTENT': 204,
        'RESET_CONTENT': 205,
        'PARTIAL_CONTENT': 206,
    },
    
    'REDIRECTION': {
        'MULTIPLE_CHOICES': 300,
        'MOVED_PERMANENTLY': 301,
        'FOUND': 302,
        'SEE_OTHER': 303,
        'NOT_MODIFIED': 304,
        'USE_PROXY': 305,
        # 306 is reserved, but unused.
        'TEMPORARY_REDIRECT': 307,
    },
    
    'CLIENT_ERROR': {
        'BAD_REQUEST': 400,
        'UNAUTHORIZED': 401,
        'PAYMENT_REQUIRED': 402,
        'FORBIDDEN': 403,
        'NOT_FOUND': 404,
        'METHOD_NOT_ALLOWED': 405,
        'NOT_ACCEPTABLE': 406,
        'PROXY_AUTHENTICATION_REQUIRED': 407,
        'REQUEST_TIMEOUT': 408,
        'CONFLICT': 409,
        'GONE': 410,
        'LENGTH_REQUIRED': 411,
        'PRECONDITION_FAILED': 412,
        'REQUEST_ENTITY_TOO_LARGE': 413,
        'REQUEST_URI_TOO_LONG': 414,
        'UNSUPPORTED_MEDIA_TYPE': 415,
        'REQUESTED_RANGE_NOT_SATISFIABLE': 416,
        'EXPECTATION_FAILED': 417,
    },
    
    'SERVER_ERROR': {
        'INTERNAL_SERVER_ERROR': 500,
        'NOT_IMPLEMENTED': 501,
        'BAD_GATEWAY': 502,
        'SERVICE_UNAVAILABLE': 503,
        'GATEWAY_TIMEOUT': 504,
        'HTTP_VERSION_NOT_SUPPORTED': 505,
    },

}


# So that `module.SERVER_ERROR` => dictionary of server error status codes.
vars().update(STATUSES)


_REPLACEMENTS = {
    'Non Authoritative': 'Non-Authoritative',
    'Http': 'HTTP',
    'Ok': 'OK',
    'Uri': 'URI',
}

_HTTP_SUPERS = {
    301: django.http.HttpResponsePermanentRedirect,
    302: django.http.HttpResponseRedirect,
    304: django.http.HttpResponseNotModified,
    400: django.http.HttpResponseBadRequest,
    403: django.http.HttpResponseForbidden,
    404: django.http.HttpResponseNotFound,
    405: django.http.HttpResponseNotAllowed,
    410: django.http.HttpResponseGone,
    500: django.http.HttpResponseServerError
}


def format_status(status):
    """Take a 'STATUS_CODE' and return a 'Status Code'."""
    
    formatted = status.replace('_', ' ').title()
    for replacement in _REPLACEMENTS.items():
        formatted = formatted.replace(*replacement)
    return formatted


def clean_var_name(string):
    """Clean a string to form a valid Python variable name."""
    
    return re.sub(r'[^A-Za-z0-9_]', '', string)


def build_response_class(class_name, status, code):
    """Build a `HttpResponse` subclass for a given status code."""
    
    def new_init(self, *args, **kwargs):
        kwargs.setdefault('status', code)
        super(type(self), self).__init__(*args, **kwargs)
    
    superclass = _HTTP_SUPERS.get(code, django.http.HttpResponse)
    docstring = "HttpResponse class for '%d %s' responses." % (code, format_status(status))
    attrs = {'__init__': new_init, '__doc__': docstring}
    return type(class_name, (superclass,), attrs)


for status_class in STATUSES:
    for status, code in STATUSES[status_class].items():
        response_class_name = clean_var_name(format_status(status))
        vars()[response_class_name] = build_response_class(response_class_name, status, code)


# Clean up the namespace.
del build_response_class
del code
del response_class_name
del status
del status_class
del _REPLACEMENTS
