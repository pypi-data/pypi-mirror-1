import unittest


class _PredicateTestBase:

    _MARKER = object()

    def _makeOne(self, pattern):
        return self._getTargetClass()(pattern)

    def assertMiss(self, pattern, info):
        pp = self._makeOne(pattern)
        hit, new_info = pp(info)
        self.failIf(hit)
        self.assertEqual(new_info, None)

    def assertHit(self, pattern, info, expected_info=_MARKER):
        if expected_info is self._MARKER:
            expected_info = info
        pp = self._makeOne(pattern)
        hit, new_info = pp(info)
        self.failUnless(hit)
        self.assertEqual(new_info, expected_info)


class SchemePredicateTests(unittest.TestCase, _PredicateTestBase):

    def _getTargetClass(self):
        from repoze.urispace.predicates import SchemePredicate
        return SchemePredicate

    def test_single_empty_info_miss(self):
        self.assertMiss('http', {})

    def test_single_empty_scheme_miss(self):
        self.assertMiss('http', {'scheme': ''})

    def test_single_nonempty_scheme_miss(self):
        self.assertMiss('http', {'scheme': 'https'})

    def test_single_nonempty_scheme_hit(self):
        self.assertHit('http', {'scheme': 'http'})

    def test_multi_empty_info_miss(self):
        self.assertMiss('http https', {})

    def test_multi_empty_scheme_miss(self):
        self.assertMiss('http https', {'scheme': ''})

    def test_multi_nonempty_scheme_miss(self):
        self.assertMiss('http https', {'scheme': 'ftp'})

    def test_mulit_nonempty_scheme_hit(self):
        self.assertHit('http https', {'scheme': 'http'})
        self.assertHit('http https', {'scheme': 'https'})


class NethostPredicateTests(unittest.TestCase, _PredicateTestBase):

    def _getTargetClass(self):
        from repoze.urispace.predicates import NethostPredicate
        return NethostPredicate

    def test_ctor_w_extra_colon_raises_ValueError(self):
        self.assertRaises(ValueError, self._makeOne, 'foo:1234:567')

    def test_ctor_w_nonprefix_wildcard_raises_ValueError(self):
        self.assertRaises(ValueError, self._makeOne, 'foo*')
        self.assertRaises(ValueError, self._makeOne, 'foo?')

    def test_empty_info_miss(self):
        self.assertMiss('www.example.com', {})

    def test_empty_nethost_miss(self):
        self.assertMiss('www.example.com', {'nethost': ('', None)})

    def test_nonempty_nethost_miss(self):
        self.assertMiss('www.example.com',
                        {'nethost': ('other.example.com', None)})

    def test_nonempty_nethost_hit(self):
        self.assertHit('www.example.com',
                       {'nethost': ('www.example.com', None)})

    def test_nonempty_nethost_default_port_miss(self):
        self.assertMiss('www.example.com',
                        {'nethost': ('www.example.com', 8080)})

    def test_nonempty_nethost_with_port_miss(self):
        self.assertMiss('www.example.com:9080',
                        {'nethost': ('www.example.com', 8080)})

    def test_nonempty_nethost_with_port_hit(self):
        self.assertHit('www.example.com:8080',
                       {'nethost': ('www.example.com', 8080)})

    def test_single_wildcard_no_period_raises(self):
        self.assertRaises(ValueError, self._makeOne, '?foo')

    def test_single_wildcard_nethost_miss(self):
        self.assertMiss('?.example.com',
                        {'nethost': ('www.other.example.com', None)})
        self.assertMiss('?.example.com', {'nethost': ('example.com', None)})

    def test_single_wildcard_nethost_hit(self):
        self.assertHit('?.example.com', {'nethost': ('www.example.com', None)})

    def test_multi_wildcard_nethost_miss(self):
        self.assertMiss('*.example.com', {'nethost': ('example.com', None)})

    def test_multi_wildcard_nethost_hit(self):
        self.assertHit('*.example.com',
                       {'nethost': ('www.example.com', None)})
        self.assertHit('*.example.com',
                       {'nethost': ('www.other.example.com', None)})


