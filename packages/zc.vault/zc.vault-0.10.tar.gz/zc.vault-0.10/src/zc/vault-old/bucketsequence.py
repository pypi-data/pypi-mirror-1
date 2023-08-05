import persistent
import persistent.list
import BTrees.IOBTree
import BTrees.Length

class Bucket(persistent.Persistent):

    def __init__(self, vals=None, previous=None, next=None, parent=None):
        self.data = persistent.list.PersistentList(vals)
        self.previous = previous
        self.next = next
        self.__parent__ = parent

    def __len__(self):
        return len(self.data)

    def clear(self):
        del self.data[:]

class Index(persistent.Persistent):

    def __init__(self, previous=None, next=None, parent=None):
        self.data = BTrees.IOBTree.IOBTree()
        self.previous = previous
        self.next = next
        self.__parent__ = parent

    def index(self, other):
        for k, v in self.data.items():
            if v is other:
                return k
        raise ValueError('value not found; likely programmer error')

    def __len__(self):
        val = self.data.maxKey()
        return val + len(self.data[val])

    def clear(self):
        self.data.clear()

LEFT = False
RIGHT = True

def shift_sequence(l, count):
    res = l[:count]
    del l[:count]
    return res

def reindex(start_bucket, stop_bucket, recurse=False):
    bucket = start_bucket
    k = None
    stopped = False
    while bucket is not None and isinstance(bucket.__parent__, Index):
        stopped = stopped or bucket is stop_bucket
        parent = bucket.__parent__
        if k is None:
            k = parent.index(bucket)
            if k == parent.data.minKey() and k > 0:
                del parent.data[k]
                k = 0
                parent.data[k] = bucket
        v = len(bucket)
        try:
            next = parent.data.minKey(k+1)
        except ValueError:
            k = None
            if recurse:
                reindex(parent, stop_bucket.__parent__, recurse)
            if stopped:
                break
        else:
            k += v
            if next != k:
                b = parent.data[next]
                del parent.data[next]
                parent.data[k] = b
        bucket = bucket.next

def balance(left, right, children=None):
    len_left = len(left.data)
    len_right = len(right.data)
    move_index = (len_left + len_right) // 2
    if len_left > len_right:
        # move some right
        if isinstance(left, Index):
            items = list(left.data.items()[move_index:])
            zero = items[0][0]
            offset = items[-1][0] + len(items[-1][1]) - zero
            for k, o in reversed(right.data.items()):
                right.data[offset+k] = o
                del right.data[k]
            for k, o in items:
                right.data[k-zero] = o
                del left.data[k]
                o.__parent__ = right
            
        else:
            right.data[0:0] = left.data[move_index:]
            if children is not None:
                for item in left.data[move_index:]:
                    children[item] = right
            del left.data[move_index:]
    else:
        # move some left
        if isinstance(left, Index):
            items = list(right.data.items()[:move_index])
            offset = len(left)
            for k, o in items:
                left.data[offset+k] = o
                del right.data[k]
                o.__parent__ = left
            offset = items[-1][0] + len(items[-1][1])
            for k, o in list(right.data.items()):
                del right.data[k]
                right.data[k-offset] = o
        else:
            move_index -= len_left
            left.data.extend(right.data[:move_index])
            if children is not None:
                for item in right.data[:move_index]:
                    children[item] = left
            del right.data[:move_index]

def rotate(left, right, size, children=None, favor=LEFT):
    if len(left.data) + len(right.data) > size:
        balance(left, right, children)
    elif favor == LEFT:
        if isinstance(left, Index):
            offset = len(left)
            for k, o in list(right.data.items()):
                left.data[offset+k] = o
                o.__parent__ = left
            right.clear()
        else:
            left.data.extend(right.data)
            if children is not None:
                for item in right.data:
                    children[item] = left
            del right.data[:]
    else:
        assert favor == RIGHT
        if isinstance(left, Index):
            offset = len(left)
            for k, o in reversed(right.data.items()):
                right.data[offset+k] = o
                del right.data[k]
            for k, o in left.data.items():
                right.data[k] = o
                o.__parent__ = right
            left.clear()
        else:
            right.data[0:0] = left.data
            if children is not None:
                for item in left.data:
                    children[item] = right
            del left.data[:]

