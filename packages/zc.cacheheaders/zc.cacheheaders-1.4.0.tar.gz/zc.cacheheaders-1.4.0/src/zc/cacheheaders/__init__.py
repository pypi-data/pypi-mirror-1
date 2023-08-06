import datetime

date_in_the_past = datetime.datetime(2008, 1, 1)


def get(map, key):
    try:
        return map[key]
    except KeyError:
        return map[key.lower()]


expires_header_format = '%a, %d %b %Y %H:%M:%S GMT'
def set_expires_header(response, expiry_time):
    response.setHeader(
        'Expires', expiry_time.strftime(expires_header_format))


def expires_header_set(headers, expiry_time):
    return get(headers, 'Expires'
        ) == expiry_time.strftime(expires_header_format)


cache_control_format = ('max-age=%d')
def set_cache_control_header(response, minutes=0, seconds=0):
    response.setHeader(
        'Cache-Control',
        cache_control_format % (minutes*60+seconds))


cache_control = 'no-cache'
def disable_caching(response):
    """Disables caching by setting the appropriate cache headers.
    """
    response.setHeader('Cache-Control', cache_control)
    response.setHeader('Pragma', cache_control)
    set_expires_header(response, date_in_the_past)


def caching_disabled(headers):
    result = expires_header_set(headers, date_in_the_past)
    if result:
        result = get(headers, 'Cache-Control') == get(headers, 'Pragma')
    return result


def set_cache_headers(response, minutes=0, seconds=0,
        now=datetime.datetime.utcnow):
    """Enables caching for the specified time by setting cache headers.
    """
    set_cache_control_header(response, minutes, seconds)
    expiry_time = now() + datetime.timedelta(minutes=minutes, seconds=seconds)
    set_expires_header(response, expiry_time)


def cache_headers_set(headers, minutes=0, seconds=0, now=None):
    """Determine whether or not the cache headers are set as given.
    """
    result = True
    if now:
        result = expires_header_set(headers,
            now() + datetime.timedelta(minutes=minutes, seconds=seconds))
    if result:
        result = get(headers, 'Cache-Control') == cache_control_format % (
            minutes*60+seconds)
    return result