class PathElementPatternTests(unittest.TestCase):

    def _getTargetClass(self):
        from repoze.urispace.predicates import PathElementPattern
        return PathElementPattern

    def _makeOne(self, pattern):
        return self._getTargetClass()(pattern)

    def test_double_wildcard_raises_ValueError(self):
        self.assertRaises(ValueError, self._makeOne, 'foo*bar*')

    def test_match_empty_nonempty_miss(self):
        ep = self._makeOne('')
        self.failIf(ep('foo'))

    def test_match_empty_empty_hit(self):
        ep = self._makeOne('')
        self.failUnless(ep(''))

    def test_match_noempty_empty_miss(self):
        ep = self._makeOne('foo')
        self.failIf(ep(''))

    def test_match_nonempty_nonempty_miss(self):
        ep = self._makeOne('foo')
        self.failIf(ep('bar'))

    def test_match_nonempty_nonempty_hit(self):
        ep = self._makeOne('foo')
        self.failUnless(ep('foo'))

    def test_match_wildcard_any_empty_hit(self):
        ep = self._makeOne('*')
        self.failUnless(ep(''))

    def test_match_wildcard_any_nonempty_path_hit(self):
        ep = self._makeOne('*')
        self.failUnless(ep('foo'))

    def test_match_wildcard_prefix_miss(self):
        ep = self._makeOne('*.html')
        self.failIf(ep('foohtml'))

    def test_match_wildcard_prefix_hit(self):
        ep = self._makeOne('*.html')
        self.failUnless(ep('foo.html'))

    def test_match_wildcard_middle_miss(self):
        ep = self._makeOne('foo*.html')
        self.failIf(ep('foohtml'))

    def test_match_wildcard_middle_pattern_hit(self):
        ep = self._makeOne('foo*.html')
        self.failUnless(ep('foo.html'))

    def test_match_wildcard_suffix_miss(self):
        ep = self._makeOne('foo*')
        self.failIf(ep('barfoo'))

    def test_match_wildcard_suffix_pattern_hit(self):
        ep = self._makeOne('foo*')
        self.failUnless(ep('foo.html'))


class PathFirstPredicateTests(unittest.TestCase, _PredicateTestBase):

    def _getTargetClass(self):
        from repoze.urispace.predicates import PathFirstPredicate
        return PathFirstPredicate

    def test_match_empty_pattern_empty_info_miss(self):
        self.assertMiss('', {})

    def test_match_empty_pattern_empty_path_miss(self):
        self.assertMiss('', {'path': ()})

    def test_match_empty_pattern_nonempty_path_miss(self):
        self.assertMiss('', {'path': ('foo', 'bar')})

    def test_match_empty_pattern_nonempty_path_not_first_miss(self):
        self.assertMiss('', {'path': ('foo', 'bar', '')})

    def test_match_empty_pattern_nonempty_path_first_hit(self):
        self.assertHit('', {'path': ('',)},
                           {'path': ()})
        self.assertHit('', {'path': ('', 'foo', 'bar')},
                           {'path': ('foo', 'bar')})


    def test_match_nonempty_pattern_empty_info_miss(self):
        self.assertMiss('index.html', {})

    def test_match_nonempty_pattern_empty_path_miss(self):
        self.assertMiss('index.html', {'path': ()})

    def test_match_nonempty_pattern_nonempty_path_miss(self):
        self.assertMiss('index.html', {'path': ('foo', 'bar')})

    def test_match_nonempty_pattern_nonempty_path_not_first_miss(self):
        self.assertMiss('index.html', {'path': ('foo', 'bar', 'index.html')})

    def test_match_nonempty_pattern_nonempty_path_first_hit(self):
        self.assertHit('foo', {'path': ('foo',)},
                              {'path': ()})
        self.assertHit('foo', {'path': ('foo', 'index.html',)},
                              {'path': ('index.html',)})


class PathLastPredicateTests(unittest.TestCase, _PredicateTestBase):

    def _getTargetClass(self):
        from repoze.urispace.predicates import PathLastPredicate
        return PathLastPredicate

    def _makeOne(self, element_pattern):
        return self._getTargetClass()(element_pattern)


    def test_match_empty_pattern_empty_info_miss(self):
        self.assertMiss('', {})

    def test_match_empty_pattern_empty_path_miss(self):
        self.assertMiss('', {'path': ()})

    def test_match_empty_pattern_nonempty_path_miss(self):
        self.assertMiss('', {'path': ('foo', 'bar')})

    def test_match_empty_pattern_nonempty_path_not_last_miss(self):
        self.assertMiss('', {'path': ('', 'foo')})

    def test_match_empty_pattern_nonempty_path_last_hit(self):
        self.assertHit('', {'path': ('foo', 'bar', '')}, {'path': ()})


    def test_match_nonempty_pattern_empty_info_miss(self):
        self.assertMiss('index.html', {})

    def test_match_nonempty_pattern_empty_path_miss(self):
        self.assertMiss('index.html', {'path': ()})

    def test_match_nonempty_pattern_nonempty_path_miss(self):
        self.assertMiss('index.html', {'path': ('foo', 'bar')})

    def test_match_nonempty_pattern_nonempty_path_not_last_miss(self):
        self.assertMiss('bar', {'path': ('foo', 'bar', 'index.html')})

    def test_match_nonempty_pattern_nonempty_path_first_hit(self):
        self.assertHit('index.html', {'path': ('foo', 'bar', 'index.html',)},
                                     {'path': ()})


