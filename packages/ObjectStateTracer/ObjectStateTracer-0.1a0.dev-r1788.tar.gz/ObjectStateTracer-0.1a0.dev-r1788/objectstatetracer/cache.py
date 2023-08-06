import cherrypy

def request_cache(name):
    """
    Caches only per request.
    """
    try:
        cache = cherrypy.request._ost_cache
    except AttributeError:
        cache = cherrypy.request._ost_cache = dict()
    return cache.setdefault(name, dict())

