# Copyright (C) 2005-2008 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
#       $Id: __init__.py,v 1.1.1.1 2008/06/27 19:21:39 dieter Exp $
""""dm.incrementalsearch"

Incremental search is an efficient low level search execution engine
on top of "ZODB.BTrees". Its primary purpose is to incrementally
perform searches involving "and", "or" and "not" queries over
"ZODB.BTrees".

Incremental search is highly efficient for specific "and" queries
because it interleaves index lookup with the incremental determination
of hits. Often only small parts of the document lists involved
in the query need to be read. This can drastically reduce
the amount of loads and therefore IO which usually dominates
the total search time at least in distributed ZEO environments.
Furthermore, it makes more efficient use of the various ZODB
caches.


**ATTENTION** "incrementalsearch" is likely to fail when you
enumerate a "XXBTree" containing "None". This is caused by
a bug in the "XXBTree.keys(minKey, maxKey)" specification
which interprets a "None" value for "minKey" and "maxKey"
as "no restriction".


The central concept in the incremental search framework
is the "ISearch". An "ISearch" is similar to an iterator over
a sorted list of keys. Unlike an iterator, "ISearch"
has two methods to move forward over the list:
"advanceTo(key)" and
"advanceFrom(fromKey, limitKey)".
"advanceTo" tries to move (forward) in the sorted list to "key",
"advanceFrom" tries to move (forward) to the smallest key in the list
which is larger than "fromKey". The sorted list over which an
"ISearch" iterates is usually not yet fully materialized but
computed incrementally. Because the determination of the next
list element can be expensive, "limitKey" can be used to
indicate that only keys in the open interval between "fromKey"
and "limitKey" are of interest. There is a constant "Unspecified"
which can be passed as argument for "fromKey" or "limitKey".
When used for "fromKey", it is considered smaller than any key
in the list; when used for "limitKey", it is considered larger than
any key in the list.


"advanceTo" and "advanceFrom" are only allowed to move forward
in the following precise sense:

  1. when *key* is passed as argument to "advanceTo" (for an
     "ISearch" instance), then any value later passed
     as "key" to "advanceTo" or as "fromKey" to "advanceFrom"
     (for this same "ISearch" instance) must not be smaller
     than *key*

  2. when *fromKey* is passed as argument to "advanceFrom" (for an
     "ISearch" instance), then any value later passed
     as "key" to "advanceTo" or as "fromKey" to "advanceFrom"
     (for this same "ISearch" instance) must be (strictly) larger
     than *fromKey*.

A debug version may check this condition and raise an exception.
However, an "ISearch" is explicitely entitled to assume this
condition without check (and therefore to deliver wrong results
if the condition is not fullfilled).


An "ISearch" has two attributes "value" and "classification".
"value" indicates the instances current value, "classification"
provides information about whether "value" is in the list.
"classification" can have the following increasing integer constants as values:

  "INLIST_SUCCESS" (the integer 0) -- "value" is in the list (and the
    last call to an "advance*" method (for this instance)
    was "completely successful").

  "INLIST" -- "value" is in the list  (but  the
    last call to an "advance*" method (for this instance)
    was not "completely successful").

  "CANDIDATE" -- "value" may or may not be in the list.

  "NOT_INLIST" -- "value" is no longer valid
    Note: "advanceFrom" must not return this value

  "AT_START" -- iteration over the list has not yet started, "value" is undefined

  "AT_END" -- the list is exhausted, there are no more hits, "value" is undefined, no more "advance*" calls are allowed.

For convenience, the "advance*" methods return the classification value.


The "ISearch" attribute "keytype" can have the constants "INT"
and "OBJECT" as values. When "ISearch" instances are combined,
their "keyType" must be the same.

"ISearch" has the attribute "estimatedSize" containing an estimation
of the underlying lists size or "-1", if no reasonable estimation
can be obtained. It is used only for optimization heuristics.
"ISearch" may grow further attributes for optimization in the future.


The "ISearch" method "asSet" returns all (remaining) elements
in the underlying list as an "IISet" or "OOSet" (depending on
"keyType"). Note that for efficiency reasons, the "asSet" method
of "IBTree" returns the tree itself (which might not be a set).
"""

