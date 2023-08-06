""" Implement predicates for URI elements.

o See: http://www.w3.org/TR/urispace.html, chapter 3, "URI Selectors"
"""
import re
from zope.interface import implements
from repoze.urispace.interfaces import IOperator


class SchemePredicate(object):
    """ Test the URI scheme.

    o See: http://www.w3.org/TR/urispace.html, section 3.1, "Scheme".
    """
    def __init__(self, pattern):
        self.pattern = pattern
        self.schemes = pattern.split(' ')

    def __call__(self, info):
        scheme = info.get('scheme')

        if scheme is not None and scheme in self.schemes:
            return True, info

        return False, None


class NethostPredicate(object):
    """ Do match testing against the nethost.

    o See: http://www.w3.org/TR/urispace.html, section 3.2.2, "Host".
    """
    WC_SEARCH = re.compile(r'\?|\*')
    wildcard = None
    port = None

    def __init__(self, pattern):
        self.pattern = pattern
        tokens = self.WC_SEARCH.split(pattern)
        if len(tokens) > 2:
            raise ValueError("Only one wildcard allowed in pattern: %s"
                                % pattern)
        if len(tokens) == 2:
            if tokens[0]:
                raise ValueError("Wildcard must be at start of in pattern: %s"
                                    % pattern)
            wc = self.wildcard = pattern[0]
            host = tokens[1]
            if wc == '?':
                if not host.startswith('.'):
                    raise ValueError("Wildcard '?' must be followed by '.': %s"
                                        % pattern)
                host = host[1:]
            self.host = host
        else:
            self.host = pattern
        tokens = self.host.split(':')
        if len(tokens) > 2:
            raise ValueError("No more than one colon in pattern: %s"
                                % pattern)
        elif len(tokens) == 2:
            self.host = tokens[0]
            self.port = int(tokens[1])

    def __call__(self, info):
        hostport = info.get('nethost')
        if hostport is None:
            return False, None

        host, port = hostport

        if self.wildcard == '*':
            hostmatch = host.endswith(self.host)

        elif self.wildcard == '?':
            first, rest = host.split('.', 1)
            hostmatch = (rest == self.host)

        else:
            hostmatch = (host == self.host)

        if hostmatch and port == self.port:
            return True, info

        return False, None


class PathElementPattern(object):
    """ Glob-like pattern matching for path elements.

    o Only a single '*' is allowed in our pattern, per spec.
    """
    def __init__(self, pattern):
        self.pattern = pattern
        tokens = pattern.split('*')
        if len(tokens) > 2:
            raise ValueError('Only one asterisk allowed: %s' % pattern)
        self.wildcard = len(tokens) == 2
        if self.wildcard:
            self.before, self.after = tokens

    def __call__(self, element):
        """ Return True if element matches our pattern.
        """
        if self.wildcard:
            return (element.startswith(self.before) and
                    element.endswith(self.after))
        return element == self.pattern


class _PathPredicate(object):

    def __init__(self, pattern):
        self.pattern = PathElementPattern(pattern)


class PathFirstPredicate(_PathPredicate):
    """ Implement the semantics of the '<path match="">...</path>' pattern:

    o Test our pattern against the first element of the current path.

    o See: http://www.w3.org/TR/urispace.html, section 3.3, "Path Segment".
    """
    def __call__(self, info):
        path = info.get('path')
        if path and self.pattern(path[0]):
            new_info = info.copy()
            new_info['path'] = path[1:]
            return True, new_info
        return False, None


class PathLastPredicate(_PathPredicate):
    """ Implement the semantics of the '<pathlast="">...</pathlast>' pattern:

    o Test our pattern against the last element of the current path.

    o These semantics are *not* called out in the URISpace spec;  it should
      probably be triggered by an extension element (e.g., <ext:path last="">).
    """
    def __call__(self, info):
        path = info.get('path')
        hit = path and self.pattern(path[-1])
        if hit:
            new_info = info.copy()
            new_info['path'] = ()
            return True, new_info
        return False, None


class PathAnyPredicate(_PathPredicate):
    """ Implement the semantics of the '<pathany="">...</pathany>' pattern:

    o Test our pattern against any element of the current path.

    o These semantics are *not* called out in the URISpace spec;  it should
      probably be triggered by an extension element (e.g., <ext:path any="">).
    """
    def __call__(self, info):
        path = info.get('path')
        if path is not None:
            residue = list(path)
            while residue:
                element, residue = residue[0], residue[1:]
                if self.pattern(element):
                    new_info = info.copy()
                    new_info['path'] = tuple(residue)
                    return True, new_info
        return False, None


class QueryKeyPredicate(object):
    """ Do match testing against the query string.

    o See: http://www.w3.org/TR/urispace.html, section 3.4, "Query".
    """
    def __init__(self, pattern):
        self.pattern = pattern
        if '=' in pattern:
            raise ValueError("pattern must not contain '=': %s" % pattern)

    def __call__(self, info):
        query = info.get('query')
        if query is not None and self.pattern in query:
            return True, info
        return False, None


class QueryValuePredicate(object):
    """ Do match testing against the query string.

    o See: http://www.w3.org/TR/urispace.html, section 3.4, "Query".
    """
    def __init__(self, pattern):
        self.pattern = pattern
        tokens = pattern.split('=')
        if len(tokens) != 2:
            raise ValueError("'pattern' must be 'key=value', was %s"
                                % pattern)
        self.key = tokens[0]
        self.value = tokens[1]

    def __call__(self, info):
        query = info.get('query')
        if query is not None and query.get(self.key, self) == self.value:
            return True, info
        return False, None

