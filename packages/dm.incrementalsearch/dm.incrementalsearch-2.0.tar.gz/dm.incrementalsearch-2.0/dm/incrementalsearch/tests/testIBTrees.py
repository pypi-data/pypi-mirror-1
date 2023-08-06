# Copyright (C) 2005 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
# see "LICENSE.txt" for details
#       $Id: testIBTrees.py,v 1.1.1.1 2008/06/27 19:21:39 dieter Exp $
'''Tests for BTrees based incremental searches.'''

from unittest import TestCase, TestSuite, makeSuite, TextTestRunner

import BTrees
from BTrees.IIBTree import IISet, IITreeSet
from BTrees.IOBTree import IOBucket, IOBTree
from BTrees.OOBTree import OOBucket, OOBTree, OOTreeSet, OOSet
from BTrees.LLBTree import LLSet, LLTreeSet
from BTrees.LOBTree import LOBucket, LOBTree

from dm.incrementalsearch import IBTree, Unspecified, \
     INLIST_SUCCESS, INLIST, AT_END, \
     INT, OBJECT, LONG, \
     intersection


class BTreeISearchTestBase(TestCase):
  '''test suite controlled by *keys* and *split*.'''

  # to be defined by deriving classes
  keys = None # keys the constructed BTree should have
  split = None # where the tree should have subtrees

  KEYTYPE = INT

  SET_CLASS = IISet


  def setUp(self):
    keys = self.keys
    set =  self._set = self.SET_CLASS(keys)
    tree, _ = self._makeTree(set, self.split)
    self._search = IBTree(tree, self.KEYTYPE)

  def _makeTree(self, set, split, next=None):
    if self.KEYTYPE == INT: Bucket = IOBucket; Tree = IOBTree
    elif self.KEYTYPE == LONG: Bucket = LOBucket; Tree = LOBTree
    else: Bucket = OOBucket; Tree = OOBTree 
    keys = list(set.keys())
    n = len(set)
    if split:
      i = 0; children = []
      for s in split:
        grandChildren = []
        while True:
          if i >= n: break
          x = set[i]
          if x >= s: break
          grandChildren.append(x); i += 1
        children.append(grandChildren)
        children.append(s)
      children.append(set.keys(split[-1]))
      for i in range(len(children)-1, -1, -2):
        tree = Bucket(); items = []
        for k in children[i]: items += [k, None]
        S = (tuple(items),)
        if next is not None: S += (next,)
        tree.__setstate__(S)
        next = children[i] = tree
      tree = Tree()
      tree.__setstate__((tuple(children), children[0]))
      return tree, children[0]
    else:
      tree = Bucket(); items = []
      for k in keys: items += [k, None]
      tree.__setstate__((tuple(items),))
      return tree, None

  def testTraverseFrom(self):
    val = Unspecified; search = self._search 
    for k in self.keys:
      cr = search.advanceFrom(val, Unspecified)
      self.assertEqual(cr, INLIST_SUCCESS)
      self.assertEqual(search.value, k)
      val = k
    self.assertEqual(search.advanceFrom(val, Unspecified), AT_END)

  def testTraverseTo(self):
    search = self._search 
    for k in self.keys:
      self.assertEqual(search.advanceTo(k), INLIST_SUCCESS)
      self.assertEqual(search.value, k)

  def testToWithSkipping(self):
    self._check(3, 4, 25, 30, 31)

  def testToBoundaries(self):
    self._check(14, 15, 28, 30, 31, 40, 41)

  def testFromSkipping(self):
    self._check((3,4), 4, (4,25), 5, (25,26), (29,Unspecified), (30,Unspecified))

  def testFromBoundaries(self):
    self._check((14,15), (15,16), (29,31), (29,36))

  def testFromBoundaries2(self):
    self._check((15,20))

  def _check(self, *cmds):
    current = Unspecified; cr = None; set = self._set; search = self._search
    for cmd in cmds:
      args = cmd
      if isinstance(cmd, tuple): val = cmd[0]; fun = search.advanceFrom
      else: val = cmd; fun = search.advanceTo; args = cmd,
      cr = fun(*args)
      hits = set.keys(val)
      if not hits: self.assertEqual(cr, AT_END); continue
      if isinstance(cmd, tuple):
        if hits[0] == val: hits = hits[1:]
        if not hits: self.assertEqual(cr, AT_END); continue
        else:
          current = hit = hits[0]; upto = cmd[1]
          self.assertEqual(search.value, hit)
          if upto is None or hit < upto: self.assertEqual(cr, INLIST_SUCCESS)
          else: self.assertEqual(cr, INLIST)
      else:
        current = hit = hits[0]
        self.assertEqual(search.value, hit)
        self.assertEqual(cr, hit > val and INLIST or INLIST_SUCCESS)

  def testIteration(self):
    self.assertEqual(list(self._set), list(self._search))