__all__ = (
  'ISearch IBTree '
  'IAnd IAnd_int IAnd_obj IAnd_long'
  'IOr IOr_int, IOr_obj IOr_long'
  'INot '
  'IFilter IFilter_int IFilter_obj IFilter_long'
  'INT OBJECT '
  'Unspecified '
  'INLIST_SUCCESS INLIST CANDIDATE NOT_INLIST AT_START AT_END '
  'Enumerator '
  'intersection intersection_int, intersection_obj intersection_long'
  ).split()

# the classification values -- must agree with 'enum Classification' in
# "ISearch.h"
INLIST_SUCCESS = 0
INLIST = 1
CANDIDATE = 2
NOT_INLIST = 3
AT_START = 4
AT_END = 5

# the keytype values -- must agree with 'enum Keytype' in "ISearch.h"
# UNDEFINED = 0
INT = 1
OBJECT = 2
LONG = 3


import ZODB # for "cPersistence"
from _isearch import ISearch, Unspecified, _IBTree, _IAnd, _IOr


##############################################################################
##############################################################################
## "BTrees" as incremental searches
##############################################################################
##############################################################################

from inspect import getmro

from BTrees.OOBTree import OOBTree, OOBucket, OOSet, OOTreeSet
from BTrees.IOBTree import IOBTree, IOBucket, IOSet, IOTreeSet
from BTrees.OIBTree import OIBTree, OIBucket, OISet, OITreeSet
from BTrees.IIBTree import IIBTree, IIBucket, IISet, IITreeSet
from BTrees.IFBTree import IFBTree, IFBucket, IFSet, IFTreeSet
from BTrees.LOBTree import LOBTree, LOBucket, LOSet, LOTreeSet
from BTrees.OLBTree import OLBTree, OLBucket, OLSet, OLTreeSet
from BTrees.LLBTree import LLBTree, LLBucket, LLSet, LLTreeSet
from BTrees.LFBTree import LFBTree, LFBucket, LFSet, LFTreeSet


# classification: type -> (maxLeafSize, maxNodeSize, keyType)
# size values from C code

_btree_classifier = {
  type(OOBTree()) : (30, 250, OBJECT,),
  type(IOBTree()) : (60, 500, INT,),
  type(OIBTree()) : (60, 250, OBJECT,),
  type(IIBTree()) : (120, 500, INT,),
  type(IFBTree()) : (120, 500, INT,),
  type(LOBTree()) : (60, 500, LONG,),
  type(OLBTree()) : (60, 250, OBJECT,),
  type(LLBTree()) : (120, 500, LONG,),
  type(LFBTree()) : (120, 500, LONG,),
  type(OOBucket()) : (0, 0, OBJECT,),
  type(IOBucket()) : (0, 0, INT,),
  type(OIBucket()) : (0, 0, OBJECT,),
  type(IIBucket()) : (0, 0, INT,),
  type(IFBucket()) : (0, 0, INT,),
  type(LOBucket()) : (0, 0, LONG,),
  type(OLBucket()) : (0, 0, OBJECT,),
  type(LLBucket()) : (0, 0, LONG,),
  type(LFBucket()) : (0, 0, LONG,),
  type(OOTreeSet()) : (30, 250, OBJECT,),
  type(IITreeSet()) : (30, 250, INT,),
  type(LLTreeSet()) : (30, 250, LONG,),
  type(OOSet()) : (0, 0, OBJECT,),
  type(IISet()) : (0, 0, INT,),
  type(LLSet()) : (0, 0, LONG,),
  }

def classifyBTree(tree):
  '''classify *tree*.

  raises a 'TypeError' when *tree* does not derive from
  a known 'BTree' type.
  '''
  cl = _btree_classifier
  for t in getmro(type(tree)):
    if t in cl: return cl[t]
  raise TypeError("not derived from a supported 'BTrees' type")


class IBTree(_IBTree):
  '''some BTrees instance as an incremental search.'''
  def __init__(self, btree, keytype=None):
    # raise exception, if type unknown
    maxLeafSize, maxNodeSize, keyType = classifyBTree(btree)
    if keytype is None: keytype = keyType
    elif keytype != keyType:
      raise TypeError('Incompatible key types')
    _IBTree.__init__(self, keytype, btree,
                     3 * maxNodeSize // 4,
                     3 * maxLeafSize // 4,
                     )


