``browser`` module
==================

This module provides decorators that are useful with Zope 3 browser
views (also usable in Zope 2).

JSON decorator
==============

The JSON decorator uses simplejson_ to encode the return value of the
decorated function as JSON.

.. _simplejson: http://pypi.python.org/pypi/simplejson

    >>> from hexagonit.decorators.browser import json

    >>> @json
    ... def json_callback():
    ...     """JSON callback method."""
    ...     return {'bool' : (True, False) }
    >>> json_callback()
    '{"bool": [true, false]}'

Any keyword arguments passed to the decorator will be passed on to the
``simplejson.dumps`` function.

    >>> @json(sort_keys=True, ensure_ascii=False)
    ... def json_callback():
    ...     """JSON callback method."""
    ...     return {'foo' : None, 'bool' : (True, False), 'ints' : [1,2,3]}
    >>> json_callback()
    u'{"bool": [true, false], "foo": null, "ints": [1, 2, 3]}'
    


HTTP cache disabling decorator
==============================

The ``nocache`` decorator is used for Zope 3 views and sets the
appropriate HTTP headers to disable caching for the results of the
decorated method.

    >>> from hexagonit.decorators.browser import nocache

We'll demonstrate the use of the decorator with a dummy view object.

    >>> class Dummy(object):pass
    >>> class BrowserView(object):
    ...     """Dummy view class that fakes the ``request`` object."""
    ...     def __init__(self):
    ...         self.request = Dummy()
    ...         self.request.response = Dummy()
    ...         self.headers = []
    ...         self.request.response.setHeader = lambda header,value: self.headers.append('%s: %s' % (header, value))
    ...         
    ...     @nocache
    ...     def ajax_callback(self):
    ...         print '\n'.join(self.headers)

    >>> view = BrowserView()
    >>> view.ajax_callback()
    Pragma: no-cache
    Expires: Sat, 1 Jan 2000 00:00:00 GMT
    Cache-Control: no-cache, must-revalidate

It is also possible to use both the ``json`` decorator and the
``nocache`` decorator at the same time.
