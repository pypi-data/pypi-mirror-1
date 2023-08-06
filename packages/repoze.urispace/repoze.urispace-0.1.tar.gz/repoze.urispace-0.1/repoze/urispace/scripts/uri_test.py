"""\
Usage: uri_test <urispace_filename> uri1 [uri2 [uri3...]]

- 'urispace_filename' names a file containing URISpace XML rules.

- 'uri1' and following are URIs to be tested against the rules.

The script prints out the assertions which match each URI.
"""
from cgi import parse_qs
import sys
from urlparse import urlsplit

def usage(message='', rc=1):
    print __doc__
    if message:
        print ''
        print message
        print ''
    sys.exit(rc)

def parseURISpace(filename):
    from elementtree.ElementTree import parse
    from repoze.urispace.parser import walkTree
    tree = parse(filename)
    return walkTree(tree.getroot())

def main():
    if len(sys.argv) < 3:
        usage('Not enough arguments.')
    urispace = parseURISpace(sys.argv[1])
    for uri in sys.argv[2:]:
        scheme, nethost, path, query, fragment = urlsplit(uri)

        path = path.split('/')
        if len(path) > 1 and path[0] == '':
            path = path[1:]

        info = {'scheme': scheme,
                'nethost': nethost,
                'path': path,
                'query': parse_qs(query, keep_blank_values=1),
                'fragment': fragment,
               }
        operators = urispace.collect(info)
        assertions = {}
        for operator in operators:
            operator.apply(assertions)
        print '-' * 78
        print 'URI:', uri
        print '-' * 78
        for key, value in sorted(assertions.items()):
            print '%s = %s' % (key, value)
        print

