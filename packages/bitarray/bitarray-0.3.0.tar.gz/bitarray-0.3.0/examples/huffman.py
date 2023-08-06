#!/usr/bin/env pyhton
"""
The non-trivial part of the code is derived from:
http://en.literateprograms.org/Huffman_coding_(Python)

The link also contains a good description of the algorithm.
"""
import sys
from bisect import insort
from collections import defaultdict
from bitarray import bitarray


def huffCode(freq):
    """
    Given a dictionary mapping symbols to thier frequency,
    return the Huffman code in the form of 
    a dictionary mapping the symbols to bitarrays.
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


def freq_string(s):
    """
    Given a string, return a dictionary
    mapping characters to thier frequency.
    """
    res = defaultdict(int)
    for c in s:
        res[c] += 1
    return res


def print_code(filename):
    freq = freq_string(open(filename).read())
    code = huffCode(freq)
    print '   char    frequency    Huffman code'
    print 70*'-'
    for c in sorted(code):
        print '%7r %8i        %s' % (c, freq[c], code[c].to01())


def encode(filename):
    s = open(filename, 'rb').read()
    code = huffCode(freq_string(s))
    fo = open(filename + '.huff', 'wb')
    fo.write('%s\n' % len(code))
    for c in sorted(code):
        fo.write('%i %s\n' % (ord(c), code[c].to01()))
    a = bitarray()
    a.encode(code, s)
    fo.write('%s\n' % a.length())
    a.tofile(fo)
    fo.close()
    print 'Ratio =%6.2f%%' % (100.0 * a.buffer_info()[1] / len(s))


def decode(filename):
    fi = open(filename, 'rb')
    codelen = int(fi.readline())
    code = {}
    for i in xrange(codelen):
        a, b = fi.readline().split()
        code[chr(int(a))] = bitarray(b)
    bits = long(fi.readline())
    a = bitarray()
    a.fromfile(fi)
    del a[bits:]
    fi.close()
    
    fo = open(filename[:-5] + '.out', 'wb')
    fo.write(''.join(a.decode(code)))
    fo.close()


def usage():
    print """Usage: %s command FILE

  print  --  calculate and display the Huffman code for the frequency
             of characters in FILE.

  encode --  encode FILE using the Huffman code calculated for the
             frequency of characters in FILE itself.
             The output is FILE.huff which contains both the Huffman
             code and the bitarray resulting from the encoding.

  decode --  decode FILE, which has .huff extension generated with the
             encode command.  The output is written in a filename
             where .huff is replaced by .out
""" % sys.argv[0]
    sys.exit(0)


if __name__ == '__main__':    
    if len(sys.argv) != 3:
        usage()

    cmd, filename = sys.argv[1:3]
    
    if cmd == 'print':
        print_code(filename)

    elif cmd == 'encode':
        encode(filename)

    elif cmd == 'decode':
        if filename.endswith('.huff'):
            decode(filename)
        else:    
            print 'Filename has no .huff extension'

    else:
        print 'Unknown command %r' % cmd
        usage()
