
import persistent
import BTrees.IOBTree
import BTrees.OIBTree
import zope.interface

import zc.freeze
import zc.vault.relationship
import zc.vault.interfaces

class ITokenCollection(zope.interface.Interface):
    """changes should fire TokensAdded, TokensRemoved, TokensReplaced,
    and OrderChanged events on pertinent changes to these objects"""

    relationship = zope.interface.Attribute('an ICollectionRelationship')

    members = zope.interface.Attribute(
        'an IOBTree of the tokens in the collection.')

    def copy(self):
        "return a non-frozen copy"

    def __eq__(self, other):
        "return whether other is equal in data to this collection"

    def __ne__(self, other):
        "return whether other is not equal in data to this collection"

class ICollectionRelationship(zc.vault.interfaces.IHierarchyRelationship):

    collection = zope.interface.Attribute('an ITokenCollection')

class approvalmethod(object):

    def __init__(self, reindex=False):
        self.reindex = reindex

    def __call__(self, func):
        self.func = func
        return self.wrapper

    def wrapper(self, wself, *args, **kwargs):
        manifest = None
        rel = wself.relationship
        if rel is not None:
            revision = rel.revision
            if revision is not None:
                if rel.token is None:
                    raise ValueError(
                        'cannot change collection without token on '
                        'relationship')
                revision.checkRelationshipChange(rel)
        self.func(wself, *args, **kwargs)
        if self.reindex and revision is not None:
            revision.reindex(rel)

class Relationship(zc.vault.relationship.Relationship):
    zope.interface.implements(ICollectionRelationship)

    def __init__(self, token=None, name=None, collection=None):
        super(Relationship, self).__init__(token, name)
        if collection is not None:
            self.collection = collection

    _collection = None
    @property
    def collection(self):
        return self._collection
    @zc.freeze.setproperty
    def collection(self, value):
        if not value._z_frozen and value.relationship is not None:
            raise ValueError(
                "non-frozen collection's relationship must be None initially")
        self._collection = value

    @property
    def children(self):
        return self.collection.children

    def equalData(self, other):
        return (super(Relationship, self).equalData(other) and
                getattr(other, 'collection', None) is not None and
                other.collection == self.collection)

    def _copyImmutables(self, source_manifest, token=None, **kwargs):
        if self._collection._z_frozen:
            kwargs['collection'] = self._collection
        return super(Relationship, self)._copyImmutables(
            source_manifest, token, **kwargs)

    def copy(self, source_manifest, token=None):
        # OVERRIDE if you add more dynamic values
        res = self._copyImmutables(source_manifest, token)
        res.collection = self._collection.copy()
        return res
        
    def _z_freeze(self):
        super(Relationship, self)._z_freeze()
        if not self.collection._z_frozen:
            self.collection._z_freeze()


class AbstractTokenCollection(persistent.Persistent, zc.freeze.Freezing):
    zope.interface.implements(ITokenCollection)

    def copy(self):
        return self.__class__(self)

    def __contains__(self, value):
        return value in self.children

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return bool(self.children)


