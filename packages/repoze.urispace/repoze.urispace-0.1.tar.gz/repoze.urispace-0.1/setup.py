##############################################################################
#
# Copyright (c) 2008 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'docs', 'index.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
VERSION_TXT = os.path.join(here, 'repoze', 'urispace', 'version.txt')
version = open(VERSION_TXT).readline().rstrip()

setup(name='repoze.urispace',
      version=version,
      description='Library / middleware for URI-based assertions',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        ],
      keywords='web wsgi zope URISpace',
      author="Agendaless Consulting",
      author_email="repoze-dev@lists.repoze.org",
      url="http://www.repoze.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['repoze'],
      zip_safe=False,
      tests_require = ['Paste',
                       'zope.interface',
                        'elementtree',
                      ],
      install_requires=['Paste',
                        'zope.interface',
                        'setuptools',
                        'elementtree',
                       ],
      test_suite="repoze.urispace.tests",
      entry_points = """\
        [console_scripts]
        uri_test = repoze.urispace.scripts.uri_test:main

        #[paste.filter_app_factory]
        #urispace = repoze.urispace.middleware:make_middleware
      """
      )

