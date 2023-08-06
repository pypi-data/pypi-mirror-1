"""
This module defines an object type which can efficiently represent
a bitarray.  Bitarrays are sequence types and behave very much like lists.

Please find a description of this package at:

    http://pypi.python.org/pypi/bitarray/

Thank you for using bitarray.
"""
__version__ = '0.2.1'

from _bitarray import _bitarray, bits2bytes


def _getIndicesEx(r, length):
    if not isinstance(r, slice):
        raise TypeError("slice object expected")
    start = r.start
    stop  = r.stop
    step  = r.step
    if r.step is None:
        step = 1
    else:
        if step == 0:
            raise ValueError("slice step cannot be zero")
    
    defstart = length-1 if step < 0 else 0
    defstop  = -1 if step < 0 else length
    
    if r.start is None:
        start = defstart
    else:
        if start < 0: start += length
        if start < 0: start = -1 if step < 0 else 0
        if start >= length: start = length-1 if step < 0 else length
    
    if r.stop is None:
        stop = defstop
    else:
        if stop < 0: stop += length
        if stop < 0: stop = -1
        if stop > length: stop = length

    if (step < 0 and stop >= length) or (step > 0 and start >= stop):
        slicelength = 0
    elif step < 0:
        slicelength = (stop-start+1) / step + 1
    else:
        slicelength = (stop-start-1) / step + 1

    if slicelength < 0:
        slicelength = 0

    return start, stop, step, slicelength


class bitarray(_bitarray):
    """bitarray([initial][endian=string])

Return a new bitarray object whose items are bits initialized from
the optional initial, and endianness.
If no object is provided, the bitarray is initalized to have length zero.
The initial object may be of the following types:

int, long
    Create bitarray of length given by the integer.  The initial values
    in the array are random, because only the memory allocated.

string
    Create bitarray from a string with '0's and '1's,
    e.g. bitarray('01101001111').

list, tuple, iterable
    Create bitarray from a sequence, each element in the sequence is
    converted to a bit using the bool function, 
    e.g. bitarray([2, 0, 'a', {}])  ->  bitarray('1010')

bitarray
    Create bitarray from another bitarray.  This is done by copying the
    memory holding the bitarray data, and is hence very fast.

The optional keyword arguments 'endian' specifies the bit endianness of the
created bitarray object.  Allowed values are 'big' and 'little' (default 'big')

Note that setting the bit endianness only has an effect when accessing the
machine representation of the bitarray, i.e. when using the methods: tofile,
fromfile, tostring, fromstring
"""

    def __hash__(self):
        return hash(self.to01())

    
    def __add__(self, other):
        """
        Concatenate two bitarray objetcs.
        The endianness of the result is the endianness of the first bitarray.
        """
        if not isinstance(other, bitarray):
            raise TypeError('can only add two bitarrays')
        res = bitarray(self)
        res.extend(other)
        return res

    
    def __iadd__(self, other):
        """
        Extend with other bitarray.
        The endianness of the other bitarray is of no relevance.
        """
        if not isinstance(other, bitarray):
            raise TypeError('can only iadd bitarrays')
        self.extend(other)
        return self

    
    def __mul__(self, n):
        if not isinstance(n, (int, long)):
            raise TypeError('can repeat integer times')
        res = bitarray(endian=self.endian())
        for dum in xrange(n):
            res.extend(self)
        return res
    
    __rmul__ = __mul__

    
    def __imul__(self, n):
        if not isinstance(n, (int, long)):
            raise TypeError('can repeat integer times')
        if n <= 0:
            self[:] = bitarray(endian=self.endian())
        elif n == 1:
            pass
        else: # n > 1
            tmp = bitarray(self)
            for dum in xrange(1, n):
                self.extend(tmp)
        return self

    
    def __getitem__(self, idx):
        if isinstance(idx, tuple):
            raise TypeError("list indices must be integers")
        
        if isinstance(idx, (int, long)):
            return self._gscr1(idx)
        
        if isinstance(idx, slice):
            return self._gscr3(*_getIndicesEx(idx, self.length()))

        
    def __setitem__(self, idx, val):
        if isinstance(idx, tuple):
            raise TypeError("list indices must be integers")
        
        if isinstance(idx, (int, long)):
            self._sscr1(idx, val)
        
        if isinstance(idx, slice):
            args = list(_getIndicesEx(idx, self.length()))
            args.append(val)
            self._sscr3(*args)

        
    def __delitem__(self, idx):
        if isinstance(idx, tuple):
            raise TypeError("list indices must be integers")
        ls = self.length()
        if isinstance(idx, (int, long)):
            if idx < 0:
                idx += ls
            if 0 <= idx < ls:
                del self[idx:idx+1]
            else:
                raise IndexError("bitarray assignment index out of range")
        
        if isinstance(idx, slice):
            self._dscr3(*_getIndicesEx(idx, ls))


    def fromfile(self, f, n=-1):
        """fromfile(f [, n])

Read n bytes from the file object f and append them to the bitarray
interpreted as machine values.  When n is omitted, as many bytes are
read until EOF is reached."""
        ls1 = self.length()
        self.fill()
        ls2 = self.length()
        _bitarray.fromfile(self, f, n)
        del self[ls1:ls2]


    def fromlist(self, lst):
        """fromlist(list)

Append bits to bitarray from list.
This method is **deprecated**, use the 'extend' method instead."""
        if not isinstance(lst, list):
            raise TypeError("list expected")
        self.extend(lst)


    def from01(self, s):
        """from01(string)

Appends items from the string, containing '0's and '1's, to the bitarray.
This method is **deprecated**, use 'extend' method instead."""
        if not isinstance(s, str):
            raise TypeError("string expected")
        self.extend(s)


    def insert(self, i, x):
        """insert(i, x)

Insert a new item x into the bitarray before position i."""
        if not isinstance(i, (int, long)):
            raise TypeError("first argument must be integer")
        self[i:i] = bitarray([x])


    def remove(self, x):
        """remove(x)

Remove the first occurence of x in the bitarray."""
        del self[self.index(x)]


    def pop(self, i=-1):
        """pop([i])

Return the i-th element and delete it from the bitarray. i defaults to -1."""
        ls = self.length()
        if ls == 0:
            raise IndexError("pop from empty bitarray")
        
        if i < 0:
            i += ls
            
        if 0 <= i < ls:
            res = self[i]
            del self[i]
            return res

        raise IndexError("pop index out of range")



def test(verbosity=1):
    """test(verbosity=1)

Selftest the module."""
    import test_bitarray
    return test_bitarray.run(verbosity=verbosity)