class UniqueSequence(AbstractTokenCollection):

    def __init__(self, vals=None):
        self.children = BTrees.IOBTree.IOTreeSet()
        self.data = persistent.list.PersistentList()
        if vals:
            self.extend(vals)

    # Read API

    def __len__(self):
        return len(self.data)

    def count(self, item):
        return item in self.children

    def __iter__(self):
        return iter(self.data)

    def index(self, value):
        return self.data.index(value)

    def __getitem__(self, index):
        return self.data.__getitem__(index)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.data == other.data

    # Write API

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def append(self, value):
        if value in self.children:
            raise ValueError('item already in collection')
        self.data.append(value)
        self.children.insert(value)
        zope.event.notify(zc.vault.interfaces.ObjectsAdded((value,), self))

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def insert(self, index, value):
        if value in self.children:
            raise ValueError('item already in collection')
        self.data.insert(index, value)
        self.children.insert(value)
        zope.event.notify(zc.vault.interfaces.ObjectsAdded((value,), self))

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def __delitem__(self, index):
        if not isinstance(index, slice):
            removed = self.data.__getitem__(index)
        else:
            removed = (self.data.__getitem__(index),)
        for v in removed:
            self.children.remove(v)
        self.data.__delitem__(index)
        zope.event.notify(zc.vault.interfaces.ObjectsRemoved(removed, self))

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def extend(self, iterable):
        vals = tuple(iterable)
        treeset = BTrees.IOBTree.IOTreeSet(vals)
        if len(treeset) != len(vals):
            raise ValueError('duplicate values in iterable')
        if BTrees.IOBTree.intersection(treeset, self.children):
            raise ValueError('item already in collection')
        self.data.extend(vals)
        self.children.update(vals)
        zope.event.notify(zc.vault.interfaces.ObjectsAdded(vals, self))

    __iadd__ = extend

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def pop(self, index=-1):
        res = self.data.pop(index)
        self.children.remove(res)
        zope.event.notify(zc.vault.interfaces.ObjectsRemoved((res,), self))
        return res

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def remove(self, item):
        self.data.remove(item)
        self.children.remove(item)
        zope.event.notify(zc.vault.interfaces.ObjectsRemoved((item,), self))

    @zc.freeze.method
    @approvalmethod()
    def reverse(self):
        old = tuple(self.data)
        self.data.reverse()
        zope.event.notify(zc.vault.interfaces.OrderChanged(old, self))

    @zc.freeze.method
    @approvalmethod()
    def sort(self, cmpfunc=None):
        old = tuple(self.data)
        self.data.sort()
        zope.event.notify(zc.vault.interfaces.OrderChanged(old, self))

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def __setitem__(self, index, value):
        if isinstance(index, slice):
            value = tuple(value)
            treeset = BTrees.IOBTree.IOTreeSet(vals)
            if len(treeset) != len(vals):
                raise ValueError('duplicate values in iterable')
            removed = BTrees.IOBTree.IOTreeSet(self.data.__getitem__(index))
            if BTrees.IOBTree.intersection(
                treeset,
                BTrees.IOBTree.difference(
                    self.children, removed)):
                raise ValueError('item already in collection')
            self.children.update(value)
            if removed:
                zope.event.notify(
                    zc.vault.interfaces.ObjectsRemoved(removed, self))
            zope.event.notify(
                zc.vault.interfaces.ObjectsAdded(value, self))
        else:
            if value in self.children:
                if self.data.index(value) is index:
                    return
                raise ValueError('item already in collection')
            self.children.insert(value)
            zope.event.notify(
                zc.vault.interfaces.ObjectsRemoved(
                    (self.data[index],), self))
            zope.event.notify(
                zc.vault.interfaces.ObjectsAdded((value,), self))
        self.data.__setitem__(index, value)


class Set(AbstractTokenCollection):
    
    def __init__(self, vals=None):
        self.children = BTrees.IOTreeSet()
        self._length = BTrees.Length()
        if vals:
            self.update(vals)

    def __iter__(self):
        return iter(self.children)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.children == other.children)

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def add(self, value):
        if value not in self:
            self.children.insert(value)
            self._length.change(1)
            zope.event.notify(zc.vault.interfaces.ObjectsAdded((value,), self))

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def clear(self):
        old = tuple(self.children)
        if old:
            self.children.clear()
            self._length.set(0)
            zope.event.notify(zc.vault.interfaces.ObjectsRemoved(old, self))

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def discard(self, value):
        if value in self:
            self.children.remove(value)
            self._length.change(-1)
            zope.event.notify(
                zc.vault.interfaces.ObjectsRemoved((value,), self))

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def pop(self):
        if not self.children:
            raise KeyError('pop from an empty set')
        else:
            res = self.children.minKey()
            self.remove(res) # this fires an event internally
            return res

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def remove(self, value):
        self.children.remove(value) # raises KeyError
        self._length.change(-1)
        zope.event.notify(
            zc.vault.interfaces.ObjectsRemoved((value,), self))

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def update(self, value):
        old = BTrees.IOBTree.IOTreeSet(self.children)
        self.children.update(value)
        diff = BTrees.IOBTree.difference(old, self.children)
        if diff:
            # don't try to be too smart
            self._length.set(len(self.children))
            zope.event.notify(
                zc.vault.interfaces.ObjectsAdded(diff, self))

    def __len__(self):
        return self._length()

