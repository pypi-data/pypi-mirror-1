``repoze.urispace`` README
==========================

``repoze.urispace`` implements the URISpace_ 1.0 spec, as proposed
to the W3C by Akamai.  Its aim is to provide an implementation of
that language as a vehicle for asserting declarative metadata about a
resource based on pattern matching against its URI.

Once asserted, such metadata can be used to guide the application in
serving the resource, with possible applciations including:

- Setting cache control headers.

- Selecting externally applied themes, e.g. in ``Deliverance``.

- Restricting access, e.g. to emulate Zope's "placeful security."

Please see the `package docs <http://packages.python.org/repoze.urispace>`_
for detailed documentation.
