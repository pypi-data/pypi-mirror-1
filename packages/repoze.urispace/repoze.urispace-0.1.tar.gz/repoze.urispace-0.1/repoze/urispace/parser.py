""" Utilities for parsing an XML serialization of a URISpace.
"""

URISPACE_NS = 'http://www.w3.org/2000/urispace'
EXTENSION_NS = 'http://repoze.org/repoze.urispace/extensions'

def makeURIElement(element):
    factory = _SELECTORS.get(element.tag, _makeOperator)
    return factory(element)

def walkTree(tree, parent=None):
    if parent is None:
        current = _makeTrueSelector(None)
    else:
        current = makeURIElement(tree)
        parent.addChild(current)

    for node in tree:
        walkTree(node, current)

    return current
    

##############  Generic utilities  ####################################
def _urispace_qname(name):
    return '{%s}%s' % (URISPACE_NS, name)

def _extention_qname(name):
    return '{%s}%s' % (EXTENSION_NS, name)

##############  Selector creation machinery  ##########################

_URISPACE_SCHEME_TAG = _urispace_qname('scheme')
_URISPACE_NETHOST_TAG = _urispace_qname('nethost')
_URISPACE_PATH_TAG = _urispace_qname('path')
_URISPACE_QUERY_TAG = _urispace_qname('query')

_EXTENSION_TRUE_TAG = _extention_qname('true')
_EXTENSION_FALSE_TAG = _extention_qname('false')
_EXTENSION_PATH_LAST_TAG = _extention_qname('pathlast')
_EXTENSION_PATH_ANY_TAG = _extention_qname('pathany')

_URISPACE_MATCH_ATTR = _urispace_qname('match')

def _getMatch(element):
    match = element.get(_URISPACE_MATCH_ATTR)
    if match is None:
        raise ValueError("No 'match' attribute in URISpace NS found!")
    return match

def _makeTrueSelector(element):
    from repoze.urispace.selectors import TrueSelector
    return TrueSelector() # no predicate required

def _makeFalseSelector(element):
    from repoze.urispace.selectors import FalseSelector
    return FalseSelector() # no predicate required

def _makeSchemeSelector(element):
    from repoze.urispace.predicates import SchemePredicate
    from repoze.urispace.selectors import PredicateSelector
    predicate = SchemePredicate(_getMatch(element))
    return PredicateSelector(predicate)

def _makeNethostSelector(element):
    from repoze.urispace.predicates import NethostPredicate
    from repoze.urispace.selectors import PredicateSelector
    predicate = NethostPredicate(_getMatch(element))
    return PredicateSelector(predicate)

def _makePathFirstSelector(element):
    from repoze.urispace.predicates import PathFirstPredicate
    from repoze.urispace.selectors import PredicateSelector
    predicate = PathFirstPredicate(_getMatch(element))
    return PredicateSelector(predicate)

def _makePathLastSelector(element):
    from repoze.urispace.predicates import PathLastPredicate
    from repoze.urispace.selectors import PredicateSelector
    predicate = PathLastPredicate(_getMatch(element))
    return PredicateSelector(predicate)

def _makePathAnySelector(element):
    from repoze.urispace.predicates import PathAnyPredicate
    from repoze.urispace.selectors import PredicateSelector
    predicate = PathAnyPredicate(_getMatch(element))
    return PredicateSelector(predicate)

def _makeQuerySelector(element):
    from repoze.urispace.predicates import QueryKeyPredicate
    from repoze.urispace.predicates import QueryValuePredicate
    from repoze.urispace.selectors import PredicateSelector
    match = _getMatch(element)
    if '=' in match:
        predicate = QueryValuePredicate(match)
    else:
        predicate = QueryKeyPredicate(match)
    return PredicateSelector(predicate)
    
_SELECTORS = {
    _EXTENSION_TRUE_TAG:        _makeTrueSelector,
    _EXTENSION_FALSE_TAG:       _makeFalseSelector,
    _URISPACE_SCHEME_TAG:       _makeSchemeSelector,
    _URISPACE_NETHOST_TAG:      _makeNethostSelector,
    _URISPACE_PATH_TAG:         _makePathFirstSelector,
    _EXTENSION_PATH_LAST_TAG:   _makePathLastSelector,
    _EXTENSION_PATH_ANY_TAG:    _makePathAnySelector,
    _URISPACE_QUERY_TAG:        _makeQuerySelector,
}

##############  Operator creation machinery  ##########################

_URISPACE_OP_ATTR = _urispace_qname('op')

def _makeClearOperator(key, value):
    from repoze.urispace.operators import ClearOperator
    return ClearOperator(key)

def _makeReplaceOperator(key, value):
    from repoze.urispace.operators import ReplaceOperator
    return ReplaceOperator(key, value)

def _makeUnionOperator(key, value):
    from repoze.urispace.operators import UnionOperator
    raise NotImplementedError

def _makeIntersectionOperator(key, value):
    from repoze.urispace.operators import IntersectionOperator
    raise NotImplementedError

def _makeRevIntersectionOperator(key, value):
    from repoze.urispace.operators import RevIntersectionOperator
    raise NotImplementedError

def _makeDifferenceOperator(key, value):
    from repoze.urispace.operators import DifferenceOperator
    raise NotImplementedError

def _makeRevDifferenceOperator(key, value):
    from repoze.urispace.operators import RevDifferenceOperator
    raise NotImplementedError

def _makePrependOperator(key, value):
    from repoze.urispace.operators import PrependOperator
    return PrependOperator(key, value)

def _makeAppendOperator(key, value):
    from repoze.urispace.operators import AppendOperator
    return AppendOperator(key, value)

_OPERATORS = {
    'replace':          _makeReplaceOperator,
    'clear':            _makeClearOperator,
    'union':            _makeClearOperator,
    'intersetion':      _makeClearOperator,
    'rev-intersetion':  _makeClearOperator,
    'difference':       _makeClearOperator,
    'rev-difference':   _makeClearOperator,
    'prepend':          _makePrependOperator,
    'append':           _makeAppendOperator,
}

def _convertSimple(element):
    return (element.tag, element.text)

_CONVERTERS = {
}

def _makeOperator(element):
    op_type = element.get(_URISPACE_OP_ATTR, 'replace')
    operator = _OPERATORS[op_type]

    converter = _CONVERTERS.get(element.tag, _convertSimple)
    key, value = converter(element)

    return operator(key, value)


