#!/usr/bin/env python

class OrderedSet(object):
    """An OrderedSet acts very much like a list. There are two important
    differences:
    
    - Each item appears in the list only once.
    - You can look up an item's index in the list in constant time.

    Use it like you would use a list. All the standard operators are defined.

    Create a set with a few initial items::
    
        >>> s = OrderedSet(['apple', 'banana', 'pear'])
    
    Look up the index of 'banana':
    
        >>> s.index('banana')
        1
        >>> s.indexFor('banana')  # (synonym)
        1

    Look up an unknown index:
    
        >>> s.index('automobile')
        Traceback (most recent call last):
            ...
        KeyError: 'automobile'

    Add a new item::
    
        >>> s.add('orange')
        3
        >>> s.index('orange')
        3

    Add an item that's already there::
    
        >>> s.add('apple')
        0

    Extend with some more items::
    
        >>> s.extend(['grapefruit', 'kiwi'])
        >>> s.index('grapefruit')
        4

    See that it otherwise behaves like a list::
    
        >>> s[0]
        'apple'
        >>> s[0] = 'Apple'
        >>> s[0]
        'Apple'
        >>> len(s)
        6
        >>> for item in s:
        ...     print item,
        Apple banana pear orange grapefruit kiwi

    ``None`` element is used as a placeholder for non-present
    elements, but it is never semantically an element of the set::

        >>> del s[0]
        >>> s[0] is None
        True
        >>> s.index('banana')
        1
        >>> None in s
        False

    (We would have used ``Ellipsis``, but it's not picklable, and it's
    not worth the trouble to work around that.)
    """
    index_is_efficient = True
    
    __slots__ = ['items', 'indices', 'index', 'indexFor', '__contains__']

    def __init__(self, origitems=None):
        '''Initialize a new OrderedSet.'''
        self.items = []     # list of all keys
        self.indices = {}   # maps known keys to their indices in the list
        if origitems:
            for item in origitems: self.add(item)

        # Quick lookup methods.
        self.index = self.indices.__getitem__
        self.indexFor = self.index
        self.__contains__ = self.indices.__contains__

    def __repr__(self):
        if len(self) < 10:
            # This isn't exactly right if there are blank items.
            return u'OrderedSet(%r)' % (self.items,)
        else:
            return u'<OrderedSet of %d items like %s>' % (len(self), self[0])

    def __getstate__(self):
        return self.items
    def __setstate__(self, state):
        self.__init__(origitems=state)


    def add(self, key):
        """
        Add an item to the set (unless it's already there),
        returning its index.

        ``None`` is never an element of an OrderedSet.
        """
        
        if key in self.indices: return self.indices[key]
        n = len(self.items)
        self.items.append(key)
        if key is not None:
            self.indices[key] = n
        return n
    append = add

    def extend(self, lst):
        "Add a collection of new items to the set."
        for item in lst: self.add(item)
    __iadd__ = extend

    def __getitem__(self, n):
        return self.items[n]

    def __setitem__(self, n, newkey):
        oldkey = self.items[n]
        del self.indices[oldkey]
        self.items[n] = newkey
        self.indices[newkey] = n

    def __delitem__(self, n):
        """
        Deletes an item from the OrderedSet.

        This is a bit messy. It'll just leave a hole in the list. Do you
        really want to do that?
        """
        oldkey = self.items[n]
        del self.indices[oldkey]
        self.items[n] = None

    def __len__(self): return len(self.items)

    def __iter__(self): return self.items.__iter__()

    def __eq__(self, other):
        '''Two OrderedSets are equal if their items are equal.
        
            >>> a = OrderedSet(['a', 'b'])
            >>> b = OrderedSet(['a'])
            >>> b.add('b')
            1
            >>> a == b
            True
        '''
        # Get 'items' from the other thing, in case it's an OrderedSet.
        return self.items == getattr(other, 'items', other)
    def __ne__(self, other):
        return not self == other


class IdentitySet(object):
    '''
    An object that behaves like an :class:OrderedSet, but simply contains
    the range of numbers up to *len*. Thus, every number is its own index.
        
    IdentitySets are used to label :class:`Tensors <divisi.tensor.Tensor>` on
    axes where labels would be meaningless or unnecessary.
    '''
    index_is_efficient = True
    
    def __init__(self, len):
        self.len = len

    def __repr__(self): return 'IdentitySet(%d)' % (self.len,)
    def __len__(self): return self.len
    
    # Doesn't check for out-of-range or even that it's an integer.
    def __getitem__(self, x): return x 
    def index(self, x): return x
    def __iter__(self): return (x for x in xrange(self.len))
    def add(self, key):
        if key + 1 > self.len:
            self.len = key + 1
        return key
    @property
    def items(self): return range(self.len)
    def __eq__(self, other):
        return self.items == getattr(other, 'items', other)
    def __ne__(self, other): return not self == other



def indexable_set(x, dim):
    if x is None:
        return IdentitySet(dim)
    if getattr(x, 'index_is_efficient', False):
        return x
    return OrderedSet(x)

    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