class Mapping(AbstractTokenCollection):

    def __init__(self, vals=None):
        self.data = BTrees.OIBTree.OIBTree()
        self.children = BTrees.IOBTree.IOBTree()
        self._length = Length.Length()
        if vals:
            self.update(vals)

    def __len__(self):
        return self._length.value

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)

    def items(self):
        return self.data.items()

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def __iter__(self):
        return iter(self.data)

    def __contains__(self, key):
        return key in self.data

    has_key = __contains__

    def getKey(self, value, default=None):
        if not isinstance(value, int):
            return default
        return self.children.get(value, default)

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def __delitem__(self, key):
        old = self._delitem(key)
        zope.event.notify(zc.vault.interfaces.ObjectsRemoved((old,), self, (key,)))

    def _delitem(self, key):
        old = self.data.pop(key)
        self.children.pop(old)
        self._length.change(-1)
        return old

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def __setitem__(self, key, value):
        old_value = self._setitem(key, value)
        if old_value == value:
            pass
        elif old_value is not None:
            zope.event.notify(zc.vault.interfaces.ObjectsReplaced(
                (old_value,), (value,), self, (key,)))
        else:
            zope.event.notify(
                zc.vault.interfaces.ObjectsAdded((value,), self, (key,)))

    def _setitem(self, key, value):
        bad = False
        if isinstance(key, basestring):
            try:
                unicode(key)
            except UnicodeError:
                bad = True
        else:
            bad = True
        if bad: 
            raise TypeError("'%s' is invalid, the key must be an "
                            "ascii or unicode string" % key)
        if not isinstance(value, int):
            raise ValueError("The value must be an integer")
        old_key = self.children.get(value)
        if old_key is not None:
            if old_key != key:
                raise ValueError('item already in collection')
            return value
        else:
            old_value = self.data.get(key)
            if old_value is None:
                self._length.change(1)
            else:
                assert self.children.pop(old_value) == key
            self.data[key] = value
            self.children[value] = key
            return old_value

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def update(self, data):
        if getattr(data, 'keys', None) is not None:
            data = [(k, data[k]) for k in data.keys()]
        old = {}
        if self.data:
            # since duplication of values is disallowed, we need to remove
            # any current overlapped values so we don't get spurious errors.
            keys = set()
            probs = []
            for k, v in data:
                keys.add(k)
                old_k = self.children.get(v)
                if old_k is not None and old_k != k:
                    probs.append((old_k, v))
            for k, v in probs:
                if k not in keys:
                    raise ValueError(
                        'name mapping can only contain unique values', v)
            for k, v in probs:
                old[k] = self._delitem[k]
        replaced_old = []
        replaced_key = []
        replaced_new = []
        added_key = []
        added_new = []
        for k, v in data:
            o = self._setitem(k, v) or old.get(k)
            if o == v:
                pass
            elif o is None:
                added_key.append(k)
                added_new.append(v)
            else:
                replaced_old.append(o)
                replaced_key.append(k)
                replaced_new.append(v)
        if replaced_old:
            zope.event.notify(zc.vault.interfaces.ObjectsReplaced(
                replaced_old, replaced_new, self, replaced_key))
        if added_key:
            zope.event.notify(
                zc.vault.interfaces.ObjectsAdded(added_value, self, added_key))

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.children == other.children)

    def getKey(self, value, default=None):
        if not isinstance(value, int):
            return default
        return self.children.get(value, default)

class OrderedMapping(Mapping):

    def __init__(self, vals=None):
        self._order = UniqueSequence()
        super(OrderedMapping, self).__init__(vals)

    def items(self):
        return [(k, self.data[k]) for k in self._order]

    def keys(self):
        return self._order

    def values(self):
        return [self.data[k] for k in self._order]

    def __iter__(self):
        return iter(self._order)

    def _delitem(self, key):
        super(OrderedMapping, self)._delitem(key)
        self._order.remove(key)

    def _setitem(self, key, val):
        old_val = super(OrderedMapping, self)._setitem(key, val)
        if old_val is not None and old_val != val:
            self._order.append(key)

    def _z_freeze(self):
        super(OrderedMapping, self)._z_freeze()
        self._order._z_freeze()

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.children == other.children and
                self.keys() == other.keys())

    @zc.freeze.method
    @approvalmethod(reindex=False)
    def move(self, from_, to_):
        if isinstance(to_, slice):
            raise ValueError('only from may be a slice')
        if isinstance(to_, basestring):
            if to_ not in self.data:
                raise ValueError('value not in collection')
        elif to_ != len(self):
            to_ = self.keys()[to_]
        old_order = tuple(self._order)
        if isinstance(from_, slice):
            moved = self._order.__getitem__(slice)
            if isinstance(to_, basestring) and to_ in moved:
                raise ValueError('Cannot move slice to a member of the slice')
            self._order.__delitem__(slice)
            if isinstance(to_, basestring):
                ix = self._order.index(to_)
                self._order[ix:ix] = moved
            else:
                self._order.extend(moved)
        else:
            if isinstance(from_, basestring):
                from_ = self._order.index(from_)
            moved = self._order.pop(from_)
            if isinstance(to_, basestring):
                self._order.insert(self._order.index(to_), moved)
            else:
                self._order.append(moved)
        zope.event.notify(zc.vault.interfaces.OrderChanged(self, old_order))

    @zc.freeze.method
    @approvalmethod(reindex=False)
    def reorder(self, order, slice=None):
        order = tuple(order)
        if slice is None:
            current = set(self._order)
        else:
            current = set(self._order.__getitem__(slice))
        order_set = set(order)
        if len(order_set) != len(order):
            raise ValueError('duplicate values in order')
        if current != order_set:
            raise ValueError('order must contain same values as current set')
        old_order = tuple(self._order)
        if slice:
            self._order.__setitem__(slice, order)
        else:
            self._order[:] = order
        zope.event.notify(zc.vault.interfaces.OrderChanged(self, old_order))
