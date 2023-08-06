from unittest import TestCase, makeSuite

from DateTime.DateTime import DateTime
from ZTUtils import make_query
from ZPublisher.HTTPRequest import HTTPRequest

class Tests(TestCase):
  def test_general(self):
    rd = self._check(
      dict(i=1, b=True, f=float(1), s='abc', u=u'\u0100', d=DateTime(),
           le=[], l=[1,2,3],
           )
      )
    self.assert_(isinstance(rd['f'], float), "float not handled correctly")
    self.assert_(isinstance(rd['u'], unicode), "unicode not handled correctly")

  def test_dict(self):
    self._check(dict(di=dict(i=1, b=False, le=[], l=[1,2,3],),),
                transformer=lambda d: d.update(dict(di=dict(d['di'].items()))) or d,
                )

  def test_tuple(self):
    self._check(dict(te=(), t=(1,2,3)),
                dict(te=[], t=[1,2,3]),
                )

  def _check(self, data, result=None, transformer=None):
    if result is None: result = data
    if transformer is None: transformer = lambda x: x
    r = HTTPRequest(
      None,
      dict(REQUEST_METHOD='GET', QUERY_STRING=make_query(data),
           SERVER_NAME='', SERVER_PORT='', SCRIPT_NAME='',
           ),
      None,
      )
    r.processInputs()
    self.assertEqual(transformer(r.form), result)
    return r.form


def test_suite(): return makeSuite(Tests)
