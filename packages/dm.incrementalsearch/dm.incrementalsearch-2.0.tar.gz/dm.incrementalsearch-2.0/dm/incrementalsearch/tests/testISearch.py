# Copyright (C) 2005-2006 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
# see "LICENSE.txt" for details
#       $Id: testISearch.py,v 1.1.1.1 2008/06/27 19:21:39 dieter Exp $
'''IncrementalSearch tests.'''

from unittest import TestCase, TestSuite, makeSuite, TextTestRunner
from BTrees.IIBTree import IISet
from BTrees.LLBTree import LLSet
from BTrees.OOBTree import OOSet

from dm.incrementalsearch import ISearch, IBTree, Enumerator, \
     INLIST_SUCCESS, CANDIDATE, NOT_INLIST, AT_END, \
     IOr, INot, IAnd, \
     IOr_int, IAnd_int, \
     INT, OBJECT, LONG, \
     Unspecified

class _ObjTests:
  KEYTYPE = OBJECT

class _LongTests:
  KEYTYPE = LONG

class IOrTests(TestCase):
  KEYTYPE = INT

  def setUp(self):
    if self.KEYTYPE == INT: set = IISet
    elif self.KEYTYPE == LONG: set = LLSet
    else: set = OOSet
    self._search = IOr(
      self.KEYTYPE,
      IBTree(set(range(5,20,5)), self.KEYTYPE),
      IBTree(set(range(2,20,2)), self.KEYTYPE),
      )
    self._search.complete()

  def testResult(self):
    self.assertEqual(self._search.asSet().keys(),
                     IISet(range(5,20,5) + range(2,20,2)).keys()
                     )
   
  def testToTraversal(self):
    search = self._search
    l = []; i = 0
    while True:
      cr = search.advanceTo(i)
      self.assertEqual(i >= 19, cr == AT_END)
      if cr == AT_END: break
      if cr == INLIST_SUCCESS: l.append(search.value)
      if cr == CANDIDATE: i = search.value
      else: i += 1
    self.assertEqual(l, IISet(range(5,20,5) + range(2,20,2)).keys())

  def testFromJumping(self):
    search = self._search
    for s,r in ((4,5), (6,8), (14,15), (15,16)):
      self.assertEqual(search.advanceFrom(s, Unspecified), INLIST_SUCCESS)
      self.assertEqual(search.value, r)
    self.assertEqual(search.advanceFrom(18, Unspecified), AT_END)

  def testFromLimit(self):
    search = self._search
    self.assertEqual(search.advanceFrom(2,4), CANDIDATE)
    self.assertEqual(search.value, 4)
    self.assertEqual(search.advanceFrom(8,11), INLIST_SUCCESS)
    self.assertEqual(search.value, 10)
    self.assertEqual(search.advanceFrom(14,16), INLIST_SUCCESS)
    self.assertEqual(search.value, 15)

  def testFromToInterleaving(self):
    search = self._search
    self.assertEqual(search.advanceFrom(8,10), CANDIDATE)
    self.assertEqual(search.value, 10)
    self.assertEqual(search.advanceTo(10), INLIST_SUCCESS)
    self.assertEqual(search.advanceFrom(10,11), CANDIDATE)
    self.assertEqual(search.value, 12)
    self.assertEqual(search.advanceTo(12), INLIST_SUCCESS)
    self.assertEqual(search.advanceFrom(12,13), CANDIDATE)
    self.assertEqual(search.value, 14)
    self.assertEqual(search.advanceTo(15), INLIST_SUCCESS)

class IOrTests_obj(_ObjTests, IOrTests): pass
class IOrTests_long(_LongTests, IOrTests): pass

