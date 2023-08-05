"""Decorators useful with Zope browser views."""

import simplejson

def json(func=None, **decorator_kwargs):
    """Simple JSON decorator that generates a JSON formatted string of the
    output of the decorated function.
    """
    if func is not None:
        # We got a function, return a decorated version of it
        def json_decor(*args, **kwargs):
            return simplejson.dumps(func(*args, **kwargs), **decorator_kwargs)

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
        return func(self, *args, **kwargs)
    disable_cache.__doc__ = func.__doc__
    disable_cache.__dict__ = func.__dict__
    disable_cache.__module__ = func.__module__
    disable_cache.__name__ = func.__name__
    return disable_cache
