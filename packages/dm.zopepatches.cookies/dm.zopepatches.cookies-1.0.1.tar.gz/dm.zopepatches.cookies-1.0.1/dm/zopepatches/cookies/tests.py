from unittest import TestCase, makeSuite

from ZPublisher.HTTPResponse import HTTPResponse

import httponly, rfc2965 # activate extensions
from dm.zopepatches.cookies import _find_unquoted_sc, _find_params, _process, \
     string_param, quoted_string_param, boolean_param, sequence_param

class Tests(TestCase):
  def test_patching(self):
    r = HTTPResponse()
    # Note: Zope 2.12 will support "http_only" instead
    r.setCookie('c', 'cv', httponly=True)
    self.assertEqual(r._cookie_list(), ['Set-Cookie: c="cv"; httponly'])
    r.setCookie('c', 'cv', httponly=False)
    self.assertEqual(r._cookie_list(), ['Set-Cookie: c="cv"'])

  def test_case_normalization(self):
    r = HTTPResponse()
    r.setCookie('c', 'cv', hTtPoNlY=True)
    self.assertEqual(r._cookie_list(), ['Set-Cookie: c="cv"; httponly'])
    
  def test_find_unquoted_sc(self):
    s = 'c="cv; ux"; P1; P2=2'
    i = _find_unquoted_sc(s, 0)
    self.assertEqual(i, 10)
    i = _find_unquoted_sc(s, 11)
    self.assertEqual(i, 14)
    i = _find_unquoted_sc(s, 15)
    self.assertEqual(i, -1)

  def test_find_params(self):
    s = 'c="cv; ux"; P1; P2=2'
    self.assertEqual(list(_find_params(s)), ['p1', 'p2'])

  def test_dont_touch_handled(self):
    s = 'c="cv"; HttpOnly=x'
    cl = ['', s]
    _process(dict(httponly=True), cl, 0)
    _process(dict(httponly=True), cl, 1)
    self.assertEqual(cl[0], '; httponly')
    self.assertEqual(cl[1], s)

  def test_types(self):
    self.assertEqual(string_param('n', 'a'), 'n=a')
    self.assertEqual(string_param('n', 'a b'), 'n="a b"')
    self.assertEqual(string_param('n', 'a,b'), 'n="a,b"')
    self.assertEqual(string_param('n', 'a;b'), 'n="a;b"')
    self.assertEqual(quoted_string_param('n', 'a'), 'n="a"')
    self.assertEqual(boolean_param('n', True), 'n')
    self.assertEqual(boolean_param('n', False), '')
    self.assertEqual(sequence_param('n', (1,2,3)), 'n="1,2,3"')

def test_suite(): return makeSuite(Tests)