class INotTests(TestCase):
  KEYTYPE = INT

  def setUp(self):
    if self.KEYTYPE == INT: set = IISet
    elif self.KEYTYPE == LONG: set = LLSet
    else: set = OOSet
    self._search = INot(
      IBTree(set(range(4, 12, 4)), self.KEYTYPE),
      Enumerator(set(range(2, 12, 2))),
      )

  def testResult(self):
    self.assertEqual(self._search.asSet().keys(), [2, 6, 10])

  def testToTraversal(self):
    search = self._search
    for i in range(2, 12, 2):
      cr = search.advanceTo(i)
      self.assertEqual(i > 10, cr == AT_END)
      self.assertEqual(i in [2, 6, 10], cr == INLIST_SUCCESS)
      self.assertEqual(i <= 10 and i not in [2, 6, 10], cr == NOT_INLIST)

  def testFromLimit(self):
    search = self._search
    self.assertEqual(search.advanceFrom(2,6), CANDIDATE)
    self.assertEqual(search.value, 6)
    self.assertEqual(search.advanceTo(6), INLIST_SUCCESS)
    self.assertEqual(search.value, 6)
    self.assertEqual(search.advanceFrom(7,11), INLIST_SUCCESS)
    self.assertEqual(search.value, 10)
    self.assertEqual(search.advanceFrom(11,13), AT_END)

class INotTests_obj(_ObjTests, INotTests): pass
class INotTests_long(_LongTests, INotTests): pass

class IFilterTests(TestCase):
  KEYTYPE = INT

  def setUp(self):
    if self.KEYTYPE == INT: set = IISet
    elif self.KEYTYPE == LONG: set = LLSet
    else: set = OOSet
    self._search = IFilter(
      self.KEYTYPE,
      lambda i, inot=range(4, 12, 4): i not in inot,
      Enumerator(set(range(2, 12, 2))),
      )

class IFilterTests_obj(_ObjTests, IFilterTests): pass
class IFilterTests_long(_LongTests, IFilterTests): pass



class IntegrationTests(TestCase):
  KEYTYPE = INT

  def testAndOrNot(self):
    if self.KEYTYPE == INT: set = IISet
    elif self.KEYTYPE == LONG: set = LLSet
    else: set = OOSet
    enumerator = Enumerator(set(range(0,17)))
    search = IOr(self.KEYTYPE,
      IBTree(set(range(5,17,5)), self.KEYTYPE),
      INot(IBTree(set(range(5,11)), self.KEYTYPE), enumerator),
      )
    search.complete()
    search = IAnd(self.KEYTYPE,
      search,
      INot(IBTree(set(range(1,17,2)), self.KEYTYPE), enumerator),
      )
    search.complete()
    self.assertEqual(search.asSet().keys(), [0,2,4,10,12,14,16])

class IntegrationTests_obj(_ObjTests, IntegrationTests): pass
class IntegrationTests_long(_LongTests, IntegrationTests): pass


class _HitNohitISearch(ISearch):
  '''auxiliary class for covering IOr test.

  Does not report candidates but only hits and nohits.
  '''
  def __init__(self, keytype, set):
    ISearch.__init__(self, keytype)
    self._set = set
    self.estimatedSize = len(set)

  def advanceTo(self, end):
    return self._locate(end)

  def advanceFrom(self, start, upto):
    return self._locate(start, False, upto)

  def _locate(self, key, include=True, limit=Unspecified):
    if key is Unspecified: key = None
    keys = list(self._set.keys(key))
    if not include and key in keys: keys.remove(key) # 21
    if not keys: return AT_END
    if include: cr = key != keys[0] and NOT_INLIST or INLIST_SUCCESS
    else: cr = limit is not Unspecified and keys[0] >= limit and CANDIDATE or INLIST_SUCCESS
    self.classification = cr
    if cr <= CANDIDATE: self.value = keys[0]
    else: self.value = key
    return cr

class IOrCoverTests(TestCase):
  KEYTYPE = INT

  def setUp(self):
    if self.KEYTYPE == INT: set = IISet
    elif self.KEYTYPE == LONG: set = LLSet
    else: set = OOSet
    s1 = set((0, 5, 10))
    s2 = set((0,3,6,10,12))
    self._search = IOr(self.KEYTYPE,
                       IBTree(s1, self.KEYTYPE),
                       _HitNohitISearch(self.KEYTYPE, s2),
                       )
    self._search.complete()
    r = set(s1)
    r.update(s2)
    self._result = r

  def testAdvanceTo(self):
    r = self._result; s = self._search; to = s.advanceTo
    for i in range(r.minKey(), r.maxKey()+1):
      cr = to(i)
      self.assertEqual(cr, i not in r and NOT_INLIST or INLIST_SUCCESS)
      if cr == INLIST_SUCCESS: self.assertEqual(s.value, i)
    self.assertEqual(to(r.maxKey()+1), AT_END)

  def testEnumerate(self):
    self.assertEqual(list(self._result), self._search.asSet().keys())

  def testAdvanceFrom(self):
    s = self._search; fr = s.advanceFrom
    def check(start, upto, result=None):
      cr = fr(start, upto)
      self.assert_((result is not None) == (cr == INLIST_SUCCESS))
      if cr == INLIST_SUCCESS: self.assertEqual(result, s.value)
    check(1,3)
    check(1,4,3)
    check(3,7,5)
    check(5,7,6)
    check(6,10)
    check(6,13, 10)
    check(11,13, 12)
    self.assertEqual(fr(12,14), AT_END)

