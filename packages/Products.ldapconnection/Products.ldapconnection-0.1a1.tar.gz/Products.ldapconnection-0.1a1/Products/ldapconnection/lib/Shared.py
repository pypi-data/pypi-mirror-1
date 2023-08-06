#	$Id:$
'''Shared Resource.

Usually, each thread has its own data to minimize interference
and to localize synchonization in the transaction commit.

However, this makes it difficult to control such data from
a single point. E.g. it is very difficult to invalidate
cache entries: while there is no problem for a thread to
invalidate entries in its own cache, it is very difficult
to do the same with the corresponding caches in the other
threads.

'Shared Resource' is a module that manages resources
shared by all threads. Such resources can be controlled
much more easily. A shared resource provides
locking capabilities (via Python s RLock) and performs
automatic locking for function calls.
Access to non-functions is not protected.

A shared resource is identified by an id. The application
is responsible that id s are unique.

Shared resources are not persistent.
Currently, they do not support acquisition. This may change however.
'''

from threading import _RLock, Lock
from sys import stdout

_ResourceMap= {}
_ResourceLock= Lock()

def getResource(id, creator, createArguments=()):
  '''returns a resource for *id*.

  If such a resource does not yet exist, one is created
  by calling *creator* with *createArguments*.
  Note, that *creator* and *createArguments* should only
  depend on *id* and not any other context, as no
  object is created, when a resource for *id* already
  exists.
  '''
  _ResourceLock.acquire()
  try:
    if _ResourceMap.has_key(id): return _ResourceMap[id]
    r= apply(creator,createArguments)
    _ResourceMap[id]= r= _WrapResource(r)
    return r
  finally: _ResourceLock.release()


class _WrapResource(_RLock):
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

  def __init__(self,target):
    self._target= target
    _RLock.__init__(self)

  def __getattr__(self,key):
    a= getattr(self._target,key)
    if callable(a): a= _WrapCallable(self,a)
    return a

  def __setattr__(self,key,value):
    if self._isMyAttribute(key): self.__dict__[key]= value
    else:
      setattr(self._target,key,value)

  # def __delattr__(self,key,value): # do not implement for the time being

  def __len__(self): return len(self._target)
  def __getitem__(self,key): return self._target[key]
  def __setitem__(self,key,value): self._target[key]= value
  def __delitem__(self,key): del self._target[key]


class _WrapCallable:
  def __init__(self,lock,callable):
    self._lock= lock; self._callable= callable

  def __call__(self,*args,**kw):
    self._lock.acquire()
    try: return apply(self._callable,args,kw)
    finally: self._lock.release()


