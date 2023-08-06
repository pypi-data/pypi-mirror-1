import unittest


class TestISelectorConformance:

    def test_class_conforms_to_ISelector(self):
        from zope.interface.verify import verifyClass
        from repoze.urispace.interfaces import ISelector
        verifyClass(ISelector, self._getTargetClass())

    def test_instance_conforms_to_ISelector(self):
        from zope.interface.verify import verifyObject
        from repoze.urispace.interfaces import ISelector
        verifyObject(ISelector, self._makeOne())


class SelectorTestsBase:

    def _makeOne(self, predicate=None, *args, **kw):
        if predicate is None:
            predicate = DummyPredicate()
        return self._getTargetClass()(predicate, *args, **kw)

    def _makeURISpaceElement(self):
        from zope.interface import implements
        from repoze.urispace.interfaces import IURISpaceElement
        class DummyURISpaceElement:
            implements(IURISpaceElement)
        return DummyURISpaceElement()

    def _makeOperator(self):
        from zope.interface import implements
        from repoze.urispace.interfaces import IOperator
        class DummyOperator:
            implements(IOperator)
        return DummyOperator()

    def test_listChildren_default_empty(self):
        one = self._makeOne()
        self.assertEqual(len(one.listChildren()), 0)

    def test_addChild_sameclass(self):
        one, two = self._makeOne(), self._makeOne()
        one.addChild(two)

        children = one.listChildren()

        self.assertEqual(len(children), 1)
        self.failUnless(children[0] is two)

    def test_addChild_IURISpaceElement(self):
        one = self._makeOne()
        two = self._makeURISpaceElement()
        one.addChild(two)

        children = one.listChildren()

        self.assertEqual(len(children), 1)
        self.failUnless(children[0] is two)

    def test_addChild_not_IURISpaceElement(self):
        one = self._makeOne()
        self.assertRaises(ValueError, one.addChild, object())


class TrueSelectorTests(unittest.TestCase,
                        TestISelectorConformance,
                        SelectorTestsBase,
                       ):

    def _getTargetClass(self):
        from repoze.urispace.selectors import TrueSelector
        return TrueSelector

    def _makeOne(self):
        return self._getTargetClass()()

    def test_collect(self):
        one = self._makeOne()
        command = self._makeOperator()
        one.addChild(command)
        info = {}

        commands = one.collect(info)

        self.assertEqual(len(commands), 1)
        self.failUnless(commands[0] is command)


class FalseSelectorTests(unittest.TestCase,
                         TestISelectorConformance,
                         SelectorTestsBase,
                        ):

    def _getTargetClass(self):
        from repoze.urispace.selectors import FalseSelector
        return FalseSelector

    def _makeOne(self):
        return self._getTargetClass()()

    def test_collect(self):
        one = self._makeOne()
        command = self._makeOperator()
        one.addChild(command)
        info = {}

        commands = one.collect(info)

        self.assertEqual(len(commands), 0)


class PredicateSelectorTests(unittest.TestCase,
                             TestISelectorConformance,
                             SelectorTestsBase,
                            ):

    def _getTargetClass(self):
        from repoze.urispace.selectors import PredicateSelector
        return PredicateSelector

    def test_collect_empty_info_returns_empty(self):
        one = self._makeOne()
        command = self._makeOperator()
        one.addChild(command)
        info = {}
        commands = one.collect(info)
        self.assertEqual(len(commands), 0)

    def test_collect_predicate_miss(self):
        one = self._makeOne()
        command = self._makeOperator()
        one.addChild(command)
        info = {'path': ('foo', 'bar', 'index.html')}
        commands = one.collect(info)
        self.assertEqual(len(commands), 0)

    def test_collect_predicate_miss_nested_not_collected(self):
        one = self._makeOne()
        command = self._makeOperator()
        one.addChild(command)
        two = self._makeOne(DummyPredicate(True))
        command2 = self._makeOperator()
        two.addChild(command2)
        one.addChild(two)
        info = {'path': ('foo', 'bar', 'index.html')}
        commands = one.collect(info)
        self.assertEqual(len(commands), 0)

    def test_collect_predicate_hit_simple(self):
        one = self._makeOne(DummyPredicate(True))
        command = self._makeOperator()
        one.addChild(command)
        info = {'path': ('foo', 'bar', 'index.html')}

        commands = one.collect(info)

        self.assertEqual(len(commands), 1)
        self.failUnless(commands[0] is command)

    def test_collect_nested_hit(self):
        one = self._makeOne(DummyPredicate(True, ('index.html',)))
        command = self._makeOperator()
        one.addChild(command)
        two = self._makeOne(DummyPredicate(True))
        command2 = self._makeOperator()
        two.addChild(command2)
        one.addChild(two)
        info = {'path': ('foo', 'bar', 'index.html')}

        commands = one.collect(info)

        self.assertEqual(len(commands), 2)
        self.failUnless(commands[0] is command)
        self.failUnless(commands[1] is command2)

class DummyPredicate:

    def __init__(self, hit=False, residue=()):
        self.hit = hit
        self.residue = residue

    def __call__(self, path):
        return self.hit, self.residue