class PathAnyPredicateTests(unittest.TestCase, _PredicateTestBase):

    def _getTargetClass(self):
        from repoze.urispace.predicates import PathAnyPredicate
        return PathAnyPredicate

    def _makeOne(self, element_pattern):
        return self._getTargetClass()(element_pattern)


    def test_match_empty_pattern_empty_info_miss(self):
        self.assertMiss('', {})

    def test_match_empty_pattern_empty_path_miss(self):
        self.assertMiss('', {'path': ()})

    def test_match_empty_pattern_nonempty_path_miss(self):
        self.assertMiss('', {'path': ('foo', 'bar')})

    def test_match_empty_pattern_nonempty_path_first_hit(self):
        self.assertHit('', {'path': ('', 'foo')},
                           {'path': ('foo',)})

    def test_match_empty_pattern_nonempty_path_middle_hit(self):
        self.assertHit('', {'path': ('foo', '', 'bar')},
                           {'path': ('bar',)})

    def test_match_empty_pattern_nonempty_path_last_hit(self):
        self.assertHit('', {'path': ('foo', 'bar', '')},
                           {'path': ()})


    def test_match_nonempty_pattern_empty_info_miss(self):
        self.assertMiss('index.html', {})

    def test_match_nonempty_pattern_empty_path_miss(self):
        self.assertMiss('index.html', {'path': ()})

    def test_match_nonempty_pattern_nonempty_path_miss(self):
        self.assertMiss('index.html', {'path': ('foo', 'bar')})

    def test_match_nonempty_pattern_nonempty_path_first_hit(self):
        self.assertHit('foo', {'path': ('foo', 'bar', 'index.html')},
                              {'path': ('bar', 'index.html')})

    def test_match_nonempty_pattern_nonempty_path_middle_hit(self):
        self.assertHit('bar', {'path': ('foo', 'bar', 'index.html')},
                              {'path': ('index.html',)})

    def test_match_nonempty_pattern_nonempty_path_last_hit(self):
        self.assertHit('index.html', {'path': ('foo', 'bar', 'index.html')},
                                     {'path': ()})


class QueryKeyPredicateTests(unittest.TestCase, _PredicateTestBase):

    def _getTargetClass(self):
        from repoze.urispace.predicates import QueryKeyPredicate
        return QueryKeyPredicate

    def test_ctor_w_equals_raises_ValueError(self):
        self.assertRaises(ValueError, self._makeOne, 'foo=baz')

    def test_empty_info_miss(self):
        self.assertMiss('foo', {})

    def test_empty_query_miss(self):
        self.assertMiss('foo', {'query': {}})

    def test_nonempty_query_miss(self):
        self.assertMiss('foo', {'query': {'bar': 'baz'}})

    def test_nonempty_query_hit(self):
        self.assertHit('foo', {'query': {'foo': 'baz'}})


class QueryValuePredicateTests(unittest.TestCase, _PredicateTestBase):

    def _getTargetClass(self):
        from repoze.urispace.predicates import QueryValuePredicate
        return QueryValuePredicate

    def test_ctor_multiple_equals_raises_ValueError(self):
        self.assertRaises(ValueError, self._makeOne, 'foo=bar=baz')
        self.assertRaises(ValueError, self._makeOne, 'foo==baz')

    def test_empty_info_miss(self):
        self.assertMiss('foo=bar', {})

    def test_empty_query_miss(self):
        self.assertMiss('foo=bar', {'query': {}})

    def test_nonempty_query_no_key_miss(self):
        self.assertMiss('foo=bar', {'query': {'bar': 'baz'}})

    def test_nonempty_query_wrong_value_miss(self):
        self.assertMiss('foo=bar', {'query': {'foo': 'baz'}})

    def test_nonempty_query_hit(self):
        self.assertHit('foo=baz', {'query': {'foo': 'baz'}})
