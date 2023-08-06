"""
Enables reading and writing bitarrays of arbitrary length to a
filename.  This is achieved by storing an additional byte at the
head of the file.  This byte contains the number of bits to be
ignored from the last byte of raw data and ranges from '0' to '7'.
Hence, 3 bits would sufficient to store this information.
"""
import sys

from bitarray import bitarray


def writeToFilename(a, filename):
    if not isinstance(a, bitarray):
        raise TypeError("object not bitarray")
    
    f = open(filename, 'wb')
    ignore = 8 * a.buffer_info()[1] - a.length()
    assert 0 <= ignore < 8
    f.write(str(ignore))
    a.tofile(f)
    f.close()


def readFromFilename(filename):
    f = open(filename, 'rb')
    ignore = int(f.read(1))
    assert 0 <= ignore < 8
    a = bitarray()
    a.fromfile(f)
    f.close()
    if ignore:
        assert a[-ignore:].count(True) == 0
        del a[-ignore:]
    return a


if __name__ == '__main__':
    import random, os
    for n in range(75):
        a = bitarray(random.randint(0, 1) for d in xrange(n))
        writeToFilename(a, 'data')
        b = readFromFilename('data')
        assert a == b
        assert len(a) == len(b) == n
        assert a is not b
        sys.stdout.write('.')
        sys.stdout.flush()

    os.remove('data')
    sys.stdout.write('\nOK\n')
