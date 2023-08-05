# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Decorators and decorator utilities.
"""

import inspect

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

def wrap_func( old_func ):
    """
    Helper utility for decorators to inherit various properties of the
    original procedure being decorated. This is meant to be applied on
    the wrappers that decorators return.

    @param old_func: The wrapper that will take the place of an
    original procedure as part of the decoration process.
    @type old_func: function
    """
    def decorator( new_func ):
        new_func.__name__ = old_func.__name__
        new_func.__dict__ = old_func.__dict__
        new_func.__doc__ = old_func.__doc__
        return new_func
    return decorator

def xmlrpc_safe(func):
    """
    Makes a procedure "XMLRPC-safe" by returning 0 whenever the inner
    function returns C{None}.  This is useful because XMLRPC requires
    return values, and 0 is commonly used when functions don't intend
    to return anything.

    @param func: The procedure to decorate.
    @type func: function
    """
    @wrap_func(func)
    def wrapper(*args,**kwargs):
        result = func(*args,**kwargs)
        if result is not None:
            return result
        else:
            return 0
    return wrapper

def with_file( *file_args, **file_kwargs ):
    """
    Opens a file and ensures that it gets cleaned up. Stopgap solution
    until Python 2.5's (and C{with}) become more prevalent. This should
    be considered deprecated for code that is already using Python 2.5.

    @param file_args, file_kwargs: The arguments to pass to L{file} or L{open}.

    @return: A decorator to be applied on the function using the file.
    @rtype: function
    """
    def decorator( func ):
        @wrap_func( func )
        def wrapper( *args, **kwargs ):
            f = file( *file_args, **file_kwargs )
            try:
                return func( f, *args, **kwargs )
            finally:
                f.close()
        return wrapper
    return decorator

def with_resource( resource ):
    """
    Ensures the resource is finally closed after the decorated function
    executes.

    @param resource: The resource on which to call C{close}.
    @type resource: object
    """
    def decorator( func ):
        @wrap_func( func )
        def wrapper( *args, **kwargs ):
            try:
                return func( resource, *args, **kwargs )
            finally:
                resource.close()
        return wrapper
    return decorator

def run( *args, **kwargs ):
    """
    Runs the decorated function. Useful to avoid this pattern::
    
        @blah
        def f():
            ...
        f(args)

    Instead you can write::

        @run(args)
        @blah
        def f():
            ...

    This makes explicit the one-shot nature of the decorated
    function. This is typically used on "closures" (inner defs).

    @param args, kwargs: The arguments to pass into the decorated
    function

    @return: A decorator to be applied on the one-shot function. The
    decorator simply returns the original function after executing the
    function immediately.
    @rtype: function
    """
    def decorator( func ):
        func( *args, **kwargs )
        return func
    return decorator