class _ObjTestBase:
  KEYTYPE = OBJECT

class _LongTestBase:
  KEYTYPE = LONG
  SET_CLASS = LLSet


class TestOneLevel(BTreeISearchTestBase):
  keys = range(1,31)

class TestOneLevel_obj(_ObjTestBase, TestOneLevel): pass
class TestOneLevel_long(_LongTestBase, TestOneLevel): pass

class TestSecondTrivialLevel(TestOneLevel):
  split = range(2,31)

class TestSecondTrivialLevel_obj(_ObjTestBase, TestSecondTrivialLevel): pass
class TestSecondTrivialLevel_long(_LongTestBase, TestSecondTrivialLevel): pass

class TestRegularSplit(TestOneLevel):
  slit = (4, 25,)

class TestRegularSplit_obj(_ObjTestBase, TestRegularSplit): pass
class TestRegularSplit_long(_LongTestBase, TestRegularSplit): pass

class TestIrregular(BTreeISearchTestBase):
  keys = range(2,15,2) + range(15,30,2) + [31, 35, 40]
  split = (15, 30,)

class TestIrregular_obj(_ObjTestBase, TestIrregular): pass
class TestIrregular_long(_LongTestBase, TestIrregular): pass

class TestLongLargeValues(BTreeISearchTestBase):
  keys = range(1,31) + range(0x10000000, 0x10000010)
  SET_KLASS = LLSet
  


class TestTrueTree(BTreeISearchTestBase):
  # to be overridden
  keys = None
  class_ = IOBTree
  mapping = True

  def setUp(self):
    keys = self.keys
    self._set = IISet(keys)
    if self.mapping: items = map(None, keys, ())
    else: items = keys
    self._search = IBTree(self.class_(items), self.KEYTYPE)


class TestMedBTree(TestTrueTree):
  keys = range(1, 70)

class TestMedBTree_obj(TestMedBTree):
  class_ = OOBTree
  KEYTYPE = OBJECT


class _DerivedBTree(IOBTree):
  '''derived from IOBTree.'''

class TestMedDerivedBTree(TestMedBTree):
  class_ = _DerivedBTree


class TestMedBTree2(TestTrueTree):
  keys = range(1, 150, 2)

class TestMedBTree2_obj(TestMedBTree2):
  class_ = OOBTree
  KEYTYPE = OBJECT

class TestSmallBTree(TestTrueTree):
  keys = range(1,10)

class TestSmallBTree_obj(TestSmallBTree):
  class_ = OOBTree
  KEYTYPE = OBJECT


class TestBucket(TestTrueTree):
  keys = range(1, 70)
  class_ = IOBucket

class TestBucket_obj(TestBucket):
  class_ = OOBucket
  KEYTYPE = OBJECT
 
class TestTreeSet(TestTrueTree):
  keys = range(1, 500)
  class_ = IITreeSet
  mapping = False

class TestTreeSet_obj(TestTreeSet):
  class_ = OOTreeSet
  KEYTYPE = OBJECT

class TestSet(TestTreeSet):
  class_ = IISet

class TestSet_obj(TestTreeSet):
  class_ = OOSet
  KEYTYPE = OBJECT

class TestEmptyTree(TestTrueTree):
  keys = ()

  def testEstimatedSize(self):
    self.assertEqual(self._search.estimatedSize, 0)


class TestDepthThree(BTreeISearchTestBase):
  keys1 = range(2,15,2); split1 = [10]
  keys2 = range(15,30,2); split2 = [19]
  keys3 = [31, 35, 40]; split3 = [38]
  keys = keys1 + keys2 + keys3
  split = [15, 30]

  set_class_ = IISet
  tree_class_ = IOBTree

  def setUp(self):
    self._set = self.set_class_(self.keys1 + self.keys2 + self.keys3)
    mkt = self._makeTree
    tree3, leaf3 = mkt(self.set_class_(self.keys3), self.split3)
    tree2, leaf2 = mkt(self.set_class_(self.keys2), self.split2, leaf3)
    tree1, leaf1 = mkt(self.set_class_(self.keys1), self.split1, leaf2)
    tree = self.tree_class_(); split = self.split
    tree.__setstate__(((tree1, split[0], tree2, split[1], tree3), leaf1))
    self._search = IBTree(tree)

