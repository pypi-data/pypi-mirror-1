# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Data structures: Heaps, lists, queues, and Python hacks.
"""

import copy, heapq, sys

class FreeStruct( object ):
    """
    General-purpose namespace structure.
    """
    def __init__( self, **args ):
        self.__dict__.update( args )

class LazyObject( object ):
    """
    An object whose attributes do nothing.

    @todo: Unfortunate name; has nothing to do with lazy
    evaluation. Check where this is used and try to rename it.
    """
    def __getattr__( self, foo ):
        return self.foo
    def foo( self, *args ):
        pass

class Enum:
    """Create an enumerated type, then add var/value pairs to it.
    The constructor and the method .ints(names) take a list of variable names,
    and assign them consecutive integers as values.    The method .strs(names)
    assigns each variable name to itself (that is variable 'v' has value 'v').
    The method .vals(a=99, b=200) allows you to assign any value to variables.
    A 'list of variable names' can also be a string, which will be .split().
    The method .end() returns one more than the maximum int value.
    Example: opcodes = Enum("add sub load store").vals(illegal=255).

    From U{http://norvig.com/python-iaq.html}.

    @copyright: Peter Norvig"""
  
    def __init__(self, names=[]): self.ints(names)

    def set(self, var, val):
        """Set var to the value val in the enum."""
        if var in vars(self).keys(): raise AttributeError("duplicate var in enum")
        if val in vars(self).values(): raise ValueError("duplicate value in enum")
        vars(self)[var] = val
        return self
  
    def strs(self, names):
        """Set each of the names to itself (as a string) in the enum."""
        for var in self._parse(names): self.set(var, var)
        return self

    def ints(self, names):
        """Set each of the names to the next highest int in the enum."""
        for var in self._parse(names): self.set(var, self.end())
        return self

    def vals(self, **entries):
        """Set each of var=val pairs in the enum."""
        for (var, val) in entries.items(): self.set(var, val)
        return self

    def end(self):
        """One more than the largest int value in the enum, or 0 if none."""
        try: return max([x for x in vars(self).values() if type(x)==type(0)]) + 1
        except ValueError: return 0
    
    def _parse(self, names):
        ### If names is a string, parse it as a list of names.
        if type(names) == type(""): return names.split()
        else: return names

# Public domain
class ListMixin(object):
  """
  Defines all list operations from a small subset of methods.

  Subclasses should define _get_element(i), _set_element(i, value),
  __len__(), _resize_region(start, end, new_size) and
  _constructor(iterable).  Define __iter__() for extra speed.

  The _get_element() and _set_element() methods are given indices with
  0 <= i < len(self).

  The _resize_region() method should resize the slice self[start:end]
  so that it has size new_size.  It is given indices such that
  start <= end, 0 <= start <= len(self) and 0 <= end <= len(self).
  The resulting elements in self[start:start+new_size] can be set to
  None or arbitrary Python values.

  The _constructor() method accepts an iterable and should return a
  new instance of the same class as self, populated with the elements
  of the given iterable.

  From U{http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/440656}.

  @copyright: Connelly Barns
  """
  def __cmp__(self, other):
    return cmp(list(self), list(other))

  def __hash__(self):
    raise TypeError('list objects are unhashable')

  def __iter__(self):
    for i in xrange(len(self)):
      yield self._get_element(i)

  def _tuple_from_slice(self, i):
    """
    Get (start, end, step) tuple from slice object.
    """
    (start, end, step) = i.indices(len(self))
    # Replace (0, -1, 1) with (0, 0, 1) (misfeature in .indices()).
    if step == 1:
      if end < start:
        end = start
      step = None
    if i.step == None:
      step = None
    return (start, end, step)

  def _fix_index(self, i):
    if i < 0:
      i += len(self)
    if i < 0 or i >= len(self):
      raise IndexError('list index out of range')
    return i

  def __getitem__(self, i):
    if isinstance(i, slice):
      (start, end, step) = self._tuple_from_slice(i)
      if step == None:
        indices = xrange(start, end)
      else:
        indices = xrange(start, end, step)
      return self._constructor([self._get_element(i) for i in indices])
    else:
      return self._get_element(self._fix_index(i))

  def __setitem__(self, i, value):
    if isinstance(i, slice):
      (start, end, step) = self._tuple_from_slice(i)
      if step != None:
        # Extended slice
        indices = range(start, end, step)
        if len(value) != len(indices):
          raise ValueError(('attempt to assign sequence of size %d' +
                            ' to extended slice of size %d') %
                           (len(value), len(indices)))
        for (j, assign_val) in enumerate(value):
          self._set_element(indices[j], assign_val)
      else:
        # Normal slice
        if len(value) != (end - start):
          self._resize_region(start, end, len(value))
        for (j, assign_val) in enumerate(value):
          self._set_element(start + j, assign_val)
    else:
      # Single element
      self._set_element(self._fix_index(i), value)

  def __delitem__(self, i):
    if isinstance(i, slice):
      (start, end, step) = self._tuple_from_slice(i)
      if step != None:
        # Extended slice
        indices = range(start, end, step)
        # Sort indices descending
        if len(indices) > 0 and indices[0] < indices[-1]:
          indices.reverse()
        for j in indices:
          del self[j]
      else:
        # Normal slice
        self._resize_region(start, end, 0)
    else:
      # Single element
      i = self._fix_index(i)
      self._resize_region(i, i + 1, 0)

  def __add__(self, other):
    if isinstance(other, self.__class__):
      ans = self._constructor(self)
      ans += other
      return ans
    return list(self) + other

  def __mul__(self, other):
    ans = self._constructor(self)
    ans *= other
    return ans

  def __radd__(self, other):
    if isinstance(other, self.__class__):
      ans = other._constructor(self)
      ans += self
      return ans
    return other + list(self)

  def __rmul__(self, other):
    return self * other

  def __iadd__(self, other):
    self[len(self):len(self)] = other
    return self

  def __imul__(self, other):
    if other <= 0:
      self[:] = []
    elif other > 1:
      aux = list(self)
      for i in xrange(other-1):
        self.extend(aux)
    return self

  def append(self, other):
    self[len(self):len(self)] = [other]

  def extend(self, other):
    self[len(self):len(self)] = other

  def count(self, other):
    ans = 0
    for item in self:
      if item == other:
        ans += 1
    return ans

  def reverse(self):
    for i in xrange(len(self)//2):
      j = len(self) - 1 - i
      (self[i], self[j]) = (self[j], self[i])

  def index(self, x, i=0, j=None):
    if i != 0 or j is not None:
      (i, j, ignore) = self._tuple_from_slice(slice(i, j))
    if j is None:
      j = len(self)
    for k in xrange(i, j):
      if self._get_element(k) == x:
        return k
    raise ValueError('index(x): x not in list')

  def insert(self, i, x):
    self[i:i] = [x]

  def pop(self, i=None):
    if i == None:
      i = len(self)-1
    ans = self[i]
    del self[i]
    return ans

  def remove(self, x):
    for i in xrange(len(self)):
      if self._get_element(i) == x:
        del self[i]
        return
    raise ValueError('remove(x): x not in list')

  # Define sort() as appropriate for the Python version.
  if sys.version_info[:3] < (2, 4, 0):
    def sort(self, cmpfunc=None):
      ans = list(self)
      ans.sort(cmpfunc)
      self[:] = ans
  else:
    def sort(self, cmpfunc=None, key=None, reverse=False):
      ans = list(self)
      if reverse == True:
        ans.sort(cmpfunc, key, reverse)
      elif key != None:
        ans.sort(cmpfunc, key)
      else:
        ans.sort(cmpfunc)
      self[:] = ans

  def __copy__(self):
    return self._constructor(self)

  def __deepcopy__(self, memo={}):
    ans = self._constructor([])
    memo[id(self)] = ans
    ans[:] = copy.deepcopy(tuple(self), memo)
    return ans

  # Tracking idea from R. Hettinger's deque class.  It's not
  # multithread safe, but does work with the builtin Python classes.
  def __str__(self, track=[]):
    if id(self) in track:
      return '...'
    track.append(id(self))
    ans = '%r' % (list(self),)
    track.remove(id(self))
    return ans

  def __repr__(self):
    return self.__class__.__name__ + '(' + str(self) + ')'


# Example usage:

class TestList(ListMixin):
  def __init__(self, L=[]):
    self.L = list(L)

  def _constructor(self, iterable):
    return TestList(iterable)

  def __len__(self):
    return len(self.L)

  def _get_element(self, i):
    assert 0 <= i < len(self)
    return self.L[i]

  def _set_element(self, i, x):
    assert 0 <= i < len(self)
    self.L[i] = x

  def _resize_region(self, start, end, new_size):
    assert 0 <= start <= len(self)
    assert 0 <= end   <= len(self)
    assert start <= end
    self.L[start:end] = [None] * new_size

# Now TestList() has behavior identical to that of list().

#############################################################################

class Heap(ListMixin):
    """
    A list that maintains the heap invariant.
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/440673

    TODO using things like pop() is unsafe! they rely on the
    unimplemented _get_element()

    TODO things like popmin() produce poor error msgs (when empty)
    """

    def __init__(self, iterable=(), key=None):
        '''
        @param iterable: An iterable over items to be added to the heap.
        @param key: Specifies a function of one argument that is used to
            extract a comparison key from each heap element.
        '''
        self._key = key
        self._lst = []
        self.extend(iterable)
        heapq.heapify(self._lst)

    def peek( self ):
        return self.get_element( 0 )

    def push(self, item):
        '''Push the item onto the heap.'''
        return heapq.heappush(self._lst, self._wrap(item))

    def popmin(self):
        '''Pop the smallest item off the heap'''
        return self._unwrap(heapq.heappop(self._lst))

    def replace(self, item):
        '''Equivalent to "x = heap.popmin(); heap.push(); return x" but more
        efficient.
        '''
        return self._unwrap(heapq.heapreplace(self._lst, self._wrap(item)))

    def pushpop(self, item):
        'Equivalent to "heap.push(); return heap.popmin()" but more efficient.'
        if self and self[0] < item:
            return self.replace(item)
        return item

    def iterpop(self):
        '''Return a destructive iterator over the heap's elements.

        Each time next is invoked, it pops the smallest item from the heap.
        '''
        while self:
            yield self.popmin()

    #---- overrided ListMixin methods ----------------------------------------

    def constructor(self, iterable):
        return self.__class__(iterable, self._key)

    def __len__(self):
        return len(self._lst)

    def get_element(self, pos):
        return self._unwrap(self._lst[pos])

    def __setitem__(self, pos, item):
        if isinstance(pos, slice):
            raise TypeError('Heap objects do no support slice setting')
        pos = self._fix_index(pos)
        item = self._wrap(item)
        lst = self._lst
        current = lst[pos]
        lst[pos] = item
        if item > current:      # re-establish the heap invariant
            heapq._siftup(lst, pos)
        if lst[pos] != item:    # item found its way below pos
            return
        while pos > 0:
            parentpos = (pos - 1) >> 1
            parent = lst[parentpos]
            if parent <= item:
                break
            lst[pos] = parent
            pos = parentpos
        lst[pos] = item

    def __delitem__(self, pos):
        if isinstance(pos, slice):
            raise TypeError('Heap objects do no support slice deleting')
        pos = self._fix_index(pos)
        lst = self._lst
        if pos == len(lst)-1:
            del lst[-1]
        else:
            self[pos] = self.pop()

    def __iter__(self):
        return itertools.imap(self._unwrap, self._lst)

    def __nonzero__(self):
        return bool(self._lst)

    def __cmp__(self, other):
        raise TypeError('Heap objects do not support comparison')

    def __eq__(self, other):
        if not isinstance(other,Heap) or len(self) != len(other):
            return False
        for i,j in itertools.izip(self,other):
            if i != j: return False
        return True

    def __ne__(self,other):
        return not self==other

    def count(self, item):
        return self._lst.count()

    append = push

    def insert(self, pos, item):
        # ignore the position since it's not certain that it can preserve the
        # heap invariant
        self.push(item)

    def extend(self, other):
        if self._key is not None:
            other = itertools.imap(self._wrap, other)
        push = heapq.heappush; lst = self._lst
        for item in other:
            push(lst,item)

    def sort(self):
        lst = self._lst; pop = heapq.heappop
        sorted = []; append = sorted.append
        while lst:
            append(pop(lst))
        self._lst = sorted

    def reverse(self):
        raise TypeError('Heap objects do not support reversal')

    #---- 'private' methods --------------------------------------------------

    def _wrap(self, item):
        if self._key is not None:
            item = (self._key(item),item)
        return item

    def _unwrap(self, item):
        if self._key is not None:
            item = item[1]
        return item

#############################################################################

class Queue( object ):
    """
    A first-in-first-out queue.

    Based on U{http://www.norvig.com/python-iaq.html}.

    @copyright: Peter Norvig
    """
    def __init__(self, items=None, thresh=100): self.start = 0; self.A = items or []; self.thresh = thresh
    def __len__(self):                return len(self.A) - self.start
    def append(self, item):           self.A.append(item)
    def extend(self, items):          self.A.extend(items)
    def peek(self):                   return self.A[self.start]
    def __iter__( self ):            return iter(self.A[self.start:])
    def __repr__( self ):
        return 'Queue(%s)' % ( repr( self.A[ self.start : ] ), )
    def __str__( self ):
        return str( self.A[ self.start : ] )
    def pop(self):
        A = self.A
        item = A[self.start]
        self.start += 1
        if self.start > self.thresh and self.start > len(A)/2:
            del A[:self.start]
            self.start = 0
        return item

