"""
(c) Ilan Schnell, May 2008

The non-trivial part of the code derived from:
http://en.literateprograms.org/Huffman_coding_(Python)

The link also contains a good description of the algorithm.
"""
import sys
from bisect import insort

try:
    from bitarray import bitarray
except ImportError:
    sys.stderr.write("Warning: count not import bitarray, "
                     "using ordinary list object instead\n")
    bitarray = list


def huffCode(freq):
    """Given a dictionary which maps symbols, which may be any (hashable)
    object, to thier frequency, return the Huffman code.

    >>> d = {'e':.2, 'l':.03, 'a':.1, 'i':.05, 'n':.07}
    >>> for c, b in huffCode(d).iteritems():
    ...   print c, ''.join('1' if i else '0' for i in b)
    ...
    i 0000
    a 01
    e 1
    l 0001
    n 001
    """
    lst = [(freq[s], s) for s in freq]
    lst.sort()
    
    while len(lst) > 1:
        childL, childR = lst.pop(1), lst.pop(0)
        parent = (childL[0] + childR[0], childL, childR)
        insort(lst, parent)

    # Now lst[0] is the root node of the Huffman tree

    def traverse(tree, prefix=bitarray()):
        if len(tree) == 2:
            result[tree[1]] = prefix
        else:
            for i in xrange(2):
                traverse(tree[i+1], prefix + bitarray([i]))

    result = {}
    traverse(lst[0])
    return result


def freqfromfile(filename, fill=True):
    res = {}
    if fill:
        for n in xrange(256):
            res[chr(n)] = 0
    for line in open(filename):
        row = line.split()
        res[chr(int(row[0]))] = int(row[-1])
    return res


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
    if len(sys.argv) == 2:
        freq = freqfromfile(sys.argv[1], False)
        code = huffCode(freq)
        for c in sorted(code):
            print '%3i %7r  %s' % \
                  (ord(c), c, ''.join('1' if i else '0' for i in code[c]))