class Sequence(persistent.Persistent):

    def __init__(self, bucket_size=30, index_size=10):
        self.bucket_size = bucket_size
        self.index_size = index_size
        self.data = Bucket(parent=self)
        self.children = BTrees.IOBTree.IOBTree() # non-ints need OOBTree
        self._length = BTrees.Length.Length()

    # Read API

    def __contains__(self, value):
        return value in self.children

    def __len__(self):
        return self._length()

    def count(self, item):
        return item in self.children

    def _get_bucket(self, index):
        bucket = self.data
        ix = index
        while not isinstance(bucket, Bucket):
            key = bucket.data.maxKey(ix)
            bucket = bucket.data[key]
            ix -= key
        return bucket, ix

    def iter(self, start=0):
        length = self._length()
        if start < 0:
            start += length
            if start < 0:
                raise IndexError('list index out of range')
        if length > start:
            bucket, ix = self._get_bucket(start)
            for v in bucket.data[ix:]:
                yield v
            bucket = bucket.next
            while bucket is not None:
                for v in bucket.data:
                    yield v
                bucket = bucket.next

    def iterReversed(self, start=-1):
        length = self._length()
        if start < 0:
            start += length
            if start < 0:
                raise IndexError('list index out of range')
        if length > start:
            bucket, ix = self._get_bucket(start)
            for v in reversed(bucket.data[:ix+1]):
                yield v
            bucket = bucket.previous
            while bucket is not None:
                for v in reversed(bucket.data):
                    yield v
                bucket = bucket.previous

    def iterSlice(self, start=0, stop=None, stride=None):
        if isinstance(start, slice):
            if stop is not None or stride is not None:
                raise ValueError(
                    'cannot pass slice with additional stop or stride')
        else:
            start = slice(start, stop, stride)
        start, stop, stride = start.indices(self._length())
        if stride == 1:
            ix = start
            i = self.iter(start)
            while ix < stop:
                yield i.next()
                ix += 1
        elif stride == -1:
            ix = start
            i = self.iterReversed(start)
            while ix > stop:
                yield i.next()
                ix -= 1
        else:
            if stride < 0:
                condition = lambda begin, end: begin > end
            else:
                condition = lambda begin, end: begin < end
            ix = start
            while condition(ix, stop):
                bucket, i = self._get_bucket(ix)
                yield bucket.data[i]
                ix += stride

    def __iter__(self):
        return self.iter()

    def index(self, value):
        bucket = self.children.get(value)
        if bucket is None:
            raise ValueError('.index(x): x not in collection')
        res = bucket.data.index(value)
        parent = bucket.__parent__
        while isinstance(parent, Index):
            i = parent.index(bucket)
            assert i is not None, 'error in data structure!'
            res += i
            bucket = parent
            parent = bucket.__parent__
        return res

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.iterSlice(index)
        if index < 0:
            index += length
            if index < 0:
                raise IndexError('list index out of range')
        elif index > self._length():
            raise IndexError('list index out of range')
        bucket, ix = self._get_bucket(index)
        return bucket.data[ix]

    # Write API
    
    # Everything relies on __setitem__ to reduce duplicated logic

    def append(self, value):
        self[self._length()] = value

    def insert(self, index, value):
        self[index:index] = (value,)

    def __delitem__(self, index):
        if not isinstance(index, slice):
            if index > self._length():
                raise IndexError('list assignment index out of range')
            index = slice(index, index+1)
        elif index.step == 1:
            index = slice(index.start. index.stop)
        elif index.step is not None:
            start, stop, stride = index.indices(self._length())
            if stride < 0:
                ix = range(start, stop, stride)
            else:
                ix = reversed(range(start, stop, stride))
            for i in ix:
                self.__setitem__(slice(i, i+1), ())
            return
        self.__setitem__(index, ())

    def extend(self, iterable):
        length = self._length()
        self[length:length] = iterable

    __iadd__ = extend

    def pop(self, index=-1):
        res = self[index]
        self[index:index+1] = ()
        return res

    def remove(self, item):
        self.pop(self.index(item))

    def reverse(self):
        self[:] = reversed(self)

    def sort(self, cmpfunc=None):
        vals = list(self.children)
        vals.sort(cmpfunc)
        self[:] = l

    def __setitem__(self, index, value):
        # the workhorse
        length = self._length()
        
        # To reduce the amount of duplicated code, everything is based on
        # slices. Either you are replacing specific items (index is an integer
        # less than len or a slice with an explicit step) or deleting/inserting
        # ranges (index is an integer equal to len or a slice with an implicit
        # step of 1).  We convert integer requests to slice requests here.
        if not isinstance(index, slice):
            value = (value,)
            if index == length:
                index = slice(length, length)
            elif index > length:
                raise IndexError('list assignment index out of range')
            else:
                index = slice(index, index+1, 1)

        start, stop, stride = index.indices(length)
        if index.step is None:
            # delete and/or insert range; bucket arrangement may change
            value = list(value)
            value_set = set(value)
            if len(value) != len(value_set):
                raise ValueError('duplicate values in iterable')
            overlap = value_set.intersection(self.children)
            if overlap:
                overlap = overlap.difference(self.__getitem__(index))
                if overlap:
                    raise ValueError(
                        'duplicates values already in sequence', overlap)
            len_value = len(value)
            start_bucket, start_ix = self._get_bucket(start)
            if start == 0 and stop == length and stride == 1:
                # shortcut: clear out everything
                self.children.clear()
                start_bucket = self.data = Bucket(parent=self)
                start_ix = 0
                self._length.set(0)
            elif stop != start:
                # we're supposed to delete
                stop_bucket, stop_ix = self._get_bucket(stop)
                bucket = start_bucket
                ix = start_ix
                while True:
                    if bucket is stop_bucket:
                        for v in bucket.data[ix:stop_ix]:
                            del self.children[v]
                        del bucket.data[ix:stop_ix]
                        break
                    for v in bucket.data[ix:]:
                        del self.children[v]
                    del bucket.data[ix:]
                    bucket = bucket.next
                    ix = 0
                bucket = start_bucket
                ix = start_ix
                while value:
                    items = shift_sequence(
                        value, self.bucket_size - len(bucket.data))
                    bucket.data[ix:ix] = items
                    for item in items:
                        self.children[item] = bucket
                    if bucket is stop_bucket or not value:
                        break
                    bucket = bucket.next
                    ix = len(bucket.data)

                # So how many have we lost (or even added)?  We can go
                # ahead and adjust the length.

                self._length.change(len_value-len(value)-(stop-start))

                # we've deleted values, and may have replaced some,
                # and now we need to see if we need to rearrange
                # buckets because they are smaller than the fill ratio
                # allows.  We do this even if we have more values to
                # insert so that the insert code can begin from a sane
                # state; that may prove to be unnecessary if this
                # algorithm and implementation is ever polished.

                # The algorithm has us first try to balance across
                # siblings, and then clean up the parents.  Typically
                # B+ tree algorithm descriptions go
                # one-item-at-a-time, while we may have swaths of
                # changes to which we need to adjust.
                #
                # Key adjustments are different than the standard B+
                # tree story because this is a sequence, and our keys
                # are indices that we need to adjust to accomodate the
                # deletions.  This means siblings to all of our
                # parents, walking up the tree.  The "swaths of
                # changes" also makes this a bit tricky.

                fill_maximum = self.bucket_size
                fill_minimum = fill_maximum // 2
                children = self.children

                original_stop_bucket = stop_bucket

                while isinstance(start_bucket, (Bucket, Index)):

                    # We'll get the buckets rotated so that any
                    # bucket that has members will be above the fill ratio
                    # (unless it is the only bucket).
                    #
                    # `bucket` is the last bucket we might have put
                    # anything in to; we'll want to look at it and the
                    # `stop_bucket` (if different) to see if we need to
                    # adjust.
                    #
                    # if bucket and stop_bucket are different and
                    # stop_bucket is not empty and either are below the
                    # fill_minimum...
                        # if the combination is less than the fill_maximum,
                        # put in bucket and empty stop_bucket
                        # else redistribute across so both are above
                        # fill_minimum
                    #
                    # in both cases, we need to adjust the children
                    # pointers for the moved values.

                    len_bucket = len(bucket.data)
                    len_stop = len(stop_bucket.data)
                    if (bucket is not stop_bucket and
                        len_stop and (
                            len_bucket < fill_minimum or
                            len_stop < fill_minimum)):
                        rotate(bucket, stop_bucket, fill_maximum, children)
                        len_bucket = len(bucket.data)
                        len_stop = len(stop_bucket.data)

                    # if (bucket is stop_bucket or stop_bucket is empty)
                    # and bucket.previous is None and stop_bucket.next is
                    # None, shortcut: just make sure this is the top
                    # bucket and stop.

                    if ((bucket is stop_bucket or not len_stop) and
                        bucket.previous is None and stop_bucket.next is None):
                        if self.data is not bucket:
                            self.data = bucket
                            bucket.__parent__ = self
                        else:
                            assert bucket.__parent__ is self
                        bucket.next = None
                        return

                    # now these are the possible states:
                    # - bucket is stop_bucket and is empty
                    # - bucket is stop_bucket and is too small
                    # - bucket is stop_bucket and is ok
                    # - bucket and stop_bucket are both empty
                    # - bucket is ok and stop_bucket is empty
                    # - bucket is too small and stop_bucket is empty
                    # - bucket is ok and stop_bucket is ok
                    #
                    # Therefore, 
                    # - if the stop_bucket is ok or the bucket is empty,
                    #   we're ok with this step, and can move on to
                    #   adjusting the indexes and pointers.
                    # - otherwise the bucket is too small, and there is
                    #   another bucket to rotate with.  Find the bucket
                    #   and adjust so that no non-empty buckets are
                    #   beneath the fill_minimum.  Make sure to adjust the
                    #   `children` data structure, and to adjust
                    #   start_bucket or stop_bucket to include the altered
                    #   bucket.

                    if len_bucket < fill_minimum:
                        previous = bucket.previous
                        next = stop_bucket.next
                        assert previous or next
                        assert bucket is stop_bucket or not len_stop
                        if (next is None or
                            previous is not None and
                            len(next.data) + len_bucket > fill_maximum):
                            # work with previous
                            rotate(previous, bucket, fill_maximum,
                                   children)
                            if bucket is start_bucket:
                                bucket = start_bucket = previous
                            if not bucket.data:
                                bucket = bucket.previous
                                assert bucket
                        else:
                            # work with next
                            rotate(bucket, next, fill_maximum, children,
                                   favor=RIGHT)
                            stop_bucket = next

                    # OK, now we need to adjust pointers and get rid of
                    # empty buckets.  We'll go level-by-level.

                    reindex_start = start_bucket

                    b = bucket
                    while b is not None:
                        if not b.data:
                            ix = b.__parent__.index(b)
                            del b.__parent__.data[ix]
                            if b.previous is not None:
                                b.previous.next = b.next
                            if b.next is not None:
                                b.next.previous = b.previous
                            if b is reindex_start:
                                reindex_start = b.next
                        if b is stop_bucket:
                            break
                        b = b.next

                    reindex(reindex_start, stop_bucket)

                    # now we get ready for the next round...

                    start_bucket = start_bucket.__parent__
                    stop_bucket = stop_bucket.__parent__
                    bucket = bucket.__parent__
                    fill_maximum = self.index_size
                    fill_minimum = fill_maximum // 2
                    children = None
                    
                assert stop_bucket is self

                if not value:
                    return # we're done; don't fall through to add story
                else:
                    # we've replaced old values with new, but there are
                    # some more left.  we'll set things up so the
                    # standard insert story should work for the remaining
                    # values.
                    start_bucket = original_stop_bucket
                    start_ix = stop_ix
                    # ...now continue with add story

            # this is the add story.

            # So, we have a start_bucket and a start_ix: we're supposed
            # to insert the values in i at start_ix in start_bucket.
            if not value:
                return
            fill_maximum = self.bucket_size
            fill_minimum = fill_maximum // 2

            self._length.change(len(value))

            # Clean out the ones after start_ix in the start_bucket, if
            # any.  

            remainder = start_bucket.data[start_ix:]
            value.extend(remainder)
            del start_bucket.data[start_ix:]
            ix = start_ix
            bucket = start_bucket
            created = []

            # Start filling at the ix.  Fill until we reached len
            # or until i is empty.  Make new buckets, remembering them in
            # a list, and fill them until i is empty, and then continue
            # with the removed ones from the start_bucket.  If the last
            # bucket is too small, merge or rotate as appropriate.

            length = fill_maximum - len(bucket.data)
            while value:
                added = shift_sequence(value, length)
                bucket.data.extend(added)
                for o in added:
                    self.children[o] = bucket
                if value:
                    bucket = Bucket(previous=bucket, next=bucket.next)
                    bucket.previous.next = bucket
                    if bucket.next is not None:
                        bucket.next.previous = bucket
                    created.append(bucket)
                    length = self.bucket_size

            if bucket.__parent__ is not self and len(bucket) < fill_minimum:
                # this should only be able to happen when a previous bucket
                # is already filled. It's simplest, then, to just split the
                # contents of the previous bucket and this one--that way
                # there's not any empty bucket to have to handle.
                assert (len(bucket.previous.data) + len(bucket.data) >=
                        2 * fill_minimum)
                balance(bucket.previous, bucket, self.children)

            # Now we have to insert any new buckets in the parents.  We
            # again fill the parents, creating and remembering as
            # necessary, and rotating at the end.  We keep on walking up
            # until the list of new buckets is empty.  If we reach the top,
            # we add a level at the top and continue.

            if not created:
                reindex(start_bucket, bucket)
                return

            value = created
            fill_maximum = self.index_size
            fill_minimum = fill_maximum // 2

            while value:
                if start_bucket.__parent__ is self:
                    self.data = parent = Index(parent=self)
                    parent.data[0] = start_bucket
                    start_bucket.__parent__ = parent
                    start_ix = 0
                    bucket = start_bucket = parent
                else:
                    assert start_bucket.__parent__ is not None
                    start_ix = start_bucket.__parent__.index(start_bucket)
                    bucket = start_bucket = start_bucket.__parent__
                    value.extend(
                        start_bucket.data.values(start_ix, excludemin=True))
                    for k in tuple(
                        start_bucket.data.keys(start_ix, excludemin=True)):
                        del start_bucket.data[k]
                ix = start_ix + len(start_bucket.data[start_ix])
                created = []

                # Start filling at the ix. Fill until we reached len or
                # until i is empty. Make new buckets, remembering them in a
                # list, and fill them until i is empty, and then continue
                # with the removed ones from the start_bucket. If the last
                # bucket is too small, merge or rotate as appropriate.

                length = fill_maximum - len(bucket.data)
                while value:
                    for o in shift_sequence(value, length):
                        bucket.data[ix] = o
                        o.__parent__ = bucket
                        ix += len(o)
                    # we don't necessarily need to fix parents--
                    # we'll get to them above
                    if value:
                        bucket = Index(previous=bucket, next=bucket.next)
                        bucket.previous.next = bucket
                        if bucket.next is not None:
                            bucket.next.previous = bucket
                        created.append(bucket)
                        length = fill_maximum
                        ix = 0

                if (bucket.__parent__ is not self and
                    len(bucket.data) < fill_minimum):
                    # this should only be able to happen when a previous
                    # bucket is already filled. It's simplest, then, to
                    # just split the contents of the previous bucket and
                    # this one--that way there's not any empty bucket to
                    # have to handle.
                    assert (len(bucket.previous.data) + len(bucket.data) >=
                            2 * fill_minimum)
                    balance(bucket.previous, bucket, self.children)
                value = created
            if start_bucket.__parent__ is not self:
                # we need to correct the indices of the parents.
                reindex(start_bucket, bucket, recurse=True)

        else:
            # replace one set with a set of equal length
            changed = []
            index = start
            removed = set()
            problems = set()
            added = {}
            error = None
            value_ct = 0
            for v in value:
                value_ct += 1
                if index >= stop:
                    error = ValueError(
                        'attempt to assign sequence of at least size %d '
                        'to extended slice of size %d' % (
                            value_ct, (stop - start) / stride))
                    break
                bucket, ix = self._get_bucket(index)
                old = bucket.data[ix]
                removed.add(old)
                if v in added:
                    error = ValueError('item duplicated in iterable', v)
                    break
                if v in self.children:
                    problems.add(v)
                bucket.data[ix] = v
                added[v] = bucket
                changed.append((bucket, ix, old))
                index += stride
            else:
                if value_ct < (stop - start) / stride:
                    error = ValueError(
                            'attempt to assign sequence of size %d to '
                            'extended slice of size %d' % (
                            value_ct, (stop - start) / stride))
            if not error and problems:
                problems -= removed
                if problems:
                    error = ValueError('item(s) already in collection',
                        problems)
            if error:
                for bucket, ix, old in changed:
                    bucket.data[ix] = old
                raise error
            for v in removed:
                del self.children[v]
            self.children.update(added)

#    I want eq and ne but don't care much about the rest

    def __eq__(self, other):
        return isinstance(other, Sequence) and tuple(self) == tuple(other)

    def __ne__(self, other):
        return not self.__eq__(other)

#     def __lt__(self, other):
#         pass
# 
#     def __gt__(self, other):
#         pass
# 
#     def __le__(self, other):
#         pass
# 
#     def __ge__(self, other):
#         pass

#     def __add__(self, other):
#         pass
# 
#     def __mul__(self, other):
#         pass
# 
#     def __rmul__(self, other):
#         pass
