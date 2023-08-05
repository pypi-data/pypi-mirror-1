"""Decorators useful with Zope browser views."""

import simplejson

def _inject_query_params(args, kwargs):
    """When a view method that takes parameters mapped from the query
    string is decorated, the parameters are lost when the decorated method
    is called. This function tries to access the request and returns a new
    kwargs dictionary that contains the arguments from the query
    string.
    """
    # Try to access the request
    try:
        instance = args[0]
        kw = kwargs.copy()
        kw.update(instance.request.form)
        return kw
    except (AttributeError, IndexError):
        return kwargs

def json(func=None, **decorator_kwargs):
    """Simple JSON decorator that generates a JSON formatted string of the
    output of the decorated function.
    """
    if func is not None:
        # We got a function, return a decorated version of it
        def json_decor(*args, **kwargs):
            kw = _inject_query_params(args, kwargs)
            return simplejson.dumps(func(*args, **kw), **decorator_kwargs)

        json_decor.__doc__ = func.__doc__
        json_decor.__dict__ = func.__dict__
        json_decor.__module__ = func.__module__
        json_decor.__name__ = func.__name__
        return json_decor

    else:
        # We got simplejson arguments, so we need to return a new
        # decorator function. We simply use a recursive call.
        return lambda f: json(f, **decorator_kwargs)


def nocache(func):
    """Decorator that disables HTTP caching by setting the appropriate
    cache headers."""
    def disable_cache(self, *args, **kwargs):
        self.request.response.setHeader('Pragma', 'no-cache')
        self.request.response.setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
        self.request.response.setHeader('Cache-Control', 'no-cache, must-revalidate')
        kw = _inject_query_params(args, kwargs)
        return func(self, *args, **kw)
    disable_cache.__doc__ = func.__doc__
    disable_cache.__dict__ = func.__dict__
    disable_cache.__module__ = func.__module__
    disable_cache.__name__ = func.__name__
    return disable_cache

__all__ = (json, nocache)
