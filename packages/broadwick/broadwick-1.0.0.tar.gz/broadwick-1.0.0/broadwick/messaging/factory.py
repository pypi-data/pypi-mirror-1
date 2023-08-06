from cgi import parse_qsl
from urlparse import urlparse
from broadwick.messaging.twistedstomp import StompClient
from broadwick.utils import uriparse

_schemes = {'stomp' : StompClient}
def ClientFactory(uri):
    scheme, authority, path, query, fragment = uriparse.urisplit(uri)

    try:
        factory = _schemes[scheme]
    except ValueError:
        raise ValueError('Scheme %r not supported. Must be one of %r' % (p.scheme, _schemes.keys()))

    user, password, host, port = uriparse.split_authority(authority)
    if port is not None:
        port = int(port)

    if query:
        args = dict(parse_qsl(query))
    else:
        args = {}
    
    return factory(host, port, user, password, **args)

