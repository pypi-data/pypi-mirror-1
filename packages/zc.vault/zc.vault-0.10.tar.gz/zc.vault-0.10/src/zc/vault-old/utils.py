import BTrees.IOBTree
import Persistent

import zope.interface
import zope.interface.common.sequence

try:
    any
except NameError:
    def any(iterable):
        for element in iterable:
            if element:
                return True
        return False


class BTreeReadSequence(persistent.Persistent):

    zope.interface.implements(zope.interface.common.sequence.IFiniteSequence)

    def __init__(self):
        self._data = BTrees.IOBTree.IOBTree()

    def __len__(self):
        if self._data:
            return self._data.maxKey() + 1
        else:
            return 0

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, stride = key.indices(len(self))
            if stride==1:
                return self._data.values(start, stop, excludemax=True)
            else:
                def gen():
                    pos = start
                    while pos < stop:
                        yield self._data[pos]
                        pos += stride
                return gen()
        elif key < 0:
            effective_key = len(self) + key
            if effective_key < 0:
                raise IndexError(key)
            return self._data[effective_key]
        elif key >= len(self):
            raise IndexError(key)
        else:
            return self._data[key]

    def __iter__(self):
        return iter(self._data.values())
