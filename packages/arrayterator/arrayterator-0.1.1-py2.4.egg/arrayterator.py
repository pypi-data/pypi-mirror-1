"""Buffered iterator for big arrays."""

__author__ = "Roberto De Almeida <rob@pydap.org>"

from __future__ import division

import operator


class arrayterator(object):
    """Buffered iterator for big arrays.

    This class creates a buffered iterator for reading big arrays in small
    contiguous blocks. The class can be used with any object that supports
    multidimensional slices and a copy() method, like variables from
    Scientific.IO.NetCDF, pynetcdf and numpy.array.
    
    An example with numpy.array:

        >>> import numpy
        >>> b = numpy.arange(10)
        >>> b.shape = (1,2,5)
        >>> print b
        [[[0 1 2 3 4]
          [5 6 7 8 9]]]
        >>> it = arrayterator(b, nrecs=3)
        >>> print it[:]
        [[[0 1 2 3 4]
          [5 6 7 8 9]]]
        >>> for value in it.flat:
        ...     print value
        0
        1
        2
        3
        4
        5
        6
        7
        8
        9

    Checking if the iterator returns the 1D data:

        >>> c = numpy.arange(10000)
        >>> c.shape = (100,100)
        >>> it = arrayterator(c, nrecs=11)  # read 11 values at a time
        >>> assert numpy.all(c.flat  == numpy.concatenate(list(it)))

    We can also specify the region to iterate over:

        >>> d = c[0:2,0:2]
        >>> it = arrayterator(c, start=(0,0), shape=(2,2))
        >>> assert numpy.all(d.flat  == numpy.concatenate(list(it)))

    And we can always slice the iterator:

        >>> it = arrayterator(c, start=(1,1), shape=(2,2), stride=(10,10))
        >>> print it[:]
        [[ 101  111]
         [1101 1111]]
        >>> for value in it.flat:
        ...     print value
        101
        111
        1101
        1111

    Note that when we slice the iterator, the slice is relative to the
    initial region. The iterator above has shape=(2,2), so the get all
    the data we must use the following slice:
    
        >>> print it[0:2,0:2]
        [[ 101  111]
         [1101 1111]]
    """
    def __init__(self, var, start=None, shape=None, stride=None, nrecs=None):
        self._var = var
        self._shape = shape or var.shape
        self._start = start or [0] * len(self._shape)
        self._stride = stride or [1] * len(self._shape)
        
        if nrecs is None:
            # Read everything.
            self._nrecs = reduce(operator.mul, self._shape)
        else:
            self._nrecs = nrecs

    def __len__(self):
        """Emulate the behaviour of a Numeric/numarray/numpy array.

        This method returns the length of the first dimension, so it can
        be used directly in functions from Numeric, numarray or numpy.
        """
        return self.shape[0]

    def __getitem__(self, index):
        slice_ = []
        for start_,shape_,step_ in zip(self._start, self.shape, self._stride):
            stop_ = start_ + (shape_ * step_)
            slice_.append(slice(start_, stop_, step_))
        slice_ = tuple(slice_)
        data = self._var[slice_].copy()

        return data[index]
    
    def flat(self):
        for block in self:
            for v in block: yield v
    flat = property(flat)

    def shape(self):
        return self._shape
    shape = property(shape)

    def __iter__(self):
        """Iterate over blocks."""
        start = self._start[:]
        span = self._nrecs * reduce(operator.mul, self._stride)

        # If nrecs is bigger than the array we just read everything.
        if span >= reduce(operator.mul, self.shape):
            slice_ = []
            for start_,shape_,step_ in zip(start, self.shape, self._stride):
                stop_ = start_ + (shape_ * step_)
                slice_.append(slice(start_, stop_, step_))
            slice_ = tuple(slice_)
            data = self._var[slice_].copy().flat
            yield data
            raise StopIteration
        
        # Find which dimension to run along.
        cumprod = [reduce(lambda x,y: x*y, self.shape[i:], 1) for i,foo in enumerate(self.shape)]
        for i,prod in enumerate(cumprod):
            if span < prod: rundim = i

        while 1:
            count = [1] * len(self.shape)
            if rundim == len(self.shape)-1:
                count[rundim] = span 
            else:
                count[rundim] = span//cumprod[rundim+1]
                for i in range(rundim+1, len(self.shape)):
                    count[i] = self.shape[i]

            if start[rundim] + count[rundim] < self.shape[rundim]:
                slice_ = []
                for start_,shape_,step_ in zip(start, count, self._stride):
                    stop_ = start_ + (shape_ * step_)
                    slice_.append(slice(start_, stop_, step_))
                slice_ = tuple(slice_)
                data = self._var[slice_].copy().flat
                yield data
                start[rundim] += count[rundim]
            else:
                # Cap count at the end of the running dimension.
                count[rundim] = self.shape[rundim] + self._start[rundim] - start[rundim]
                slice_ = []
                for start_,shape_,step_ in zip(start, count, self._stride):
                    stop_ = start_ + (shape_ * step_)
                    slice_.append(slice(start_, stop_, step_))
                slice_ = tuple(slice_)
                data = self._var[slice_].copy().flat
                yield data 

                if rundim == 0:
                    raise StopIteration
                else:
                    # Increment dimension(s).
                    start[rundim-1] += 1
                    start[rundim] = self._start[rundim]

                    for i in range(rundim-1, 0, -1):
                        if start[i] >= self.shape[i]:
                            start[i] = self._start[i]
                            start[i-1] += 1
                        else:
                            break

                    # Reached the end of the array.
                    if start[0] >= self.shape[0]: raise StopIteration

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