class IOrCoverTests_obj(_ObjTests, IOrCoverTests): pass
class IOrCoverTests_long(_LongTests, IOrCoverTests): pass


class _ISearchCandidate1Hit2(ISearch):
  def __init__(self):
    ISearch.__init__(self, INT)

  def advanceTo(self, end):
    self.value = end
    cl = end != 2 and NOT_INLIST or INLIST_SUCCESS
    self.classification = cl
    #print 'advanceTo', end, cl
    return cl

  def advanceFrom(self, fr, upto):
    if fr is Unspecified or fr < 1:
      if upto is Unspecified or upto > 2: v = 2; cl = INLIST_SUCCESS
      elif upto <= 1: v = 1; cl = CANDIDATE
      else: v = 2; cl = CANDIDATE
    elif fr < 2:
      if upto is Unspecified or upto > 2: v = 2; cl = INLIST_SUCCESS
      else: v = upto; cl = CANDIDATE
    else: cl = AT_END; v = 2
    self.classification = cl
    self.value = v
    #print 'advanceFron', fr, upto, cl ,v
    return cl

class IOrToCandidateBug(TestCase):
  def testToCandidateBug(self):
    s = IISet((0,))
    ss = IOr_int(IBTree(s), _ISearchCandidate1Hit2())
    ss.complete()
    self.assertEqual(ss.advanceFrom(Unspecified, Unspecified), INLIST_SUCCESS)
    self.assertEqual(ss.value, 0)
    self.assertEqual(ss.advanceFrom(ss.value, Unspecified), INLIST_SUCCESS)
    self.assertEqual(ss.value, 2)
    self.assertEqual(ss.advanceFrom(ss.value, Unspecified), AT_END)



class TestCompletion(TestCase):
  set = [5, [1,2,3], 4, [-1, 6], -1]

  def testAnd(self):
    self._check('and')

  def testOr(self):
    self._check('or')

  def _check(self, op):
    search, flat = self._build(op, self.set)
    sizes = [s.estimatedSize for s in search.unmantle() if s >= 0]
    proper = [i for i in flat if i >= 0]
    no_improper = len(flat) - len(proper)
    if no_improper:
      self.assertEqual(sizes[-no_improper:], [-1] * no_improper)
      sizes = sizes[:-no_improper]
    proper.sort()
    if op == 'or': proper.reverse()
    self.assertEqual(proper, sizes)

  def _build(self, op, set):
    class _Proxy(ISearch):
      def __init__(self, size):
        self._s = size
        ISearch.__init__(self, INT)
        self.estimatedSize = size
    sl = []; il = []
    for s in set:
      if isinstance(s, list):
        search, sizes = self._build(op, s)
        sl.append(search); il += sizes
      else: sl.append(_Proxy(s)), il.append(s)
    cl = op == 'and' and IAnd_int or IOr_int
    search = cl(*sl); search.complete()
    return search, il

    

def test_suite():
  md = globals()
  cls = []
  for cl in [
    IOrTests,
    IOrCoverTests,
    INotTests,
    IFilterTests,
    IntegrationTests,
    ]:
    cls.append(cl)
    cls.append(md[cl.__name__ + '_obj'])
    cls.append(md[cl.__name__ + '_long'])
  cls.append(TestCompletion)
  cls.append(IOrToCandidateBug)
  return TestSuite([makeSuite(cl) for cl in cls])

def main():
  tester = TextTestRunner()
  tester.run(test_suite())

if __name__ == '__main__': main()

