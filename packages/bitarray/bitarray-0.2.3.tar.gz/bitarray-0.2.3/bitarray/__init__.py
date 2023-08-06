"""
This module defines an object type which can efficiently represent
a bitarray.  Bitarrays are sequence types and behave very much like lists.

Please find a description of this package at:

    http://pypi.python.org/pypi/bitarray/

Thank you for using bitarray.
- Ilan Schnell
"""
__version__ = '0.2.3'

from _bitarray import _bitarray, bits2bytes


class bitarray(_bitarray):
    """bitarray([initial][endian=string])

Return a new bitarray object whose items are bits initialized from
the optional initial, and endianness.
If no object is provided, the bitarray is initialized to have length zero.
The initial object may be of the following types:

int, long
    Create bitarray of length given by the integer.  The initial values
    in the array are random, because only the memory allocated.

string
    Create bitarray from a string with '0's and '1's.

list, tuple, iterable
    Create bitarray from a sequence, each element in the sequence is
    converted to a bit using truth value value.

bitarray
    Create bitarray from another bitarray.  This is done by copying the
    memory holding the bitarray data, and is hence very fast.

The optional keyword arguments 'endian' specifies the bit endianness of the
created bitarray object.
Allowed values are 'big' and 'little' (default is 'big').

Note that setting the bit endianness only has an effect when accessing the
machine representation of the bitarray, i.e. when using the methods: tofile,
fromfile, tostring, fromstring
"""
    # bitwise operation operate on the machine data regardless of what
    # the endianness is set to.
    
    def __and__(self, other):    #  a & b
        res = bitarray(self)
        res._bitwise(other, 'and')
        return res
    
    def __iand__(self, other):   #  a &= b
        self._bitwise(other, 'and')
        return self
        
    def __or__(self, other):     #  a | b
        res = bitarray(self)
        res._bitwise(other, 'or')
        return res
    
    def __ior__(self, other):    #  a |= b
        self._bitwise(other, 'or')
        return self
    
    def __xor__(self, other):    #  a ^ b
        res = bitarray(self)
        res._bitwise(other, 'xor')
        return res

    def __ixor__(self, other):   #  a ^= b
        self._bitwise(other, 'xor')
        return self
    
    def __invert__(self):        #  ~a
        res = bitarray(self)
        res.invert()
        return res
    
    # ----------------------------------------------------------
    
    def __add__(self, other):
        """
        Concatenate two bitarray objetcs.
        The endianness of the result is the endianness of the first bitarray.
        """
        if not isinstance(other, bitarray):
            raise TypeError('can only add bitarrays')
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

    # ----------------------------------------------------------
    def __hash__(self):
        return hash(self.tostring())

 
    def fromlist(self, lst):
        """fromlist(list)

Append bits to bitarray object from an ordinary list.
This method is **deprecated**, use the extend method instead."""
        if not isinstance(lst, list):
            raise TypeError("list expected")
        self.extend(lst)


    def from01(self, s):
        """from01(string)

Appends items from a string, containing '0's and '1's, to the bitarray.
This method is **deprecated**, use the extend method instead."""
        if not isinstance(s, str):
            raise TypeError("string expected")
        self.extend(s)


    def _decode(self, codedict):
        "decode\n\nXXX Not implemented yet"
        pos = 0
        
        res = []
        while pos < length:
            res.append(sym)
            pos += l
        
        print 'decode:', len(self), pos
        if pos != length:
            raise "ERROR"
        
        return res


def test(verbosity=1):
    """test(verbosity=1)

Run selftest."""
    import test_bitarray
    return test_bitarray.run(verbosity=verbosity)

