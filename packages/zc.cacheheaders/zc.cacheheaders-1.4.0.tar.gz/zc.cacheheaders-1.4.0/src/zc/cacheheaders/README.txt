zc.cacheheaders
===============

This is a utility egg that provides functions for setting the exires header, to
disable caching, and to enable caching to a specified time.  We'll begin by
creating a response, and viewing its headers.

    >>> import pprint
    >>> import zope.publisher.http
    >>> response = zope.publisher.http.HTTPResponse()
    >>> pprint.pprint(response.getHeaders())
    [('X-Powered-By', 'Zope (www.zope.org), Python (www.python.org)')]

Now we'll test stuff.

    >>> import zc.cacheheaders
    >>> zc.cacheheaders.set_expires_header(
    ...     response, zc.cacheheaders.date_in_the_past)
    >>> pprint.pprint(response.getHeaders())
    [('X-Powered-By', 'Zope (www.zope.org), Python (www.python.org)'),
     ('Expires', 'Tue, 01 Jan 2008 00:00:00 GMT')]
    >>> zc.cacheheaders.expires_header_set(
    ...     dict(response.getHeaders()), zc.cacheheaders.date_in_the_past)
    True

    >>> response = zope.publisher.http.HTTPResponse()
    >>> zc.cacheheaders.disable_caching(response)
    >>> pprint.pprint(response.getHeaders())
    [('X-Powered-By', 'Zope (www.zope.org), Python (www.python.org)'),
     ('Expires', 'Tue, 01 Jan 2008 00:00:00 GMT'),
     ('Pragma', 'no-cache'),
     ('Cache-Control', 'no-cache')]
    >>> zc.cacheheaders.caching_disabled(dict(response.getHeaders()))
    True

    >>> response = zope.publisher.http.HTTPResponse()
    >>> zc.cacheheaders.set_cache_headers(
    ...     response, 3, now=lambda:zc.cacheheaders.date_in_the_past)
    >>> pprint.pprint(response.getHeaders())
    [('X-Powered-By', 'Zope (www.zope.org), Python (www.python.org)'),
     ('Expires', 'Tue, 01 Jan 2008 00:03:00 GMT'),
     ('Cache-Control', 'max-age=180')]
    >>> zc.cacheheaders.cache_headers_set(
    ...     dict(response.getHeaders()),
    ...     3,
    ...     now=lambda:zc.cacheheaders.date_in_the_past)
    True

We can just set the cache control headers (without creating a Expires header).

    >>> response = zope.publisher.http.HTTPResponse()
    >>> zc.cacheheaders.set_cache_control_header(
    ...     response, minutes=3)
    >>> pprint.pprint(response.getHeaders())
    [('X-Powered-By', 'Zope (www.zope.org), Python (www.python.org)'),
     ('Cache-Control', 'max-age=180')]

Sometimes you want more control over the cache interval than just "minutes" can
afford.  In those situations you can use a new invention called "seconds":

    >>> response = zope.publisher.http.HTTPResponse()
    >>> zc.cacheheaders.set_cache_headers(
    ...     response, seconds=10, now=lambda:zc.cacheheaders.date_in_the_past)
    >>> pprint.pprint(response.getHeaders())
    [('X-Powered-By', 'Zope (www.zope.org), Python (www.python.org)'),
     ('Expires', 'Tue, 01 Jan 2008 00:00:10 GMT'),
     ('Cache-Control', 'max-age=10')]
    >>> zc.cacheheaders.cache_headers_set(
    ...     dict(response.getHeaders()),
    ...     seconds=10,
    ...     now=lambda:zc.cacheheaders.date_in_the_past)
    True
