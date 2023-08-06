"""
Split sliceable objects into batchs, eg for a paging display
"""

import math

__version__ = '1'

class Batcher(object):
    """
    Batch any sliceable object into batches.

    Synopsis::

        >>> items = list('ABCDEFGHIJ')
        >>> batcher = Batcher(items, 4)

        >>> # How many batches are available?
        >>> len(batcher)
        3

        >>> # Get contents of the first batch
        >>> list(batcher[0])
        ['A', 'B', 'C', 'D']

        >>> # Batches look like lists but know about their context too
        >>>
        >>> batch = batcher[1]
        >>> batch
        <Batch #1>

        >>> batcher[1].previous
        <Batch #0>

        >>> batcher[1].next 
        <Batch #2>

        >>> print batcher[2].next
        None

    A common requirement in web applications is to implement a pager widget.
    The range method can help when the user is viewing page **n** and we want to
    display a range of pages centered on **n**, adjusting endpoints to keep
    them in range::

        >>> items = range(100)
        >>> batcher = Batcher(items, 4)

        >>> len(batcher)
        25

        >>> # The range of 5 batches centered on the given batch
        >>> batcher[0].range(5)
        [<Batch #0>, <Batch #1>, <Batch #2>, <Batch #3>, <Batch #4>]
        

        >>> batcher[7].range(5)
        [<Batch #5>, <Batch #6>, <Batch #7>, <Batch #8>, <Batch #9>]

        >>> batcher[23].range(5)
        [<Batch #20>, <Batch #21>, <Batch #22>, <Batch #23>, <Batch #24>]

    If there aren't enough batches available, the entire batch will be returned::

        >>> items = range(10)
        >>> batcher = Batcher(items, 4)
        >>> len(batcher)
        3
        >>> batcher[1].range(5)
        [<Batch #0>, <Batch #1>, <Batch #2>]

    Because batches use python's slicing API to retrieve data, we can
    interrogate the slice object to find out the indices of the first and last
    items in a batch, useful for showing data such as "Page 1 (items 1-10)"::

        >>> items = range(25)
        >>> batcher = Batcher(items, 10)
        >>> batch = batcher[0]
        >>> batch.slice
        slice(0, 10, None)
        >>> "Page %d (items %d-%d)" % (batch.index + 1, batch.slice.start + 1, batch.slice.stop)
        'Page 1 (items 1-10)'
        
    Note how python's slice semantics mean that the indices are zero-based (so
    we add 1 when formatting for display) and that the stop index of the slice
    points to the item after the end of the series.
    """

    def __init__(self, sliceable, size, sliceable_length=None, pad=False):
        """
        Create a new batch from ``sliceable``

        sliceable
            Any object supporting the slicing interface

        size
            How many items per batch

        sliceable_length,
            If the length of the sliceable can't be got via ``len(sliceable)``
            you need to provide it.

        pad
            If true the final batch will be padded with ``None``s to make it
            the same size as the others
        """

        self.sliceable = sliceable
        self.size = size
        self.pad = pad

        if sliceable_length is None:
            self.itemcount = len(sliceable)
        else:
            self.itemcount = sliceable_length

    def __getitem__(self, index):
        """
        Return the batch at ``index`` or the requested slice of batches
        """
        if isinstance(index, slice):
            return [ self[ix] for ix in xrange(slice.start, slice.stop, slice.step) ]

        if not isinstance(index, int):
            raise TypeError("index must be an integer")

        if index < 0:
            index = len(self) + index

        offset = index * self.size
        if offset < 0 or offset >= self.itemcount and self.itemcount > 0:
            raise IndexError("index out of range")

        return Batch(self, index, offset, min(self.itemcount, offset + self.size))

    def __len__(self):
        """
        Return the total number of batches available.

        Synopsis::

            >>> batcher = Batcher(range(10), 10)
            >>> len(batcher)
            1
            >>> batcher = Batcher(range(11), 10)
            >>> len(batcher)
            2
        """
        return math.ceil(self.itemcount / float(self.size))

    def range(self, center_on, size):
        """
        Return a range of batches, of size ``size``, centered on the given batch index.
        """
        start = max(0, center_on - size / 2)
        end = start + size
        if end > len(self):
            start = max(0, start - (end - len(self)))
            end = len(self)

        return [ self[ix] for ix in xrange(start, end) ]

class Batch(object):
    """
    A single batch of items
    """

    def __init__(self, batcher, index, start, end):
        """
        Initialize the batch
        """
        self.batcher = batcher
        self.index = index
        self.slice = slice(start, end, None)
        self._items = None

    @property
    def has_next(self):
        return self.index < len(self.batcher) - 1

    @property
    def next(self):
        try:
            return self.batcher[self.index + 1]
        except IndexError:
            return None

    @property
    def has_previous(self):
        return self.index > 0

    @property
    def previous(self):
        if self.index <= 0:
            return None
        return self.batcher[self.index - 1]

    def range(self, size):
        return self.batcher.range(self.index, size)

    @property
    def items(self):
        if self._items:
            return self._items
        else:
            self._items = self.batcher.sliceable[self.slice]
            if self.batcher.pad:
                self._items = list(self._items)
                self._items += [None] * (self.batcher.size - len(self._items))
            return self._items

    def __getattr__(self, attr):
        return getattr(self.items, attr)

    def __repr__(self):
        return '<Batch #%d>' % self.index

    def __iter__(self):
        return iter(self.items)

