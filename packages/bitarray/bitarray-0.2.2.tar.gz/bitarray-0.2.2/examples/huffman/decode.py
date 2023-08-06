#!/usr/bin/env python
import sys
from varlencode import Varlencode
from huffman import huffCode, freqfromfile
from fileutil import readFromFilename

huff = Varlencode(huffCode(freqfromfile('english.dat')))

data = readFromFilename('data')
text = ''.join(huff.decode(data))

sys.stdout.write(text)

# Local Variables:
# mode: python
# End:
