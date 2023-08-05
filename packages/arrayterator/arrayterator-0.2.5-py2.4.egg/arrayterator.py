from __future__ import division

"""Buffered iterator for big arrays."""

__author__ = "Roberto De Almeida <rob@pydap.org>"


import operator
import copy


class arrayterator(object):
    """Buffered iterator for big arrays.

    This class creates a buffered iterator for reading big arrays in small
    contiguous blocks. The class is useful for objects stored in the
    filesystem. It allows iteration over the object *without* reading
    everything in memory; instead, small blocks are read and iterated over.
    
    The class can be used with any object that supports multidimensional
    slices and a copy() method, like variables from Scientific.IO.NetCDF,
    pynetcdf and numpy.array.

    An example with numpy.array:

        >>> import numpy
        >>> a = numpy.arange(10)
        >>> a.shape = (1,2,5)
        >>> print a
        [[[0 1 2 3 4]
          [5 6 7 8 9]]]
        >>> it = arrayterator(a, nrecs=3)
        >>> for block in it:
        ...     print block[:]
        [0 1 2]
        [3 4]
        [5 6 7]
        [8 9]
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

        >>> b = numpy.arange(10000)
        >>> b.shape = (100,100)
        >>> it = arrayterator(b, nrecs=11)  # read 11 values at a time
        >>> assert numpy.all(b.flat == numpy.concatenate(list(it)))

    We can also specify the region to iterate over by slicing the
    arrayterator object:

        >>> it2 = it[0:2,0:2]
        >>> for value in it2.flat:
        ...     print value
        0
        1
        100
        101
        
        >>> it3 = it2[0,:]
        >>> for value in it3.flat:
        ...     print value
        0
        1
    """
    def __init__(self, var, nrecs=None):
        self._var = var
        
        self._start = [0] * len(var.shape)
        self._stop = var.shape
        self._step = [1] * len(var.shape)
        
        if nrecs is None:
            # Read everything.
            self._nrecs = reduce(operator.mul, var.shape)
        else:
            self._nrecs = nrecs

    def __getitem__(self, index):
        # Fix index and check for ellipsis.
        if not isinstance(index, tuple): index = (index,)

        out = []
        length, dims = len(index), len(self.shape)
        for slice_ in index:
            if slice_ is Ellipsis: 
                out.extend([slice(None)] * (dims - length + 1))
                length += (dims - length)
            else:
                out.append(slice_)
        index = tuple(out)

        if len(index) < dims:
            index += (slice(None),) * (dims - len(index))

        # Return a new arrayterator over a subset of the data.
        out = copy.copy(self)
        out._start, out._stop, out._step = [], [], []

        for i, (start, stop, step, slice_) in enumerate(zip(self._start, self._stop, self._step, index)):
            start_ = start + (getattr(slice_, 'start', slice_) or 0)
            step_ = step * (getattr(slice_, 'step', 1) or 1)
            
            stop_ = getattr(slice_, 'stop', start+1)
            if stop_ is None:
                stop_ = stop
            else:
                if stop_ < 0: stop_ += stop + start
                stop_ = min(stop, stop_ - start)

            out._start.append(start_)
            out._stop.append(stop_)
            out._step.append(step_)

        return out
            
    def flat(self):
        for block in self:
            for v in block: yield v
    flat = property(flat)

    def shape(self):
        return [((stop - start - 1)//step + 1) for start, stop, step in zip(self._start, self._stop, self._step)]
    shape = property(shape)

    def __array__(self):
        slice_ = []
        for start_,shape_,step_ in zip(self._start, self.shape, self._step):
            stop_ = start_ + (shape_ * step_)
            slice_.append(slice(start_, stop_, step_))
        slice_ = tuple(slice_)
        return self._var[slice_].copy()

    def __iter__(self):
        """Iterate over blocks."""
        start = self._start[:]
        span = self._nrecs * reduce(operator.mul, self._step)

        # If nrecs is bigger than the array we just read everything.
        if span >= reduce(operator.mul, self.shape):
            slice_ = []
            for start_,shape_,step_ in zip(start, self.shape, self._step):
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
                for start_,shape_,step_ in zip(start, count, self._step):
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
                for start_,shape_,step_ in zip(start, count, self._step):
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