##############################################################################
##############################################################################
## "IAnd" and "IOr"
##############################################################################
##############################################################################


class _MultiSearch(object):
  '''abstract base class for 'IAnd' and 'IOr'.

  A combined search over one or more ISearches.
  '''

  _searches = None

  def __init__(self, keytype, *searches):
    self._keytype = keytype
    self._searches = []
    for s in searches: self.addSearch(s)
  
  def addSearch(self, search):
    if self._keytype != search.keytype:
      raise ValueError('disagreeing keytypes')
    self._searches.append(search)

  def complete(self):
    raise NotImplementedError


class _IEmpty(ISearch):
  '''the empty ISearch.'''
  def __init__(self, keytype):
    ISearch.__init__(self, keytype)
    self.classification = AT_END
    self.estimatedSize = 0

  def advanceTo(self, to): return AT_END
  def advanceFrom(self, start, limit): return AT_END


class IAnd(_MultiSearch, _IAnd):
  '''the incremental and of one or more ISearches.'''
  def complete(self):
    searches = self._searches
    if searches is None:
      raise ValueError("must not call 'complete' twice")
    # eliminate nested ands and ors with less than 2 elements.
    i = 0
    while i < len(searches):
      search = searches[i]
      if isinstance(search, _IEmpty) \
         or isinstance(search, IOr) and not search.size:
        searches[:] = [_IEmpty(self._keytype)]; break
      if isinstance(search, _IOr) and search.size == 1:
        searches[i] = search.unmantle()[0]; continue
      if isinstance(search, _IAnd):
        searches[i:i+1] = search.unmantle(); continue
      i += 1
    # order by increasing size -- indeterminate is considered very large
    # also estimate size as the minimal size
    from sys import maxint
    l = []; estimatedSize = maxint
    for s in searches:
      size = s.estimatedSize
      if size < 0: size = maxint
      elif size < estimatedSize: estimatedSize = size
      l.append((size, s))
    l.sort()
    if estimatedSize == maxint: estimatedSize = -1 # no useful estimation
    del self._searches # prevent a second use
    _IAnd.__init__(self, self._keytype, [ss[1] for ss in l])
    self.estimatedSize = estimatedSize
    self.size = len(l)

class IAnd_int(IAnd):
  ''''IAnd' specialization for 'INT' keys.'''
  def __init__(self, *searches):
    IAnd.__init__(self, INT, *searches)

class IAnd_obj(IAnd):
  ''''IAnd' specialization for 'OBJECT' keys.'''
  def __init__(self, *searches):
    IAnd.__init__(self, OBJECT, *searches)

class IAnd_Long(IAnd):
  ''''IAnd' specialization for 'LONG' keys.'''
  def __init__(self, *searches):
    IAnd.__init__(self, LONG, *searches)

class IOr(_MultiSearch, _IOr):
  '''the incremental or of zero or more ISearches.'''
  def complete(self):
    searches = self._searches
    # eliminate nested ors and one element ands
    i = 0
    while i < len(searches):
      search = searches[i]
      if isinstance(search, _IEmpty): del searches[i]; continue
      if isinstance(search, _IAnd) and search.size == 1:
        searches[i] = search.unmantle()[0]; continue
      if isinstance(search, _IOr):
        searches[i:i+1] = search.unmantle(); continue
      i += 1
    # order be descreasing size -- indeterminate is considered very small
    # estimate the size as the sum of the determinate sizes
    l = []; estimatedSize = 0; indeterminate = True
    for s in searches:
      size = s.estimatedSize
      if size >= 0: indeterminate = False; estimatedSize += size
      l.append((size, s))
    l.sort(); l.reverse()
    del self._searches # prevent a second use
    _IOr.__init__(self, self._keytype, [ss[1] for ss in l])
    self.estimatedSize = estimatedSize
    self.size = len(l)

class IOr_int(IOr):
  ''''IOr' specialization for 'INT' keys.'''
  def __init__(self, *searches):
    IOr.__init__(self, INT, *searches)

class IOr_obj(IOr):
  ''''IOr' specialization for 'OBJECT' keys.'''
  def __init__(self, *searches):
    IOr.__init__(self, OBJECT, *searches)