class TestDepthThree_obj(TestDepthThree):
  KEYTYPE = OBJECT
  set_class_ = OOSet
  tree_class_ = OOBTree

### Intersection tests
class IntersectionTestBase(TestCase):
  # to be overridden in deriving classes
  KEYTYPE = INT
  class_ = None
  mapping = None
  module = None

  set = range(1000)

  def testEmptyIntersection(self):
    self.assertRaises(ValueError, intersection, self.KEYTYPE)

  def testUnaryIntersection(self):
    self._check(1)

  def testEqualIntersection(self):
    self._check(1, 1)

  def testSubsetIntersection(self):
    self._check(2, 1)
    self._check(1, 2)

  def testEmptyResult(self):
    self._check(2, (2,1))

  def testTripleIntersection(self):
    self._check(2, 3, 5)

  def testSmallResult(self):
    s = [100, 200]
    self._check(s, 1)
    self._check(1, s)

  def _check(self, *args):
    args = map(self._makeSet, args)
    result = None; bti = self.module.intersection
    for set in args: result = bti(result, set)
    self.assert_(list(result.keys()) == intersection(self.KEYTYPE, *args).keys())

  def _makeSet(self, spec):
    '''make a set from *spec*.

    *spec* can be an integer (meaning: 'spec * self._set')
    a pair (*f*, *o*) (meaning 'f * self._set + o')
    or a list (meaning itself).
    '''
    set = self.set
    if isinstance(spec, int): spec = [spec * x for x in set]
    elif isinstance(spec, tuple):
      f, o = spec
      spec = [f * x + o for x in set]
    if self.mapping: spec = map(None, spec, ())
    return self.class_(spec)


class TestSetIntersection(IntersectionTestBase):
  class_ = IISet
  mapping = False
  module = BTrees.IIBTree

class TestSetIntersection_obj(TestSetIntersection):
  KEYTYPE = OBJECT
  class_ = OOSet
  module = BTrees.OOBTree

class TestSetIntersection_long(TestSetIntersection):
  KEYTYPE = LONG
  class_ = LLSet
  module = BTrees.LLBTree

class TestTreeSetIntersection(TestSetIntersection):
  class_ = IITreeSet

class TestTreeSetIntersection_obj(TestTreeSetIntersection):
  KEYTYPE = OBJECT
  class_ = OOTreeSet
  module = BTrees.OOBTree

class TestBucketIntersection(IntersectionTestBase):
  class_ = IOBucket
  module = BTrees.IOBTree
  mapping = True

class TestBucketIntersection_obj(TestBucketIntersection):
  KEYTYPE = OBJECT
  class_ = OOBucket
  module = BTrees.OOBTree

class TestBTreeIntersection(TestBucketIntersection):
  class_ = IOBTree

class TestBTreeIntersection_obj(TestBTreeIntersection):
  KEYTYPE = OBJECT
  class_ = OOBTree
  module = BTrees.OOBTree
    

def test_suite():
  md = globals()
  cls = []
  for cl in [
    TestOneLevel,
    TestSecondTrivialLevel,
    TestRegularSplit,
    TestIrregular,
    TestMedBTree,
    TestMedBTree2,
    TestSmallBTree,
    TestBucket,
    TestTreeSet,
    TestSet,
    TestDepthThree,
    TestSetIntersection,
    TestTreeSetIntersection,
    TestBucketIntersection,
    TestBTreeIntersection,
    ]:
    cls.append(cl)
    cls.append(md[cl.__name__ + '_obj'])
  for cl in [
    TestOneLevel,
    TestSecondTrivialLevel,
    TestRegularSplit,
    TestIrregular,
    TestSetIntersection,
    ]:
    cls.append(md[cl.__name__ + '_long'])
  cls.append(TestMedDerivedBTree)
  cls.append(TestEmptyTree)
  return TestSuite([makeSuite(cl) for cl in cls])

def main():
  tester = TextTestRunner()
  tester.run(test_suite())

if __name__ == '__main__': main()
