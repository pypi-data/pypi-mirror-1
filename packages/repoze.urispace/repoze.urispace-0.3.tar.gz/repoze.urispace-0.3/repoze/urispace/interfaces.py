from zope.interface import Attribute
from zope.interface import Interface

class IURISpaceElement(Interface):
    """ Base for elements making up a URISpace.
    """

class IOperator(IURISpaceElement):
    """ Objects which update a set of assertions.

    o Command pattern
    """
    key = Attribute(u"To what key does the operation pertain?")
    value = Attribute(u"What value is used in this operation?")

    def apply(assertions):
        """ Perform the given operation on a set of assertions.

        o 'assertions' is a mapping of existing key, value pairs.
        """

class ISelector(IURISpaceElement):
    """ Objects which perform matches against URI elements.
    """
    def listChildren():
        """ Return a sequece of elements which are nested within us.

        o All elements will provide IURISpaceElement.
        """

    def addChild(child):
        """ Add child to the list of elements nested within us.

        o Raise ValueError if 'child' is not an IURISpaceElement.
        """

    def collect(uri_info):
        """ Return a sequence of command objects matching the given URI.

        o 'uri_info' is a mapping with keys corresponding to the elements of
          the URI:

          - 'scheme'

          - 'netloc'

          - 'path'

          - 'query'

          - 'fragment'

        o Extensions may add other keys to the mapping, which may be
          used by some ISelector implementations.
        """
