"""This module defines an object type which can efficiently represent
a bitarray.  Bitarrays are sequence types and behave very much like lists.

The constructor is:

bitarray([initializer]) -- create a new bitarray"""

from _bitarray import _bitarray

__version__ = "0.1.0"


def getIndicesEx(r, length):
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

    if (step < 0 and stop >= length) or \
       (step > 0 and start >= stop):
        slicelength = 0
    elif step < 0:
        slicelength = (stop-start+1) / step + 1
    else:
        slicelength = (stop-start-1) / step + 1

    if slicelength < 0:
        slicelength = 0

    return start, stop, step, slicelength


class bitarray(_bitarray):
    """bitarray([initializer]) -> bitarray

Return a new bitarray whose items are bits initialized from the optional
initializer value, which must be a list, string, or iterable over elements
of the appropriate type.

Bitarrays represent bool values and behave pretty much like lists.

Methods:

append() -- append a new bit to the end of the bitarray
buffer_info() -- return information giving the current memory info
bytereverse() -- reverse the order of all bits within each byte
count() -- return number of occurences of a bit
extend() -- extend bitarray by appending multiple bits from an iterable
fill() -- fill the last byte segment with zeros
from01() -- appends bits from a string containing '0's and '1's
fromfile() -- read bits from a file object
fromlist() -- append bits from the list
fromstring() -- append bits from the string
index() -- return index of first occurence of a bit
insert() -- insert a new bit into the bitarray at a provided position
invert() -- invert all bits in the bitarray
length() -- return the number of bits of the bitarray
pop() -- remove and return bit (default last)
remove() -- remove first occurence of a bit
reverse() -- reverse the order of bits in the bitarray
setall() -- set all bits in the bitarray to specified value
to01() -- return a string containing '0's and '1's
tofile() -- write all bits to a file object
tolist() -- return the bitarray converted to an ordinary list
tostring() -- return the bitarray converted to a string"""
    
    def __len__(self):
        # for very large arrays, this will fail but .length() will still work
        return self.length()

    def __hash__(self):
        return hash(tuple(self))
    
    def __add__(self, other):
        if not isinstance(other, bitarray):
            raise TypeError('can only add bitarrays')
        res = bitarray(self)
        res.extend(other)
        return res
    
    def __iadd__(self, other):
        if not isinstance(other, bitarray):
            raise TypeError('can only iadd bitarrays')
        self.extend(other)
        return self
    
    def __mul__(self, n):
        if not isinstance(n, (int, long)):
            raise TypeError('can repeat integer times')
        res = bitarray()
        for dum in xrange(n):
            res.extend(self)
        return res
    
    __rmul__ = __mul__
    
    def __imul__(self, n):
        if not isinstance(n, (int, long)):
            raise TypeError('can repeat integer times')
        if n <= 0:
            self[:] = bitarray()
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
            return self._gscr3(*getIndicesEx(idx, self.length()))
        
    def __setitem__(self, idx, val):
        if isinstance(idx, tuple):
            raise TypeError("list indices must be integers")
        
        if isinstance(idx, (int, long)):
            self._sscr1(idx, val)
        
        if isinstance(idx, slice):
            args = list(getIndicesEx(idx, self.length()))
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
            self._dscr3(*getIndicesEx(idx, ls))

    def insert(self, i, x):
        """insert(i, x)

Insert a new item x into the bitarray before position i."""
        if not isinstance(i, (int, long)):
            raise TypeError("first argument must be int or long")
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

    def reverse(self):
        """reverse()

reverse the order of bits in the bitarray."""
        for i, b in enumerate(self[::-1]):
            self[i] = b
    
    def __int__(self):
        """__int__()

Return bitarray as int or long.  The first bit is the least significant (and
the last one the most significant).
For example, int(bitarray([0, 1, 1])) returns 6."""
        res = 0
        for b in self[::-1]:
            res <<= 1
            res |= int(b)
        return res
    
    __long__ = __int__
    
    def fromint(self, n):
        """fromint(n)

Convert the integer number n to binary, and a append the result to the
bitarray.  For example, fromint(6) has the same effect as extend([0, 1, 1])"""
        if not isinstance(n, (int, long)):
            raise TypeError("first argument must be int or long")
        while n:
            self.append(n & 1)
            n >>= 1
