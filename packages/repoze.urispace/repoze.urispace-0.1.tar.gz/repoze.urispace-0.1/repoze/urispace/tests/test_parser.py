import unittest

class Test_makeURIElement(unittest.TestCase):

    def _makeQName(self, name, ns=None):
        if ns is None:
            return name
        return '{%s}%s' % (ns, name)

    def _makeURISpaceQName(self, name):
        from repoze.urispace.parser import URISPACE_NS
        return self._makeQName(name, URISPACE_NS)

    def _makeExtensionQName(self, name):
        from repoze.urispace.parser import EXTENSION_NS
        return self._makeQName(name, EXTENSION_NS)

    def _makeNSAttrs(self, ns, attrs=None, **kw):
        if attrs is None:
            attrs = {}
        for k, v in kw.items():
            qname = self._makeQName(k, ns)
            attrs[qname] = v
        return attrs

    def _makeURISpaceAttrs(self, attrs=None, **kw):
        from repoze.urispace.parser import URISPACE_NS
        return self._makeNSAttrs(URISPACE_NS, attrs, **kw)

    def _makeElement(self, qname, attrs):
        from elementtree.ElementTree import Element
        return Element(qname, attrs)

    def _callFUT(self, element):
        from repoze.urispace.parser import makeURIElement
        return makeURIElement(element)

    def test_simple_tag_no_op_attr(self):
        from repoze.urispace.operators import ReplaceOperator
        source = self._makeElement('simple', {})
        source.text = 'Simple'
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, ReplaceOperator))
        self.assertEqual(derived.key, 'simple')
        self.assertEqual(derived.value, 'Simple')

    def test_simple_tag_w_clear(self):
        from repoze.urispace.operators import ClearOperator
        attrs = self._makeURISpaceAttrs(op='clear')
        source = self._makeElement('simple', attrs)
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, ClearOperator))
        self.assertEqual(derived.key, 'simple')
        self.assertEqual(derived.value, None)

    def test_simple_tag_w_replace(self):
        from repoze.urispace.operators import ReplaceOperator
        attrs = self._makeURISpaceAttrs(op='replace')
        source = self._makeElement('simple', attrs)
        source.text = 'Simple'
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, ReplaceOperator))
        self.assertEqual(derived.key, 'simple')
        self.assertEqual(derived.value, 'Simple')

    def TBD_test_simple_tag_w_union(self):
        from repoze.urispace.operators import UnionOperator
        attrs = self._makeURISpaceAttrs(op='union')
        source = self._makeElement('simple', attrs)
        source.text = 'Simple'  # XXX need RDF bag
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, UnionOperator))
        self.assertEqual(derived.key, 'simple')
        self.assertEqual(derived.value, 'Simple')

    def TBD_test_simple_tag_w_intersection(self):
        from repoze.urispace.operators import IntersectionOperator
        attrs = self._makeURISpaceAttrs(op='intersection')
        source = self._makeElement('simple', attrs)
        source.text = 'Simple'  # XXX need RDF bag
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, IntersectionOperator))
        self.assertEqual(derived.key, 'simple')
        self.assertEqual(derived.value, 'Simple')

    def TBD_test_simple_tag_w_rev_intersection(self):
        from repoze.urispace.operators import RevIntersectionOperator
        attrs = self._makeURISpaceAttrs(op='rev-intersection')
        source = self._makeElement('simple', attrs)
        source.text = 'Simple'  # XXX need RDF bag
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, RevIntersectionOperator))
        self.assertEqual(derived.key, 'simple')
        self.assertEqual(derived.value, 'Simple')

    def TBD_test_simple_tag_w_difference(self):
        from repoze.urispace.operators import DifferenceOperator
        attrs = self._makeURISpaceAttrs(op='difference')
        source = self._makeElement('simple', attrs)
        source.text = 'Simple'  # XXX need RDF bag
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, DifferenceOperator))
        self.assertEqual(derived.key, 'simple')
        self.assertEqual(derived.value, 'Simple')

    def TBD_test_simple_tag_w_rev_difference(self):
        from repoze.urispace.operators import RevDifferenceOperator
        attrs = self._makeURISpaceAttrs(op='rev-difference')
        source = self._makeElement('simple', attrs)
        source.text = 'Simple'  # XXX need RDF bag
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, RevDifferenceOperator))
        self.assertEqual(derived.key, 'simple')
        self.assertEqual(derived.value, 'Simple')

    def test_simple_tag_w_prepend(self):
        from repoze.urispace.operators import PrependOperator
        attrs = self._makeURISpaceAttrs(op='prepend')
        source = self._makeElement('simple', attrs)
        source.text = 'Simple'
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, PrependOperator))
        self.assertEqual(derived.key, 'simple')
        self.assertEqual(derived.value, 'Simple')

    def test_simple_tag_w_append(self):
        from repoze.urispace.operators import AppendOperator
        attrs = self._makeURISpaceAttrs(op='append')
        source = self._makeElement('simple', attrs)
        source.text = 'Simple'
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, AppendOperator))
        self.assertEqual(derived.key, 'simple')
        self.assertEqual(derived.value, 'Simple')

    def test_true_selector_tag(self):
        from repoze.urispace.selectors import TrueSelector
        qname = self._makeExtensionQName('true')
        source = self._makeElement(qname, {})
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, TrueSelector))

    def test_false_selector_tag(self):
        from repoze.urispace.selectors import FalseSelector
        qname = self._makeExtensionQName('false')
        source = self._makeElement(qname, {})
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, FalseSelector))

    def test_scheme_selector_tag_no_match_attr_raises(self):
        qname = self._makeURISpaceQName('scheme')
        source = self._makeElement(qname, {})
        self.assertRaises(ValueError, self._callFUT, source)

    def test_scheme_selector_tag_w_match_attr(self):
        from repoze.urispace.predicates import SchemePredicate
        from repoze.urispace.selectors import PredicateSelector
        qname = self._makeURISpaceQName('scheme')
        attrs = self._makeURISpaceAttrs(match='http')
        source = self._makeElement(qname, attrs)
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, PredicateSelector))
        self.failUnless(isinstance(derived.predicate, SchemePredicate))
        self.assertEqual(derived.predicate.pattern, 'http')

    def test_nethost_selector_tag_no_match_attr_raises(self):
        qname = self._makeURISpaceQName('nethost')
        source = self._makeElement(qname, {})
        self.assertRaises(ValueError, self._callFUT, source)

    def test_nethost_selector_tag_w_match_attr(self):
        from repoze.urispace.predicates import NethostPredicate
        from repoze.urispace.selectors import PredicateSelector
        qname = self._makeURISpaceQName('nethost')
        attrs = self._makeURISpaceAttrs(match='www.example.com')
        source = self._makeElement(qname, attrs)
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, PredicateSelector))
        self.failUnless(isinstance(derived.predicate, NethostPredicate))
        self.assertEqual(derived.predicate.pattern, 'www.example.com')

    def test_path_selector_tag_no_match_attr_raises(self):
        qname = self._makeURISpaceQName('path')
        source = self._makeElement(qname, {})
        self.assertRaises(ValueError, self._callFUT, source)

    def test_path_selector_tag_w_match_attr(self):
        from repoze.urispace.predicates import PathFirstPredicate
        from repoze.urispace.selectors import PredicateSelector
        qname = self._makeURISpaceQName('path')
        attrs = self._makeURISpaceAttrs(match='index.html')
        source = self._makeElement(qname, attrs)
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, PredicateSelector))
        self.failUnless(isinstance(derived.predicate, PathFirstPredicate))
        self.assertEqual(derived.predicate.pattern.pattern, 'index.html')

    def test_pathlast_selector_tag_no_match_attr_raises(self):
        qname = self._makeExtensionQName('pathlast')
        source = self._makeElement(qname, {})
        self.assertRaises(ValueError, self._callFUT, source)

    def test_pathlast_selector_tag_w_match_attr(self):
        from repoze.urispace.predicates import PathLastPredicate
        from repoze.urispace.selectors import PredicateSelector
        qname = self._makeExtensionQName('pathlast')
        attrs = self._makeURISpaceAttrs(match='index.html')
        source = self._makeElement(qname, attrs)
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, PredicateSelector))
        self.failUnless(isinstance(derived.predicate, PathLastPredicate))
        self.assertEqual(derived.predicate.pattern.pattern, 'index.html')

    def test_pathany_selector_tag_no_match_attr_raises(self):
        qname = self._makeExtensionQName('pathany')
        source = self._makeElement(qname, {})
        self.assertRaises(ValueError, self._callFUT, source)

    def test_pathany_selector_tag_w_match_attr(self):
        from repoze.urispace.predicates import PathAnyPredicate
        from repoze.urispace.selectors import PredicateSelector
        qname = self._makeExtensionQName('pathany')
        attrs = self._makeURISpaceAttrs(match='foobar')
        source = self._makeElement(qname, attrs)
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, PredicateSelector))
        self.failUnless(isinstance(derived.predicate, PathAnyPredicate))
        self.assertEqual(derived.predicate.pattern.pattern, 'foobar')

    def test_query_selector_tag_no_match_attr_raises(self):
        qname = self._makeURISpaceQName('query')
        source = self._makeElement(qname, {})
        self.assertRaises(ValueError, self._callFUT, source)

    def test_query_selector_tag_w_match_attr_no_value(self):
        from repoze.urispace.predicates import QueryKeyPredicate
        from repoze.urispace.selectors import PredicateSelector
        qname = self._makeURISpaceQName('query')
        attrs = self._makeURISpaceAttrs(match='foo')
        source = self._makeElement(qname, attrs)
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, PredicateSelector))
        self.failUnless(isinstance(derived.predicate, QueryKeyPredicate))
        self.assertEqual(derived.predicate.pattern, 'foo')

    def test_query_selector_tag_w_match_attr_and_value(self):
        from repoze.urispace.predicates import QueryValuePredicate
        from repoze.urispace.selectors import PredicateSelector
        qname = self._makeURISpaceQName('query')
        attrs = self._makeURISpaceAttrs(match='foo=bar')
        source = self._makeElement(qname, attrs)
        derived = self._callFUT(source)
        self.failUnless(isinstance(derived, PredicateSelector))
        self.failUnless(isinstance(derived.predicate, QueryValuePredicate))
        self.assertEqual(derived.predicate.pattern, 'foo=bar')