##############################################################################
##############################################################################
## INot
##############################################################################
##############################################################################


class INot(ISearch):
  _search = None

  def __init__(self, search, enumerator=None):
    ISearch.__init__(self, search.keytype)
    self._search = search
    self._enumerator = enumerator

  def advanceTo(self, to):
    '''we assume without check that *to* is in the domain.'''
    search = self._search; self.value = to
    if search is None: cl = INLIST_SUCCESS
    else:
      cl = search.advanceTo(to)
      if cl == AT_END: del self._search
      cl = cl == INLIST_SUCCESS and NOT_INLIST or INLIST_SUCCESS
    self.classification = cl
    return cl

  def advanceFrom(self, fromKey, limitKey):
    search = self._search; enumerator = self._enumerator
    next = fromKey
    while True:
      next = enumerator.next(next)
      if next is Unspecified: cl = AT_END; break
      if limitKey is not Unspecified and cmp(next, limitKey) >= 0:
        cl = CANDIDATE; break
      if search is None: cl = INLIST_SUCCESS; break
      cl = search.advanceTo(next)
      if cl == AT_END: del self._search
      if cl != INLIST_SUCCESS: cl = INLIST_SUCCESS; break
    if cl != AT_END: self.value = next
    self.classification = cl
    return cl


##############################################################################
##############################################################################
## IFilter
##############################################################################
##############################################################################


class IFilter(ISearch):

  def __init__(self, keytype, filter, enumerator=None):
    ISearch.__init__(self, keytype)
    self._filter = filter
    self._enumerator = enumerator

  def advanceTo(self, to):
    '''we assume without check that *to* is in the domain.'''
    filter = self._filter; self.value = to
    fr = filter(to)
    if fr: cl = INLIST_SUCCESS
    else: cl = NOT_INLIST
    self.classification = cl
    return cl

  def advanceFrom(self, fromKey, limitKey):
    filter = self._filter; enumerator = self._enumerator
    next = fromKey
    while True:
      next = enumerator.next(next)
      if next is Unspecified: cl = AT_END; break
      if limitKey is not Unspecified and cmp(next, limitKey) >= 0:
        cl = CANDIDATE; break
      fr = filter(next)
      if fr: cl = INLIST_SUCCESS; break
    if cl != AT_END: self.value = next
    self.classification = cl
    return cl

class IFilter_int(IFilter):
  ''''IFilter' specialization for 'INT' keys.'''
  def __init__(self, filter, enumerator=None):
    IFilter.__init__(self, INT, filter, enumerator)

class IFilter_obj(IFilter):
  ''''IFilter' specialization for 'OBJECT' keys.'''
  def __init__(self, filter, enumerator=None):
    IFilter.__init__(self, OBJECT, filter, enumerator)

class IFilter_long(IFilter):
  ''''IFilter' specialization for 'OBJECT' keys.'''
  def __init__(self, filter, enumerator=None):
    IFilter.__init__(self, LONG, filter, enumerator)


##############################################################################
##############################################################################
## Enumerator
##############################################################################
##############################################################################

class Enumerator(object):
  '''turn a 'BTrees' object into a document enumerator.

  Note, this fails if the tree contains 'None' as key (bug in
  the 'BTrees' specification.
  '''
  def __init__(self, btree):
    self._tree = btree

  def check(self, elem):
    return self._tree.has_key(elem)

  def next(self, elem):
    if elem is Unspecified: elem = None
    candidates = self._tree.keys(elem)
    # from ZODB 3.3 on, we can specify that we do not want "elem"
    if not candidates: return Unspecified
    candidate = candidates[0]
    if candidate != elem: return candidate
    try: return candidates[1]
    except IndexError: return Unspecified
  



##############################################################################
##############################################################################
## intersection
##############################################################################
##############################################################################

def intersection(keytype, *sets):
  '''the intersection of *sets*.

  *sets* must not be empty; any set must agree with *keytype*.
  '''
  iand = IAnd(keytype, *[IBTree(set, keytype) for set in sets])
  iand.complete()
  return iand.asSet()

def intersection_int(*sets):
  return intersection(INT, *sets)

def intersection_obj(*sets):
  return intersection(OBJECT, *sets)

def intersection_long(*sets):
  return intersection(LONG, *sets)

