from bitarray import bitarray

class PBM: # Portable Bitmap class
    def __init__(self, w=0, h=0):
        self.data = [bitarray(w, endian='big') for y in xrange(h)]
    
    def clear(self):
        for row in self.data:
            row.setall(False)
    
    def size(self):
        h = len(self.data)
        if h:
            w = len(self.data[0])
        else:
            w = 0
        return w, h
    
    def save(self, filename):
        fo = open(filename, 'wb')
        fo.write('P4\n')
        fo.write('# This is a partable bitmap (pbm) file.\n')
        fo.write('%i %i\n' % (self.size()))
        for row in self.data:
            row.tofile(fo)
        fo.close()
    
    def load(self, filename):
        fi = open(filename, 'rb')
        assert fi.readline() == 'P4\n'
        while True:
            line = fi.readline()
            if not line.startswith('#'):
                w, h = map(int, line.split())
                break
        if w:
            bytes_per_row = (w - 1) / 8 + 1
        else:
            bytes_per_row = 0
        self.data = []
        for y in xrange(h):
            row = bitarray(endian='big')
            row.fromfile(fi, bytes_per_row)
            self.data.append(row)
        fi.close()
    
    def __getitem__(self, s):
        x, y = s
        return self.data[y][x]

    def __setitem__(self, s, val):
        x, y = s
        self.data[y][x] = val


if __name__ == '__main__':
    # draw picture with straight line from (10, 10) to (390, 390)
    a = PBM(600, 400)
    a.clear()
    for x in xrange(10, 390):
        a[x, x] = True
    a.save('pic1.pbm')
    
    # copy the picture
    b = PBM()
    b.load('pic1.pbm')
    b[10, 10] = True
    print b.size()
    b.save('pic2.pbm')
