import unittest

class TestIOperatorConformance:

    def test_class_conforms_to_IOperator(self):
        from zope.interface.verify import verifyClass
        from repoze.urispace.interfaces import IOperator
        verifyClass(IOperator, self._getTargetClass())

    def test_instance_conforms_to_IOperator(self):
        from zope.interface.verify import verifyObject
        from repoze.urispace.interfaces import IOperator
        verifyObject(IOperator, self._makeOne())


class ReplaceOperatorTests(unittest.TestCase,
                           TestIOperatorConformance,
                          ):

    def _getTargetClass(self):
        from repoze.urispace.operators import ReplaceOperator
        return ReplaceOperator

    def _makeOne(self, key='dummy', value='dummy'):
        return self._getTargetClass()(key, value)

    def test_apply_empty_assertions(self):
        command = self._makeOne('some_key', 'some value')
        assertions = {}
        command.apply(assertions)
        self.assertEqual(assertions, {'some_key': 'some value'})

    def test_apply_assertions_nomatch(self):
        command = self._makeOne('some_key', 'some value')
        assertions = {'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(assertions, {'some_key': 'some value',
                                      'another_key': 'another value',
                                     })

    def test_apply_assertions_match(self):
        command = self._makeOne('some_key', 'new value')
        assertions = {'some_key': 'some value',
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(assertions, {'some_key': 'new value',
                                      'another_key': 'another value',
                                     })


class ClearOperatorTests(unittest.TestCase,
                         TestIOperatorConformance,
                        ):

    def _getTargetClass(self):
        from repoze.urispace.operators import ClearOperator
        return ClearOperator

    def _makeOne(self, key='dummy'):
        return self._getTargetClass()(key)

    def test_apply_empty_assertions(self):
        command = self._makeOne('some_key')
        assertions = {}
        command.apply(assertions)
        self.assertEqual(assertions, {})

    def test_apply_assertions_nomatch(self):
        command = self._makeOne('some_key')
        assertions = {'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(assertions, {'another_key': 'another value'})

    def test_apply_assertions_match(self):
        command = self._makeOne('some_key')
        assertions = {'some_key': 'some value',
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(assertions, {'another_key': 'another value'})


class UnionOperatorTests(unittest.TestCase,
                         TestIOperatorConformance,
                        ):

    def _getTargetClass(self):
        from repoze.urispace.operators import UnionOperator
        return UnionOperator

    def _makeOne(self, key='dummy', value='value'):
        return self._getTargetClass()(key, value)

    def test_apply_empty_assertions(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {}
        command.apply(assertions)
        self.assertEqual(len(assertions), 1)
        values = sorted(assertions['some_key'])
        self.assertEqual(values, ['bam', 'baz', 'qux'])

    def test_apply_assertions_nomatch(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions['another_key'], 'another value')
        values = sorted(assertions['some_key'])
        self.assertEqual(values, ['bam', 'baz', 'qux'])

    def test_apply_assertions_disjoint(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {'some_key': ['foo', 'bar'],
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions['another_key'], 'another value')
        values = sorted(assertions['some_key'])
        self.assertEqual(values, ['bam', 'bar', 'baz', 'foo', 'qux'])

    def test_apply_assertions_conjoint(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {'some_key': ['foo', 'bar', 'baz'],
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions['another_key'], 'another value')
        values = sorted(assertions['some_key'])
        self.assertEqual(values, ['bam', 'bar', 'baz', 'foo', 'qux'])


class IntersectionOperatorTests(unittest.TestCase,
                                TestIOperatorConformance,
                               ):

    def _getTargetClass(self):
        from repoze.urispace.operators import IntersectionOperator
        return IntersectionOperator

    def _makeOne(self, key='dummy', value='value'):
        return self._getTargetClass()(key, value)

    def test_apply_empty_assertions(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {}
        command.apply(assertions)
        self.assertEqual(len(assertions), 1)
        self.assertEqual(len(assertions['some_key']), 0)

    def test_apply_assertions_nomatch(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions['another_key'], 'another value')
        self.assertEqual(len(assertions['some_key']), 0)

    def test_apply_assertions_disjoint(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {'some_key': ['foo', 'bar'],
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions['another_key'], 'another value')
        self.assertEqual(len(assertions['some_key']), 0)

    def test_apply_assertions_conjoint(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {'some_key': ['foo', 'bar', 'baz'],
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions['another_key'], 'another value')
        self.assertEqual(assertions['some_key'], ['baz'])


class RevIntersectionOperatorTests(unittest.TestCase,
                                   TestIOperatorConformance,
                                  ):

    def _getTargetClass(self):
        from repoze.urispace.operators import RevIntersectionOperator
        return RevIntersectionOperator

    def _makeOne(self, key='dummy', value='value'):
        return self._getTargetClass()(key, value)

    def test_apply_empty_assertions(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {}
        command.apply(assertions)
        self.assertEqual(len(assertions), 1)
        values = sorted(assertions['some_key'])
        self.assertEqual(values, ['bam', 'baz', 'qux'])

    def test_apply_assertions_nomatch(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions['another_key'], 'another value')
        values = sorted(assertions['some_key'])
        self.assertEqual(values, ['bam', 'baz', 'qux'])

    def test_apply_assertions_disjoint(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {'some_key': ['foo', 'bar'],
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions['another_key'], 'another value')
        values = sorted(assertions['some_key'])
        self.assertEqual(values, ['bam', 'bar', 'baz', 'foo', 'qux'])

    def test_apply_assertions_conjoint(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {'some_key': ['foo', 'bar', 'baz'],
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions['another_key'], 'another value')
        values = sorted(assertions['some_key'])
        self.assertEqual(values, ['bam', 'bar', 'foo', 'qux'])


class DifferenceOperatorTests(unittest.TestCase,
                              TestIOperatorConformance,
                             ):

    def _getTargetClass(self):
        from repoze.urispace.operators import DifferenceOperator
        return DifferenceOperator

    def _makeOne(self, key='dummy', value='value'):
        return self._getTargetClass()(key, value)

    def test_apply_empty_assertions(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {}
        command.apply(assertions)
        self.assertEqual(len(assertions), 1)
        self.assertEqual(assertions['some_key'], [])

    def test_apply_assertions_nomatch(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions['another_key'], 'another value')
        self.assertEqual(assertions['some_key'], [])

    def test_apply_assertions_disjoint(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {'some_key': ['foo', 'bar'],
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions['another_key'], 'another value')
        values = sorted(assertions['some_key'])
        self.assertEqual(values, ['bar', 'foo'])

    def test_apply_assertions_conjoint(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {'some_key': ['foo', 'bar', 'baz'],
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions['another_key'], 'another value')
        values = sorted(assertions['some_key'])
        self.assertEqual(values, ['bar', 'foo'])


class RevDifferenceOperatorTests(unittest.TestCase,
                                 TestIOperatorConformance,
                                ):

    def _getTargetClass(self):
        from repoze.urispace.operators import RevDifferenceOperator
        return RevDifferenceOperator

    def _makeOne(self, key='dummy', value='value'):
        return self._getTargetClass()(key, value)

    def test_apply_empty_assertions(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {}
        command.apply(assertions)
        self.assertEqual(len(assertions), 1)
        values = sorted(assertions['some_key'])
        self.assertEqual(values, ['bam', 'baz', 'qux'])

    def test_apply_assertions_nomatch(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions['another_key'], 'another value')
        values = sorted(assertions['some_key'])
        self.assertEqual(values, ['bam', 'baz', 'qux'])

    def test_apply_assertions_disjoint(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {'some_key': ['foo', 'bar'],
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions['another_key'], 'another value')
        values = sorted(assertions['some_key'])
        self.assertEqual(values, ['bam', 'baz', 'qux'])

    def test_apply_assertions_conjoint(self):
        command = self._makeOne('some_key', ['baz', 'bam', 'qux'])
        assertions = {'some_key': ['foo', 'bar', 'baz'],
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(len(assertions), 2)
        self.assertEqual(assertions['another_key'], 'another value')
        values = sorted(assertions['some_key'])
        self.assertEqual(values, ['bam', 'qux'])


class PrependOperatorTests(unittest.TestCase,
                           TestIOperatorConformance,
                          ):

    def _getTargetClass(self):
        from repoze.urispace.operators import PrependOperator
        return PrependOperator

    def _makeOne(self, key='dummy', value='value'):
        return self._getTargetClass()(key, value)

    def test_apply_empty_assertions(self):
        command = self._makeOne('some_key', 'some value')
        assertions = {}
        command.apply(assertions)
        self.assertEqual(assertions, {'some_key': ['some value']})

    def test_apply_assertions_nomatch(self):
        command = self._makeOne('some_key', 'some value')
        assertions = {'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(assertions, {'some_key': ['some value'],
                                      'another_key': 'another value'})

    def test_apply_assertions_override_scalar(self):
        command = self._makeOne('some_key', 'new value')
        assertions = {'some_key': 'old value',
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(assertions, {'some_key': ['new value', 'old value'],
                                      'another_key': 'another value'})

    def test_apply_assertions_scalar_value_appends_list(self):
        command = self._makeOne('some_key', 'new value')
        assertions = {'some_key': ['old value'],
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(assertions, {'some_key': ['new value', 'old value'],
                                      'another_key': 'another value'})

    def test_apply_assertions_sequence_value_extends_list(self):
        command = self._makeOne('some_key', ['new value', 'another value'])
        assertions = {'some_key': ['old value'],
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(assertions, {'some_key': ['new value',
                                                   'another value',
                                                   'old value'],
                                      'another_key': 'another value'})


class AppendOperatorTests(unittest.TestCase,
                          TestIOperatorConformance,
                         ):

    def _getTargetClass(self):
        from repoze.urispace.operators import AppendOperator
        return AppendOperator

    def _makeOne(self, key='dummy', value='value'):
        return self._getTargetClass()(key, value)

    def test_apply_empty_assertions(self):
        command = self._makeOne('some_key', 'some value')
        assertions = {}
        command.apply(assertions)
        self.assertEqual(assertions, {'some_key': ['some value']})

    def test_apply_assertions_nomatch(self):
        command = self._makeOne('some_key', 'some value')
        assertions = {'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(assertions, {'some_key': ['some value'],
                                      'another_key': 'another value'})

    def test_apply_assertions_override_scalar(self):
        command = self._makeOne('some_key', 'new value')
        assertions = {'some_key': 'old value',
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(assertions, {'some_key': ['old value', 'new value'],
                                      'another_key': 'another value'})

    def test_apply_assertions_scalar_value_appends_list(self):
        command = self._makeOne('some_key', 'new value')
        assertions = {'some_key': ['old value'],
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(assertions, {'some_key': ['old value', 'new value'],
                                      'another_key': 'another value'})

    def test_apply_assertions_sequence_value_extends_list(self):
        command = self._makeOne('some_key', ['new value', 'another value'])
        assertions = {'some_key': ['old value'],
                      'another_key': 'another value'}
        command.apply(assertions)
        self.assertEqual(assertions, {'some_key': ['old value',
                                                   'new value',
                                                   'another value'],
                                      'another_key': 'another value'})

