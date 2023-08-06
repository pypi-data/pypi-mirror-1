import unittest

class Test_getAssertions(unittest.TestCase):

    def _callFUT(self, environ):
        from repoze.urispace.middleware import getAssertions
        return getAssertions(environ)

    def test_no_key(self):
        self.assertEqual(self._callFUT({}), {})

    def test_w_key(self):
        ASSERTIONS = {'foo': 'bar'}
        environ = {'repoze.urispace.assertions': ASSERTIONS}
        self.assertEqual(self._callFUT(environ), ASSERTIONS)

class UrispaceMiddlewareTests(unittest.TestCase):

    _tempdir = None
    _started = None

    def tearDown(self):
        if self._tempdir is not None:
            import shutil
            shutil.rmtree(self._tempdir)

    def _getTargetClass(self):
        from repoze.urispace.middleware import URISpaceMiddleware
        return URISpaceMiddleware

    def _makeOne(self, application, source):
        return self._getTargetClass()(application, source)

    def _makeFile(self, text, basename='urispace.xml'):
        import os
        import tempfile
        td = self._tempdir = tempfile.mkdtemp()
        filename = os.path.join(td, basename)
        f = open(filename, 'w')
        f.write(text)
        f.flush()
        f.close()
        return filename

    def _makeStream(self, text):
        from StringIO import StringIO
        return StringIO(text)

    def _makeEnviron(self,
                     request_method='GET',
                     server_name='example.com',
                     server_port='80',
                     script_name='',
                     path_info='/',
                     query_string='',
                     use_https=False,
                     **kw):
        environ = {'REQUEST_METHOD': request_method,
                   'SERVER_NAME': server_name,
                   'SERVER_PORT': server_port,
                   'SCRIPT_NAME': script_name,
                   'PATH_INFO': path_info,
                   'QUERY_STRING': query_string,
                  }
        environ['wsgi.url_scheme'] = use_https and 'HTTPS' or 'HTTP'
        environ.update(kw)
        return environ

    def _startResponse(self, status, headers, exc_info=None):
        self._started = (status, headers, exc_info)

    def _makeApplication(self):
        def _app(environ, start_response):
            start_response('200 OK', ())
            return ['body']
        return _app

    def test_ctor_w_stream(self):
        from zope.interface.verify import verifyObject
        from repoze.urispace.interfaces import IURISpaceElement
        application = self._makeApplication()
        stream = self._makeStream(_EMPTY_URISPACE)

        mw = self._makeOne(application, stream)

        self.failUnless(mw.application is application)
        verifyObject(IURISpaceElement, mw.urispace)

    def test_ctor_w_filename(self):
        from zope.interface.verify import verifyObject
        from repoze.urispace.interfaces import IURISpaceElement
        application = self._makeApplication()
        filename = self._makeFile(_EMPTY_URISPACE)

        mw = self._makeOne(application, filename)

        self.failUnless(mw.application is application)
        verifyObject(IURISpaceElement, mw.urispace)

    def test_getInfo_defaults(self):
        application = self._makeApplication()
        stream = self._makeStream(_EMPTY_URISPACE)
        mw = self._makeOne(application, stream)
        environ = self._makeEnviron()

        info = mw.getInfo(environ)

        self.assertEqual(info['scheme'], 'HTTP')
        self.assertEqual(info['nethost'], 'example.com')
        self.assertEqual(info['path'], [])
        self.assertEqual(info['query'], {})
        self.assertEqual(info['fragment'], '')

    def test_getInfo_alt_port(self):
        application = self._makeApplication()
        stream = self._makeStream(_EMPTY_URISPACE)
        mw = self._makeOne(application, stream)
        environ = self._makeEnviron(server_port='8000')

        info = mw.getInfo(environ)

        self.assertEqual(info['scheme'], 'HTTP')
        self.assertEqual(info['nethost'], 'example.com:8000')

    def test_getInfo_https(self):
        application = self._makeApplication()
        stream = self._makeStream(_EMPTY_URISPACE)
        mw = self._makeOne(application, stream)
        environ = self._makeEnviron(use_https=True)

        info = mw.getInfo(environ)

        self.assertEqual(info['scheme'], 'HTTPS')

    def test_getInfo_https_alt_port(self):
        application = self._makeApplication()
        stream = self._makeStream(_EMPTY_URISPACE)
        mw = self._makeOne(application, stream)
        environ = self._makeEnviron(use_https=True, server_port='4443')

        info = mw.getInfo(environ)

        self.assertEqual(info['scheme'], 'HTTPS')
        self.assertEqual(info['nethost'], 'example.com:4443')

    def test_getInfo_script_name_ends_w_slash(self):
        application = self._makeApplication()
        stream = self._makeStream(_EMPTY_URISPACE)
        mw = self._makeOne(application, stream)
        environ = self._makeEnviron(script_name='script/name/',
                                    path_info='index.html')

        info = mw.getInfo(environ)

        self.assertEqual(info['path'], ['script', 'name', 'index.html'])

    def test_getInfo_script_name_ends_wo_slash(self):
        application = self._makeApplication()
        stream = self._makeStream(_EMPTY_URISPACE)
        mw = self._makeOne(application, stream)
        environ = self._makeEnviron(script_name='script/name',
                                    path_info='index.html')

        info = mw.getInfo(environ)

        self.assertEqual(info['path'], ['script', 'name', 'index.html'])

    def test_getInfo_script_name_ends_wo_slash_path_info_is_slash(self):
        application = self._makeApplication()
        stream = self._makeStream(_EMPTY_URISPACE)
        mw = self._makeOne(application, stream)
        environ = self._makeEnviron(script_name='script/name',
                                    path_info='/')

        info = mw.getInfo(environ)

        self.assertEqual(info['path'], ['script', 'name'])

    def test_getInfo_query_string_normal(self):
        application = self._makeApplication()
        stream = self._makeStream(_EMPTY_URISPACE)
        mw = self._makeOne(application, stream)
        environ = self._makeEnviron(query_string='foo=bar')

        info = mw.getInfo(environ)

        self.assertEqual(info['query'], {'foo': ['bar']})

    def test_getInfo_query_string_multiple(self):
        application = self._makeApplication()
        stream = self._makeStream(_EMPTY_URISPACE)
        mw = self._makeOne(application, stream)
        environ = self._makeEnviron(query_string='foo=bar&baz=bam')

        info = mw.getInfo(environ)

        self.assertEqual(info['query'], {'foo': ['bar'], 'baz': ['bam']})

    def test_getInfo_query_string_w_blank_value(self):
        application = self._makeApplication()
        stream = self._makeStream(_EMPTY_URISPACE)
        mw = self._makeOne(application, stream)
        environ = self._makeEnviron(query_string='foo=bar&baz')

        info = mw.getInfo(environ)

        self.assertEqual(info['query'], {'foo': ['bar'], 'baz': ['']})

    def test___call___w_empty_urispace(self):
        application = self._makeApplication()
        stream = self._makeStream(_EMPTY_URISPACE)
        mw = self._makeOne(application, stream)
        environ = self._makeEnviron()

        result = mw(environ, self._startResponse)

        self.assertEqual(self._started, ('200 OK', (), None))
        self.assertEqual(environ['repoze.urispace.assertions'], {})

    def test___call___w_default_urispace(self):
        application = self._makeApplication()
        stream = self._makeStream(_DEFAULT_URISPACE)
        mw = self._makeOne(application, stream)
        environ = self._makeEnviron()

        result = mw(environ, self._startResponse)

        self.assertEqual(self._started, ('200 OK', (), None))
        self.assertEqual(environ['repoze.urispace.assertions'], {'foo': 'bar'})

    def test___call___w_testing_urispace_hit(self):
        application = self._makeApplication()
        stream = self._makeStream(_TESTING_URISPACE)
        mw = self._makeOne(application, stream)
        environ = self._makeEnviron(script_name='/to_match/something')

        result = mw(environ, self._startResponse)

        self.assertEqual(environ['repoze.urispace.assertions'], {'foo': 'qux'})

    def test___call___w_testing_urispace_miss(self):
        application = self._makeApplication()
        stream = self._makeStream(_TESTING_URISPACE)
        mw = self._makeOne(application, stream)
        environ = self._makeEnviron(script_name='/nomatch/other')

        result = mw(environ, self._startResponse)

        self.assertEqual(environ['repoze.urispace.assertions'], {'foo': 'bar'})


_EMPTY_URISPACE = """\
<?xml version="1.0" ?>
<urispace/>
"""

_DEFAULT_URISPACE = """\
<?xml version="1.0" ?>
<urispace>
 <foo>bar</foo>
</urispace>
"""

_TESTING_URISPACE = """\
<?xml version="1.0" ?>
<urispace
   xmlns:uri="http://www.w3.org/2000/urispace">
 <foo>bar</foo>
 <uri:path uri:match="to_match">
   <foo>qux</foo>
 </uri:path>
</urispace>
"""
