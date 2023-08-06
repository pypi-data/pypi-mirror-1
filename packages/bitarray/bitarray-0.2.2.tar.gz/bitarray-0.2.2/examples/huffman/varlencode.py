"""
(c) Ilan Schnell, May 2008
"""

class Varlencode:
    """Implements variable length bit encoding and decoding.
    An instance is initialized by the type of the code stream,
    and a dictionary containing the code which maps objects to the
    coded objects.
    
    >>> code = {'e':'1', 'a':'01', 'n':'001', 'i':'0000', 'l':'0001'}
    >>> huffman = Varlencode(code)
    >>> huffman.encode('ilan')
    '0000000101001'
    >>> ''.join(huffman.decode('0000000101001'))
    'ilan'
    
    >>> code = {'a':'1', 'n':'00', 'i':'02', 'l':'01'}
    >>> x = Varlencode(code)
    >>> x.encode('ilan')
    '0201100'
    >>> ''.join(x.decode('0201100'))
    'ilan'
    """
    def __init__(self, code):
        self.code = code
        self.reverse = {}
        for item, rep in code.iteritems():
            self.reverse[rep] = item
            self.typ = rep.__class__
        
        self.minlen = 10**9
        self.maxlen = 0
        for rep in self.reverse:
            self.minlen = min(self.minlen, len(rep))
            self.maxlen = max(self.maxlen, len(rep))
            assert isinstance(rep, self.typ)
            
        assert len(self.code) == len(self.reverse)
        
    def encode(self, seq):
        output = self.typ()
        for item in seq:
            output += self.code[item]
        return output
    
    def decode(self, dat):
        pos = 0
        while True:
            for i in xrange(self.minlen, self.maxlen+1):
                try:
                    yield self.reverse[dat[pos:pos+i]]
                    pos += i
                    break
                except KeyError:
                    pass
            else:
                break


if __name__ == '__main__':
    import doctest
    from array import array
    from huffman import huffCode, freqfromfile
    
    doctest.testmod()
    
    exmaple = 'Now is the time.'
    
    huff = Varlencode(huffCode(freqfromfile('english.dat')))
    
    data = huff.encode(exmaple)
    assert ''.join(huff.decode(data)) == exmaple

    # --------------------------------

    code = {}
    for line in open('huffman.out'):
        row = line.split()
        code[int(row[0])] = row[-1]
        
    huff = Varlencode(code)
    
    data = huff.encode(map(ord, exmaple))
    assert array('B', huff.decode(data)).tostring() == exmaple
    
    # --------------------------------

    code = {}
    for i in xrange(256):
        code[chr(i)] = (255-i,)
    
    x = Varlencode(code)
    
    data = x.encode(exmaple)
    assert ''.join(x.decode(data)) == exmaple