class Test_walkTree(unittest.TestCase):

    _old_factory = None

    def tearDown(self):
        if self._old_factory is not None:
            self._setFactory(self._old_factory)

    def _setFactory(self, factory):
        from repoze.urispace import parser as P
        self._old_factory, P.makeURIElement = P.makeURIElement, factory

    def _makeSelector(self, node):
        from zope.interface import directlyProvides
        from repoze.urispace.interfaces import ISelector
        selector = DummySelector(node)
        directlyProvides(selector, ISelector)
        return selector

    def _makeOperator(self, node):
        from zope.interface import directlyProvides
        from repoze.urispace.interfaces import IOperator
        operator = DummyOperator(node)
        directlyProvides(operator, IOperator)
        return operator
        
    def _makeElement(self, node):
        from repoze.urispace.parser import URISPACE_NS
        from repoze.urispace.parser import EXTENSION_NS
        if (URISPACE_NS in node.tag or EXTENSION_NS in node.tag):
            return self._makeSelector(node)
        return self._makeOperator(node)

    def _callFUT(self, tree):
        from repoze.urispace.parser import walkTree
        return walkTree(tree)

    def _parse(self, text):
        from elementtree.ElementTree import fromstring
        return fromstring(text)

    def test_empty_tree(self):
        from repoze.urispace.selectors import TrueSelector
        tree = self._parse(EMPTY_TREE)
        urispace = self._callFUT(tree)
        self.failUnless(isinstance(urispace, TrueSelector))
        self.assertEqual(len(urispace.listChildren()), 0)

    def test_simple_tree(self):
        from repoze.urispace.selectors import TrueSelector
        self._setFactory(self._makeElement)
        tree = self._parse(SIMPLE_TREE)
        urispace = self._callFUT(tree)
        self.failUnless(isinstance(urispace, TrueSelector))
        children = urispace.listChildren()
        self.assertEqual(len(children), 1)
        child = children[0]
        self.failUnless(isinstance(child, DummyOperator))
        self.assertEqual(child.node.tag, 'simple')
        self.assertEqual(child.node.text, 'Simple')

    def test_path_tree(self):

        from repoze.urispace.selectors import TrueSelector
        from repoze.urispace.parser import URISPACE_NS
        self._setFactory(self._makeElement)
        tree = self._parse(PATH_TREE)

        urispace = self._callFUT(tree)

        self.failUnless(isinstance(urispace, TrueSelector))
        children = urispace.listChildren()
        self.assertEqual(len(children), 2)

        operator = children[0]
        self.failUnless(isinstance(operator, DummyOperator))
        self.assertEqual(operator.node.tag, 'simple')
        self.assertEqual(operator.node.text, 'Simple')

        selector = children[1]
        self.failUnless(isinstance(selector, DummySelector))
        self.assertEqual(selector.node.tag, '{%s}path' % URISPACE_NS)

        grands = selector.listChildren()
        self.assertEqual(len(grands), 1)

        grand = grands[0]
        self.failUnless(isinstance(grand, DummyOperator))
        self.assertEqual(grand.node.tag, 'simple')
        self.assertEqual(grand.node.text, 'Overridden')

    def test_nested_path_tree(self):

        from repoze.urispace.selectors import TrueSelector
        from repoze.urispace.parser import URISPACE_NS
        self._setFactory(self._makeElement)
        tree = self._parse(NESTED_PATH_TREE)

        urispace = self._callFUT(tree)

        self.failUnless(isinstance(urispace, TrueSelector))
        children = urispace.listChildren()
        self.assertEqual(len(children), 2)

        operator = children[0]
        self.failUnless(isinstance(operator, DummyOperator))
        self.assertEqual(operator.node.tag, 'simple')
        self.assertEqual(operator.node.text, 'Simple')

        selector = children[1]
        self.failUnless(isinstance(selector, DummySelector))
        self.assertEqual(selector.node.tag, '{%s}path' % URISPACE_NS)

        grands = selector.listChildren()
        self.assertEqual(len(grands), 2)

        nested = grands[0]
        self.failUnless(isinstance(nested, DummySelector))
        self.assertEqual(nested.node.tag, '{%s}scheme' % URISPACE_NS)

        greats = nested.listChildren()
        self.assertEqual(len(greats), 2)

        great = greats[0]
        self.failUnless(isinstance(great, DummyOperator))
        self.assertEqual(great.node.tag, 'simple')
        self.assertEqual(great.node.text, 'Re-overridden')

        another = greats[1]
        self.failUnless(isinstance(another, DummyOperator))
        self.assertEqual(another.node.tag, 'another')
        self.assertEqual(another.node.text, 'Value')

        grand = grands[1]
        self.failUnless(isinstance(grand, DummyOperator))
        self.assertEqual(grand.node.tag, 'simple')
        self.assertEqual(grand.node.text, 'Overridden')


class DummySelector:
    def __init__(self, node):
        self.node = node
        self._added = []
    def addChild(self, child):
        self._added.append(child)
    def listChildren(self):
        return self._added

class DummyOperator:
    def __init__(self, node):
        self.node = node

EMPTY_TREE = """\
<dummy/>
"""

SIMPLE_TREE = """\
<urispace xmlns:uri="http://www.w3.org/2000/urispace">
 <simple>Simple</simple>
</urispace>
"""

PATH_TREE = """\
<urispace xmlns:uri="http://www.w3.org/2000/urispace">
 <simple>Simple</simple>
 <uri:path uri:match="foo">
  <simple>Overridden</simple>
 </uri:path>
</urispace>
"""

NESTED_PATH_TREE = """\
<urispace xmlns:uri="http://www.w3.org/2000/urispace">
 <simple>Simple</simple>
 <uri:path uri:match="foo">
  <uri:scheme uri:match="https">
   <simple>Re-overridden</simple>
   <another>Value</another>
  </uri:scheme>
  <simple>Overridden</simple>
 </uri:path>
</urispace>
"""
