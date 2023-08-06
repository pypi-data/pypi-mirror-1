Notes on the :mod:`repoze.urispace` Parse Implementation
********************************************************


Parser Implementation Notes
---------------------------

- The root node of a URISpace is not required to be any particular element,
  nor even in the URISpace namespace (see the first example in "Appendix C",
  of URISpace_, for instance).  The root node is always mapped to a
  :class:`repoze.urispace.selectors.TrueSelector`, for regularity.

- Create selectors for nodes based on their QNames, using a dictionary.
  Create predicates for the selectors (where required) from the
  ``urispace:match`` attribute.

- Any node whose QName does not map to a selector type should be treated as
  an operator.  The default operator type is ``replace``, with overrides
  coming from the ``urispace:op`` attribute.

- The QName of an operator element is used to look up a converter, which
  is then passed the entire element (including children), and must return
  a ``(key, value)`` pair.

- The default converter, used if no other is registered for the operator
  node's QName, return the node's QName as the key, and the node's text as
  the value.

Implementing the Spec
---------------------

- :mod:`repoze.urispace` implements "Scheme Selectors" (section 3.1)
  by combining a selector and a predicate:
  
  - :class:`repoze.urispace.selectors.PredicateSelector`
  - :class:`repoze.urispace.predicates.SchemePredicate`

- Of the "Authority Selectors" (section 3.2), :mod:`repoze.urispace`
  implements the "Host" variant (section 3.2.2) by combining a selector
  and a predicate:

  - :class:`repoze.urispace.selectors.PredicateSelector`
  - :class:`repoze.urispace.predicates.NethostPredicate`

  :mod:`repoze.urispace` does not implement selectors for "Authority Name"
  (section 3.2.1) or "User" (section 3.2.3). at this time.

- :mod:`repoze.urispace` implements "Path Segment Selectors" (section 3.3)
  by combining a selector and a predicate:
  
  - :class:`repoze.urispace.selectors.PredicateSelector`
  - :class:`repoze.urispace.predicates.PathFirstPredicate`

.. Note:: the semantics of the path segment selector in the spec require
   matching only on the first element of the current path.
   :mod:`repoze.urispace` provides extensions which allow for matches on
   the last element of the current path, and for matches on any element 
   of the current path.  See `Extending the Spec`_.

- :mod:`repoze.urispace` implements "Query Selectors" (section 3.4)
  by combining a selector and one of two predicates, based on whether
  the match string includes an ``=``:
  
  - :class:`repoze.urispace.selectors.PredicateSelector`
  - :class:`repoze.urispace.predicates.QueryKeyPredicate`
  - :class:`repoze.urispace.predicates.QueryValuePredicate`


Extending the Spec
------------------

The URISpace_ specification contemplates extension via what it calls
"External Selectors" (see chapter 4).  :mod:`repoze.urispace` in fact
uses this facility to provide additional selectors:

- :mod:`repoze.urispace` implements an extension to "Path Segment"
  selectors (section 3.3), allowing a match on the last element of the
  current path:

  - :class:`repoze.urispace.selectors.PredicateSelector`
  - :class:`repoze.urispace.predicates.PathLastPredicate`

- :mod:`repoze.urispace` implements an extension to "Path Segment"
  selectors (section 3.3), allowing a match on any element of the
  current path:

  - :class:`repoze.urispace.selectors.PredicateSelector`
  - :class:`repoze.urispace.predicates.PathAnyPredicate`

- :class:`repoze.urispace.selectors.TrueSelector` always dispatches
  to contained elements;  its primary use is to represent the root
  node of a URISpace.

- :class:`repoze.urispace.selectors.FalseSelector` never dispatches
  to contained elements.  Its primary use is in "commenting out"
  sections of the URISpace.


.. _URISpace: http://www.w3.org/TR/urispace.html

.. _URIRFC: http://www.ietf.org/rfc/rfc2396.txt
