from cgi import parse_qs
from elementtree.ElementTree import parse
from repoze.urispace.parser import walkTree

EKEY = 'repoze.urispace.assertions'

def getAssertions(environ):
    return environ.get(EKEY, {})

def getInfo(environ):
    scheme = environ['wsgi.url_scheme']

    nethost = environ['SERVER_NAME']
    port = environ['SERVER_PORT']
    if scheme == 'HTTP' and port != '80':
        nethost = '%s:%s' % (nethost, port)
    elif scheme == 'HTTPS' and port != '443':
        nethost = '%s:%s' % (nethost, port)

    path = '%s/%s' % (environ['SCRIPT_NAME'], environ['PATH_INFO'])
    path = filter(None, path.split('/'))

    query = parse_qs(environ['QUERY_STRING'], keep_blank_values=1)

    return {'scheme': scheme,
            'nethost': nethost,
            'path': path,
            'query': query,
            'fragment': '',
           }

class URISpaceMiddleware:

    def __init__(self, application, source):
        self.application = application
        tree = parse(source)
        self.urispace = walkTree(tree.getroot())

    def __call__(self, environ, start_response):
        assertions = environ[EKEY] = {}
        info = getInfo(environ)

        operators = self.urispace.collect(info)
        for operator in operators:
            operator.apply(assertions)

        return self.application(environ, start_response)

def make_middleware(app, global_conf, filename=None, stream=None):
    if filename is None:
        if stream is None:
            raise ValueError("Must supply either 'file' or 'stream'.")
        source = stream
    elif stream is not None:
        raise ValueError("Must supply only one of 'file' or 'stream'.")
        source = filename
    return URISpaceMiddleware(app, source)
