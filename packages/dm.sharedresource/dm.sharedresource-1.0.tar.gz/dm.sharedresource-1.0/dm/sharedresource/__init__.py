# Copyright (C) 2000-2008 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Eppelborn, Germany
# see "LICENSE.txt" for details
"""Shared Resource.

"Shared Resource" manages resources shared by all threads.

A resource is identified by an id and can be obtained by "get_resource".
"get_resource" will create a new resource, if no resource with
the given id exists.

The resource returned is not the resource itself but a wrapper
that synchronizes all calls to the resource's methods.
Therefore, several threads can safely call resource methods.
"""

from threading import _RLock, Lock

def get_resource(id, creator, *create_args, **create_kw):
  """return a resource for *id*.

  If such a resource does not yet exist, one is created
  by calling *creator* with *create_args* and *create_kw*.

  Note, that *creator*, *create_args* and *create_kw* should only
  depend on *id* and not any other context, as no
  object is created, when a resource for *id* already
  exists.

  *id* must be hashable and support equality tests.
  """
  _ResourceLock.acquire()
  try:
    if _ResourceMap.has_key(id): return _ResourceMap[id]
    r= creator(*create_args, **create_kw)
    _ResourceMap[id]= r= _WrapResource(r)
    return r
  finally: _ResourceLock.release()

_ResourceMap= {}
_ResourceLock= Lock()


class _WrapResource(_RLock):
  """Resource wrapper causing method calls on the resource to be synchronized.
  """
  # for __setattr__
  _myAttributes= { '_target' : None,
		   # _RLock instance variables
		   '_RLock__block' : None,
		   '_RLock__count' : None,
		   '_RLock__owner' : None,
		   # Verbose instance variables
		   '_Verbose__verbose' : None,
		   }
  _myAttributes.update(_RLock.__dict__)
  _isMyAttribute= _myAttributes.has_key
  _target= None

  def __init__(self, target):
    self._target= target
    _RLock.__init__(self)

  def __getattr__(self, key):
    self.acquire()
    try: a = getattr(self._target, key)
    finally: self.release()
    if callable(a): a = _WrapCallable(self, a)
    return a

  def __setattr__(self, key, value):
    if self._isMyAttribute(key): self.__dict__[key] = value
    else:
      self.acquire()
      try: setattr(self._target, key, value)
      finally: self.release()

  def _synchronize(f):
    """call *f* under a lock protection."""
    def wrapper(self, *args, **kw):
      self.acquire()
      try: return f(self, *args, **kw)
      finally: self.release()
    return wrapper

  @_synchronize
  def __len__(self): return len(self._target)
  @_synchronize
  def __nonzero__(self): return self._target.__nonzero__()
  @_synchronize
  def __str__(self): return str(self._target)
  @_synchronize
  def __getitem__(self, index): return self._target[index]
  @_synchronize
  def __setitem__(self, index, value): self._target[index] = value
  @_synchronize
  def __delitem__(self, index): del self._target[index]


class _WrapCallable:
  """A wrapper around a callable which synchronize calls to it."""
  
  def __init__(self, lock, callable):
    self.__lock = lock
    self.__callable = callable

  def __call__(self, *args, **kw):
    self.__lock.acquire()
    try: return self.__callable(*args, **kw)
    finally: self.__lock.release()
