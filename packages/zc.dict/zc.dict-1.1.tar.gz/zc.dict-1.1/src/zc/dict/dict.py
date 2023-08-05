##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""zc.dict -- A BTree based persistent mapping

$Id: dict.py 77395 2007-07-04 14:56:33Z alga $
"""
from BTrees.OOBTree import OOBTree
from BTrees.Length import Length
from persistent import Persistent


class Dict(Persistent):
    """A BTree-based dict-like persistent object that can be safely
    inherited from.
    """

    def __init__(self, dict=None, **kwargs):
        self._data = OOBTree()
        self._len = Length()
        if dict is not None:
            self.update(dict)
        if len(kwargs):
            self.update(kwargs)

    def __setitem__(self, key, value):
        delta = 1
        if key in self._data:
            delta = 0
        self._data[key] = value
        if delta:
            self._len.change(delta)

    def __delitem__(self, key):
        del self._data[key]
        self._len.change(-1)

    def update(self, other):
        for k, v in other.iteritems():
            self[k] = v

    def clear(self):
        self._data.clear()
        self._len.set(0)

    def __len__(self):
        return self._len()

    def keys(self):
        return list(self._data.keys())

    def values(self):
        return list(self._data.values())

    def items(self):
        return list(self._data.items())

    def copy(self):
        if self.__class__ is Dict:
            return Dict(OOBTree(self._data))
        import copy
        data = self._data
        try:
            self._data = OOBTree()
            c = copy.copy(self)
        finally:
            self._data = data
        c.update(self)
        return c

    def __getitem__(self, key): return self._data[key]
    def __iter__(self): return iter(self._data)
    def iteritems(self): return self._data.iteritems()
    def iterkeys(self): return self._data.iterkeys()
    def itervalues(self): return self._data.itervalues()
    def has_key(self, key): return bool(self._data.has_key(key))
    def get(self, key, failobj=None): return self._data.get(key, failobj)
    def setdefault(self, key, failobj=None): self._data.setdefault(key, failobj)
    def pop(self, key, *args): return self._data.pop(key, *args)
    def __contains__(self, key): return self._data.__contains__(key)

    def popitem(self):
        try:
            k, v = self.iteritems().next()
        except StopIteration:
            raise KeyError, 'container is empty'
        del self[k]
        return (k, v)

