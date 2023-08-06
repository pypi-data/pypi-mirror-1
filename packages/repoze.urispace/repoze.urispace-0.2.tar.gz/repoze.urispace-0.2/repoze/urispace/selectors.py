""" Implement selectors for URI elements.

o Each selector holds a predicate, plus zero or more children

o Children may be selectors, in which case the nesting implies
  "and"-ing of the selection.
  
o Children may also be operators, which are returned by the selector
  during collection if its predicate is satisfied.

o See: http://www.w3.org/TR/urispace.html, chapter 3, "URI Selectors"
"""
from zope.interface import implements
from repoze.urispace.interfaces import IOperator
from repoze.urispace.interfaces import ISelector
from repoze.urispace.interfaces import IURISpaceElement


class SelectorBase(object):
    """ Base for objects which test URIs and return operators.

    o Implements composite pattern to allow nesting.
    """
    def __init__(self, predicate):
        self.predicate = predicate
        self.children = []

    def listChildren(self):
        """ See ISelector.
        """
        return tuple(self.children)

    def addChild(self, child):
        """ See ISelector.
        """
        if not IURISpaceElement.providedBy(child):
            raise ValueError
        self.children.append(child)


class TrueSelector(SelectorBase):
    """ Always fire (e.g., for the root of the URISpace).
    """
    implements(ISelector)
    predicate = lambda *x: True

    def __init__(self):
        self.children = []

    def collect(self, uri_info):
        """ See ISelector.
        """
        commands = []
        commands.extend([x for x in self.children
                            if IOperator.providedBy(x)])
        for child in [x for x in self.children
                            if ISelector.providedBy(x)]:
            commands.extend(child.collect(uri_info))
        return commands


class FalseSelector(SelectorBase):
    """ Never fire (e.g., to comment out part of the URISpace).
    """
    implements(ISelector)
    predicate = lambda *x: False

    def __init__(self):
        self.children = []

    def collect(self, uri_info):
        """ See ISelector.
        """
        return []


class PredicateSelector(SelectorBase):
    """ Do match testing using a generic predicate against URI info.
    """
    implements(ISelector)

    def __init__(self, predicate):
        self.predicate = predicate
        self.children = []

    def collect(self, uri_info):
        """ See ISelector.
        """
        commands = []
        hit, new_info = self.predicate(uri_info)
        if hit:
            commands.extend([x for x in self.children
                                if IOperator.providedBy(x)])
            for child in [x for x in self.children
                                if ISelector.providedBy(x)]:
                commands.extend(child.collect(new_info))
        return commands
