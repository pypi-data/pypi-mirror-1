:mod:`repoze.urispace` -- Hierarchical URI-based metadata
*********************************************************

:Author: Tres Seaver
:Version: |version|

.. module:: repoze.urispace
   :synopsis: Hierarchical URI-based metadata

.. topic:: Overview

   :mod:`repoze.urispace` implements the URISpace_ 1.0 spec, as proposed
   to the W3C by Akamai.  Its aim is to provide an implementation of
   that language as a vehicle for asserting declarative metadata about a
   resource based on pattern matching against its URI.

   Once asserted, such metadata can be used to guide the application in
   serving the resource, with possible applciations including:

   - Setting cache control headers.

   - Selecting externally applied themes, e.g. in :mod:`Deliverance`

   - Restricting access, e.g. to emulate Zope's "placeful security."


URISpace Specification
----------------------

The URISpace_ specification provides for matching on the following
portions of a URI:

- scheme

- authority (see URIRFC_)

  o host, including wildcarding (leading only) and port

  o user (if specified in the URI)

- path elements, including nesting and wildcarding, as well as
  parameters, where used.

- query elements, including test for presence or for specific value

- fragments (likely irrelevant for server-side applications)

.. Note:: :mod:`repoze.urispace` does not yet provide support for
   fragment matching.

The asserted metadata can be scalar, or can use RDF Bag and Sequences
to indicate sets or ordered collections.

.. Note:: :mod:`repoze.urispace` does not yet provide support for
   parsing multi-valued assertions using RDF.

Operators are provided to allow for incrementally updating or clearing
the value for a given metadata element.  Specified operators include:

``replace``
    Completely replace any previously asserted value with a new one.
    This is the default operator.

``clear``
    Remove any previously asserted value.

``union``
    Perform a set union: ``old | new``

``intersection``
    Perform a set intersection: ``old & new``

``rev-intersection``
    Perform a set exclusion:  ``old ^ new``

``difference``
    Perform set subtraction:  ``old - new``

``rev-difference``
    Perform set subtraction:  ``new - old``

``prepend``
    Insert  ``new`` values at the head of ``old`` values

``append``
    Insert  ``new`` values at the tail of ``old`` values


Example
-------

Suppose we want to select different Delieverance themes and or rulesets
based on the URI of the resource being themed.  In particular:

- The ``news``, ``lifestyle``, and ``sports`` sections of the site each get
  custom themes, with the homepage and any other sections sharing the
  default theme.

- Within the news section, the ``world``, ``national``, and ``local``
  sections all use a different theme URL (one with the desired color
  scheme name encoded as a query string).

- Within any section, the ``index.html`` page should use a different
  ruleset, than that for stories in that section (whose final path element
  will be ``<slug>.html``): the index page's HTML structured very differently
  from that used for stories.

A URISpace file specifying these policies would look like:

.. include:: examples/dv_news.xml
   :literal:

Given that URISpace file, one can test how given URIs matches using
the ``uri_test`` script::

  $ /path/to/bin/uri_test examples/dv_news.xml \
    http://example.com/ \
    http://example.com/foo \
    http://example.com/news/ \
    http://example.com/news/index.html \
    http://example.com/news/world/index.html \
    http://example.com/sports/ \
    http://example.com/sports/world_series_2008.html 
  ------------------------------------------------------------------------------
  URI: http://example.com/
  ------------------------------------------------------------------------------
  rules = http://static.example.com/rules/default.xml
  theme = http://themes.example.com/default.html

  ------------------------------------------------------------------------------
  URI: http://example.com/foo
  ------------------------------------------------------------------------------
  rules = http://static.example.com/rules/default.xml
  theme = http://themes.example.com/default.html

  ------------------------------------------------------------------------------
  URI: http://example.com/news/
  ------------------------------------------------------------------------------
  rules = http://static.example.com/rules/default.xml
  theme = http://themes.example.com/news.html

  ------------------------------------------------------------------------------
  URI: http://example.com/news/index.html
  ------------------------------------------------------------------------------
  rules = http://static.example.com/rules/default.xml
  theme = http://themes.example.com/news.html

  ------------------------------------------------------------------------------
  URI: http://example.com/news/world/index.html
  ------------------------------------------------------------------------------
  rules = http://static.example.com/rules/default.xml
  theme = http://themes.example.com/news.html?style=world

  ------------------------------------------------------------------------------
  URI: http://example.com/sports/
  ------------------------------------------------------------------------------
  rules = http://static.example.com/rules/default.xml
  theme = http://themes.example.com/sports.html

  ------------------------------------------------------------------------------
  URI: http://example.com/sports/world_series_2008.html
  ------------------------------------------------------------------------------
  rules = http://static.example.com/rules/default.xml
  theme = http://themes.example.com/sports.html


Using a URISpace parser in Python Code
--------------------------------------

Once parsing is complete, the URISpace is available as tree-like object.
The canonical operators to extract metadata for a given URI are:

.. code-block:: python

  from urlparse import urlsplit
  scheme, nethost, path, query, fragment = urlsplit(uri)

  path = path.split('/')
  if len(path) > 1 and path[0] == '':
      path = path[1:]

  info = {'scheme': scheme,
          'nethost': nethost,
          'path': path,
          'query': parse_qs(query, keep_blank_values=1),
          'fragment': fragment,
          }
  operators = urispace.collect(info)
  assertions = {}
  for operator in operators:
      operator.apply(assertions)

At this point, ``assertions`` will contain keys and values for all
operators found while matching against the URI.

Using URISpace as WSGI Middleware
---------------------------------

One application of a URISpace might be to make assertions about the
URI of a WSGI request, in order to allow other parts of the application
to use those assertions.  :mod:`repoze.urispace` provides a component
which can be used as middleware for this purpose.

To configure the middleware in a :mod:`PasteDeploy` config file::

  [filter:urispace]
  use = egg:repoze.urispace#urispace
  file = %{here)s/urispace.xml

You should then be able to add the middleware to your pipeline::

  [pipeline:main]
  pipeline =
    urispace
    your_app

In your application, you can get to the assertions made by the middleware
using the :func:`repoze.urispace.middleware.getAssertions` API, e.g.:

.. code-block:: python

   from repoze.urispace.middleware import getAssertions

   def your_app(environ, start_response):
       assertions = getAssertions(environ)

Development Notes
-----------------


Extending :mod:`repoze.urispace`
++++++++++++++++++++++++++++++++

- Registering custom selectors (TBD)

- Registering operator converters (TBD)


.. toctree::
   :maxdepth: 2

   parser


.. _URISpace: http://www.w3.org/TR/urispace.html

.. _URIRFC: http://www.ietf.org/rfc/rfc2396.txt

.. target-notes:: 
