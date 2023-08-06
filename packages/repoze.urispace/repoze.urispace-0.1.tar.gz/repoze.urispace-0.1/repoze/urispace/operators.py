""" Implement commands which mutate a set of value assertions.

o See: http://www.w3.org/TR/urispace.html, chapter 5, "Metadata Operators"
"""
from zope.interface import implements
from repoze.urispace.interfaces import IOperator


class ReplaceOperator:
    """ Updates a given key in the assertion set with a new value.
    """
    implements(IOperator)

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def apply(self, assertions):
        """ See IOperator.
        """
        assertions[self.key] = self.value


class ClearOperator:
    """ Clears a given key from the assertion set.
    """
    implements(IOperator)
    value = None

    def __init__(self, key):
        self.key = key

    def apply(self, assertions):
        """ See IOperator.
        """
        try:
            del assertions[self.key]
        except KeyError:
            pass

class SetOperatorBase:
    """ Base class for operators on sets.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def _setify(self, x):
        if not isinstance(x, set):
            x = set(x)
        return x

    def apply(self, assertions):
        """ See IOperator.
        """
        old = self._setify(assertions.setdefault(self.key, []))
        new = self._setify(self.value)
        assertions[self.key] = list(self._merge(old, new))


class UnionOperator(SetOperatorBase):
    """ Assign the union of the old and new values.
    """
    implements(IOperator)

    def _merge(self, old, new):
        return old | new


class IntersectionOperator(SetOperatorBase):
    """ Assign the intersection of the old and new values.
    """
    implements(IOperator)

    def _merge(self, old, new):
        return old & new


class RevIntersectionOperator(SetOperatorBase):
    """ Assign the symmetric differences (XOR) of the old and new values.
    """
    implements(IOperator)

    def _merge(self, old, new):
        return old ^ new


class DifferenceOperator(SetOperatorBase):
    """ Assign the difference, old - new.
    """
    implements(IOperator)

    def _merge(self, old, new):
        return old - new


class RevDifferenceOperator(SetOperatorBase):
    """ Assign the differences, new - old.
    """
    implements(IOperator)

    def _merge(self, old, new):
        return new - old


class SequenceOperatorBase:
    """ Base class for operators on sequences.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def _listify(self, x):
        if isinstance(x, basestring):
            x = [x]
        if not isinstance(x, list):
            x = list(x)
        return x

    def apply(self, assertions):
        """ See IOperator.
        """
        old = self._listify(assertions.setdefault(self.key, []))
        new = self._listify(self.value)
        assertions[self.key] = self._merge(old, new)

class PrependOperator(SequenceOperatorBase):
    """ Updates a given key in the assertion set, prepending a new value.

    o Promotes existing scalar values to lists.
    """
    implements(IOperator)

    def _merge(self, old, new):
        result = new[:]
        result.extend(old)
        return result

class AppendOperator(SequenceOperatorBase):
    """ Updates a given key in the assertion set, appending a new value.

    o Promotes existing scalar values to lists.
    """
    implements(IOperator)

    def _merge(self, old, new):
        result = old[:]
        result.extend(new)
        return result
