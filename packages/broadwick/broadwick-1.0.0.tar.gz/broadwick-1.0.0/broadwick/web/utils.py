from twisted.web.util import Redirect
from UserList import UserList
import logging


def expose(func=None, **kwargs):
    """ """
    from broadwick.web.resource import StringResource
    return _setup_expose(func, StringResource(**kwargs))

def expose_genshi(func=None, **kwargs):
    from broadwick.web.resource import GenshiResource
    return _setup_expose(func, GenshiResource(**kwargs))

def expose_json(func=None, **kwargs):
    from broadwick.web.resource import JsonResource
    return _setup_expose(func, JsonResource(**kwargs))

def expose_csv(func=None, **kwargs):
    from broadwick.web.resource import CsvResource
    return _setup_expose(func, CsvResource(**kwargs))


def request_param(param):
    def f(func):
        func._request_param = param
        return func
    return f

def auth_roles(func=None, roles=None):
    def _auth(f):
        f._auth_roles = roles
        return f

    if func is not None:
        return _auth(func)
    else:
        return _auth

def _setup_expose(func, resource):
    def _expose(f):
        if not hasattr(func, '_exposed'):
            f._exposed = True
            f._resources = {}
        f._resources[resource.ext] = resource
        return f

    if func is not None:
        return _expose(func)
    else:
        return _expose

def isexposedfunc(f):
    return hasattr(f, '__call__') and hasattr(f, '_exposed')
    
def exposeds(obj):
    for attr in dir(obj):
        value = getattr(obj, attr)
        if isexposedfunc(value):
            yield attr,value

def listen(view, port, *args, **kwargs):
    """Will listen on port and send request to view"""
    from twisted.internet import reactor
    from twisted.web import server
    from page import website

    logging.info('%s available on port %s' % (view.__class__.__name__, port))
    site = website(view, *args, **kwargs)
    reactor.listenTCP(port, site)
    return site

def hasexposed(obj):
    try:
        exposeds(obj).next()
    except StopIteration:
        return False
    return True


def redirect(url):
    raise ReDirectException(url)


class ReDirectException(Exception): 
    def __init__(self, url):
        Exception.__init__(self)
        self.url = url

class AuthenticationException(Exception): 
    pass

