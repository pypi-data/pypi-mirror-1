#!/usr/bin/env python
import sys
from varlencode import Varlencode
from huffman import huffCode, freqfromfile
from fileutil import writeToFilename

huff = Varlencode(huffCode(freqfromfile('english.dat')))

text = open(sys.argv[1]).read()
data = huff.encode(text)

writeToFilename(data, 'data')

# Local Variables:
# mode: python
# End:
