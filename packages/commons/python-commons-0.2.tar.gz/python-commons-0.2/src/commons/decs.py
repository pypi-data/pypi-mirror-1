# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Decorators and decorator utilities.

@todo: Move the actual decorators to modules based on their topic.
"""

import functools, inspect, xmlrpclib

def wrap_callable(any_callable, before, after):
    """
    Wrap any callable with before/after calls.

    From the Python Cookbook. Modified to support C{None} for
    C{before} or C{after}.

    @copyright: O'Reilly Media

    @param any_callable: The function to decorate.
    @type any_callable: function
    
    @param before: The pre-processing procedure. If this is C{None}, then no pre-processing will be done.
    @type before: function
    
    @param after: The post-processing procedure. If this is C{None}, then no post-processing will be done.
    @type after: function
    """
    def _wrapped(*a, **kw):
        if before is not None:
            before( )
        try:
            return any_callable(*a, **kw)
        finally:
            if after is not None:
                after( )
    # In 2.4, only: _wrapped.__name__ = any_callable.__name__
    return _wrapped

class GenericWrapper( object ):
    """
    Wrap all of an object's methods with before/after calls. This is
    like a decorator for objects.

    From the I{Python Cookbook}.

    @copyright: O'Reilly Media
    """
    def __init__(self, obj, before, after, ignore=( )):
        # we must set into __dict__ directly to bypass __setattr__; so,
        # we need to reproduce the name-mangling for double-underscores
        clasname = 'GenericWrapper'
        self.__dict__['_%s__methods' % clasname] = {  }
        self.__dict__['_%s__obj' % clasname] = obj
        for name, method in inspect.getmembers(obj, inspect.ismethod):
            if name not in ignore and method not in ignore:
                self.__methods[name] = wrap_callable(method, before, after)
    def __getattr__(self, name):
        try:
            return self.__methods[name]
        except KeyError:
            return getattr(self.__obj, name)
    def __setattr__(self, name, value):
        setattr(self.__obj, name, value)

##########################################################

def xmlrpc_safe(func):
    """
    Makes a procedure "XMLRPC-safe" by returning 0 whenever the inner
    function returns C{None}. This is useful because XMLRPC requires
    return values, and 0 is commonly used when functions don't intend
    to return anything.

    Also, if the procedure returns a boolean, it will be wrapped in
    L{xmlrpclib.Boolean}.

    @param func: The procedure to decorate.
    @type func: function
    """
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        result = func(*args,**kwargs)
        if result is not None:
            if type( result ) == bool:
                return xmlrpclib.Boolean( result )
            else:
                return result
        else:
            return 0
    return wrapper
