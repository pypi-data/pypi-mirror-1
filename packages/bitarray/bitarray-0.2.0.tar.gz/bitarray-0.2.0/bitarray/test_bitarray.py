import os
import sys
import unittest
from random import randint


if __name__ == '__main__':
    from __init__ import bitarray, _getIndicesEx
    repr_type = "<class '__init__.bitarray'>"
else:
    from bitarray import bitarray, _getIndicesEx
    repr_type = "<class 'bitarray.bitarray'>"


def randombitarrays(n=20):
    for n in xrange(n):
        yield bitarray([randint(0, 1) for d in xrange(n)],
                       endian='big' if randint(0, 1) else 'little')

def randomlists():
    for n in xrange(20):
        yield [bool(randint(0, 1)) for d in xrange(n)]

def randomstrings():
    for n in xrange(20):
        yield ''.join(chr(randint(0, 255)) for d in xrange(n))

def rndsliceidx(length):
    return randint(-2*length, 2*length-1) if randint(0, 1) == 1 else None

def slicelen(r, length):
    return _getIndicesEx(r, length)[-1]


class Tests(unittest.TestCase):
    
    def check_obj(self, a):
        self.assertEqual(repr(type(a)), repr_type)
        ignore = 8 * a.buffer_info()[1] - a.length()
        self.assert_(0 <= ignore < 8)
        
        
    def assertEQUAL(self, a, b):
        self.assertEqual(a, b)
        self.assertEqual(a.endian(), b.endian())
        self.check_obj(a)
        self.check_obj(b)


    def test_buffer_info(self):
        a = bitarray([False])
        self.assertRaises(TypeError, a.buffer_info, 42)
        bi = a.buffer_info()
        self.assert_(isinstance(bi, tuple))
        self.assertEqual(len(bi), 3)
        self.assert_(isinstance(bi[0], (int, long)))
        self.assert_(isinstance(bi[1], int))
        self.assert_(isinstance(bi[2], str))

        for n in xrange(1000):
            bi = bitarray(n).buffer_info()
            self.assertEqual(bi[1], 0 if n==0 else ((n - 1) / 8 + 1));
        
        a = bitarray(endian='little')
        self.assertEqual(a.buffer_info()[2], 'little')
        
        a = bitarray(endian='big')
        self.assertEqual(a.buffer_info()[2], 'big')


    def test_endian(self):
        a = bitarray(endian='little')
        self.assertEqual(a.endian(), 'little')
        
        a = bitarray(endian='big')
        self.assertEqual(a.endian(), 'big')


    def test_len(self):
        for n, a in enumerate(randombitarrays()):
            self.assertEqual(len(a), n)

    
    def test_getitem(self):
        a = bitarray()
        self.assertRaises(IndexError, a.__getitem__,  0)
        a.append(True)
        self.assertEqual(a[0], True)
        self.assertRaises(IndexError, a.__getitem__,  1)
        self.assertRaises(IndexError, a.__getitem__, -2)
        
        a.append(False)
        self.assertEqual(a[1], False)
        self.assertRaises(IndexError, a.__getitem__,  2)
        self.assertRaises(IndexError, a.__getitem__, -3)
        
        a = bitarray('1100010')
        for i, b in enumerate([True, True, False, False, False, True, False]):
            self.assertEqual(a[i], b)
            self.assertEqual(a[i-7], b)
        self.assertRaises(IndexError, a.__getitem__,  7)
        self.assertRaises(IndexError, a.__getitem__, -8)
        
        a = bitarray('AQ', 3)
        self.assertEQUAL(a[:], a)
        self.assert_(a[:] is not a)
        aa = a.tolist()
        self.assertEQUAL(a[11:2:-3], bitarray(aa[11:2:-3]))
        self.check_obj(a[:])
        
        self.assertRaises(ValueError, a.__getitem__, slice(None, None, 0))
        self.assertRaises(TypeError, a.__getitem__, (1, 2))
        
        for a in randombitarrays():
            aa = a.tolist()
            la = len(a)
            if la == 0: continue
            for dum in xrange(10):
                step = rndsliceidx(la)
                if step == 0: step = None
                s = slice(rndsliceidx(la), rndsliceidx(la), step)
                self.assertEQUAL(a[s], bitarray(aa[s], endian=a.endian()))

        
    def test_setitem(self):
        a = bitarray([False])
        a[0] = 1
        self.assertEqual(a.tolist(), [True])
        
        a = bitarray(2)
        a[0] = 0
        a[1] = 1
        self.assertEqual(a.tolist(), [False, True])
        a[-1] = 0
        a[-2] = 1
        self.assertEqual(a.tolist(), [True, False])
        
        self.assertRaises(IndexError, a.__setitem__,  2, True)
        self.assertRaises(IndexError, a.__setitem__, -3, False)
        
        a = bitarray(5*[False])
        a[0] = 1
        a[-2] = 1
        self.assertEqual(a, bitarray('10010'))
        self.assertRaises(IndexError, a.__setitem__,  5, 'foo')
        self.assertRaises(IndexError, a.__setitem__, -6, 'bar')
        
        for a in randombitarrays():
            la = len(a)
            if la == 0: continue
            for dum in xrange(3):
                step = rndsliceidx(la)
                if step == 0: step = None
                s = slice(rndsliceidx(la), rndsliceidx(la), step)
                for b in randombitarrays():
                    if len(b) == slicelen(s, len(a)) or step is None:
                        c = bitarray(a)
                        d = c
                        c[s] = b
                        self.assert_(c is d)
                        self.check_obj(c)
                        cc = a.tolist()
                        cc[s] = b.tolist()
                        self.assertEqual(c, bitarray(cc))
        

    def test_delitem(self):
        a = bitarray('100110')
        del a[1]
        self.assertEqual(len(a), 5)
        del a[3]
        del a[-2]
        self.assertEqual(a, bitarray('100'))
        self.assertRaises(IndexError, a.__delitem__,  3)
        self.assertRaises(IndexError, a.__delitem__, -4)
        
        for a in randombitarrays():
            la = len(a)
            if la == 0: continue
            for dum in xrange(10):
                step = rndsliceidx(la)
                if step == 0: step = None
                s = slice(rndsliceidx(la), rndsliceidx(la), step)
                c = bitarray(a)
                d = c
                del c[s]
                self.assert_(c is d)
                self.check_obj(c)
                cc = a.tolist()
                del cc[s]
                self.assertEQUAL(c, bitarray(cc, endian=c.endian()))
        

    def test_iterate(self):
        for lst in randomlists():
            acc = []
            for b in bitarray(lst):
                acc.append(b)
            self.assertEqual(acc, lst)

        
    def test_new(self):
        a = bitarray()
        self.assertEqual(a.tolist(), [])
        self.assertEqual(len(a), 0)
        self.check_obj(a)
        
        for n in xrange(50):
            a = bitarray(n)
            self.assertEqual(len(a), n)
            self.check_obj(a)
            a = bitarray(long(n))
            self.assertEqual(len(a), n)
            self.check_obj(a)
            a = bitarray(n*'A', 0)
            self.assertEqual(a.tostring(), n*'A')
            self.assertEqual(len(a), 8*n)
            self.check_obj(a)
            
        for lst in randomlists():
            a = bitarray(lst)
            self.assertEqual(a.tolist(), lst)
            self.check_obj(a)
            a = bitarray(tuple(lst))
            self.assertEqual(a.tolist(), lst)
            self.check_obj(a)
            a = bitarray(iter(lst))
            self.assertEqual(a.tolist(), lst)
            self.check_obj(a)
            a = bitarray(''.join('1' if x else '0' for x in lst))
            self.assertEqual(a.tolist(), lst)
            self.check_obj(a)
            
        for a in randombitarrays():
            b = bitarray(a)
            self.assert_(a is not b)
            self.assertEQUAL(a, b)
            
        self.assertEqual(bitarray(None), bitarray())
        for i in xrange(-10, 20):
            self.assertEqual(bitarray(None, i), bitarray())
            
        self.assertRaises(ValueError, bitarray.__new__, bitarray, -1)
        self.assertRaises(ValueError, bitarray.__new__, bitarray, '0120100')
        
        self.assertRaises(TypeError, bitarray.__new__, bitarray, 'A', 42, 69)
        for wrong in [Ellipsis, slice(0), {}, set(), frozenset(),
                      xrange(9), 2.354, 4+3j, u'unicode']:
            self.assertRaises(TypeError, bitarray.__new__, bitarray, wrong)
            
        for i in xrange(-10, 20):
            if i in (-1, 0): continue
            self.assertRaises(TypeError, bitarray.__new__, bitarray, '', i)
            
        for i in [-2, 8, 9, 10]:
            self.assertRaises(TypeError, bitarray.__new__, bitarray, 'a', i)
            
        for i in xrange(8):
            a = bitarray('\xff', i)
            self.assertEqual(a, (8-i)*bitarray('1'))
            a = bitarray('A\xff', i)
            self.assertEqual(a[8:], (8-i)*bitarray('1'))

        self.assertRaises(TypeError, bitarray.__new__, bitarray, '', 0, 42)
        self.assertRaises(ValueError, bitarray.__new__, bitarray, '', 0, 'foo')

        a = bitarray('00100000', endian='big')
        self.assertEqual(a.tostring(), ' ')

        a = bitarray([0, 0, 0, 0, 0, 1, 0, 0], endian='little')
        self.assertEqual(a.tostring(), ' ')
        
        for end in ('little', 'big'):
            a = bitarray(endian=end)
            c = bitarray(a)
            self.assertEqual(c.endian(), end)
            c = bitarray(a, endian='little')
            self.assertEqual(c.endian(), 'little')
            c = bitarray(a, endian='big')
            self.assertEqual(c.endian(), 'big')


    def test_repr(self):
        for a in randombitarrays():
            b = eval(repr(a))
            self.assert_(b is not a)
            self.assertEqual(a, b)
            self.check_obj(b)


    def test_append(self):
        for a in randombitarrays():
            aa = a.tolist()
            b = a
            b.append(1)
            self.assert_(a is b)
            self.check_obj(b)
            self.assertEQUAL(b, bitarray(aa+[1], endian=a.endian()))
            b.append('')
            self.assertEQUAL(b, bitarray(aa+[1, 0], endian=a.endian()))


    def test_extend(self):
        for a in randomlists():
            for b in randombitarrays():
                c = bitarray(a)
                idc = id(c)
                c.extend(b)
                self.assertEqual(id(c), idc)
                self.assertEqual(c, bitarray(a + b.tolist()))

            for b in randomlists():
                c = bitarray(a)
                idc = id(c)
                c.extend(b)
                self.assertEqual(id(c), idc)
                self.assertEqual(c.tolist(), a + b)
                self.check_obj(c)

                def foo():
                    for e in b:
                        yield e
                c = bitarray(a)
                idc = id(c)
                c.extend(foo())
                self.assertEqual(id(c), idc)
                self.assertEqual(c.tolist(), a + b)
                self.check_obj(c)


    def test_insert(self):
        a = bitarray()
        b = a
        a.insert(0, True)
        self.assert_(a is b)
        self.assertEqual(len(a), 1)
        self.assertRaises(TypeError, a.insert)
        self.assertRaises(TypeError, a.insert, None)

        for a in randombitarrays():
            aa = a.tolist()
            item = bool(randint(0, 1))
            pos = randint(-len(a), len(a))
            a.insert(pos, item)
            aa.insert(pos, item)
            self.assertEqual(a.tolist(), aa)
            self.check_obj(a)
            

    def test_index(self):
        a = bitarray()
        for i in (True, False, 1, 0):
            self.assertRaises(ValueError, a.index, i)
        
        a = bitarray(100*[False])
        self.assertRaises(ValueError, a.index, True)
        a[20] = a[27] = 54
        self.assertEqual(a.index(42), 20)
        self.assertEqual(a.index(0), 0)
        
        a = bitarray(200*[True])
        self.assertRaises(ValueError, a.index, False)
        a[173] = a[187] = 0
        self.assertEqual(a.index(False), 173)
        self.assertEqual(a.index(True), 0)

        for n in xrange(50):
            for m in xrange(n):
                a = bitarray(n)
                a.setall(0)
                self.assertRaises(ValueError, a.index, 1)
                a[m] = 1
                self.assertEqual(a.index(1), m)

                a.setall(1)
                self.assertRaises(ValueError, a.index, 0)
                a[m] = 0
                self.assertEqual(a.index(0), m)


    def test_copy(self):
        import copy
        for a in randombitarrays():
            b = copy.copy(a)
            self.assert_(b is not a)
            self.assertEQUAL(a, b)
            
            b = copy.deepcopy(a)
            self.assert_(b is not a)
            self.assertEQUAL(a, b)


    def test_pickle(self):
        from cPickle import loads, dumps
        for a in randombitarrays():
            b = loads(dumps(a))
            self.assert_(b is not a)
            self.assertEQUAL(a, b)


    def test_count(self):
        a = bitarray('10011')
        self.assertEqual(a.count(True), 3)
        self.assertEqual(a.count(False), 2)
        self.assertEqual(a.count('foo'), 3)
        self.assertEqual(a.count(''), 2)
        for a in randombitarrays():
            self.assertEqual(a.count(1), a.to01().count('1'))
            self.assertEqual(a.count(0), a.to01().count('0'))


    def test_fill(self):
        for a in randombitarrays():
            aa = a.tolist()
            la = len(a)
            b = a
            b.fill()
            self.assertEqual(b.endian(), a.endian())
            bb = b.tolist()
            lb = len(b)
            self.assert_(a is b)
            self.check_obj(b)
            if la % 8 == 0:
                self.assertEqual(bb, aa)
                self.assertEqual(lb, la)
            else:
                self.assert_(lb % 8 == 0)
                self.assertNotEqual(bb, aa)
                self.assertEqual(bb[:la], aa)
                self.assertEqual(b[la:], (lb-la)*bitarray('0'))
                self.assert_(0 < lb-la < 8)
        a = bitarray('101')
        a.fill()
        self.assertEqual(a, bitarray('10100000'))
        
        
    def test_reverse(self):
        self.assertRaises(TypeError, bitarray().reverse, 42)
        
        for a in randombitarrays():
            aa = a.tolist()
            b = a
            a.reverse()
            self.assert_(a is b)
            self.assertEQUAL(a, bitarray(aa[::-1], endian=a.endian()))
            

    def test_tofromfile(self):
        from test import test_support
        from cStringIO import StringIO

        for s in randomstrings():
            a = bitarray(s, 0)
            self.assertRaises(TypeError, a.tofile)
            self.assertRaises(TypeError, a.tofile, StringIO())
            f = open(test_support.TESTFN, 'wb')
            a.tofile(f)
            f.close()
            self.assertRaises(TypeError, a.tofile, f)
            
            b = bitarray()
            self.assertRaises(TypeError, b.fromfile)
            self.assertRaises(TypeError, b.fromfile, StringIO())
            f = open(test_support.TESTFN, 'rb')
            b.fromfile(f)
            self.assertEQUAL(a, b)
        
        f = open(test_support.TESTFN, 'wb')
        f.write('A')
        f.close()

        b = bitarray()
        f = open(test_support.TESTFN, 'rb')
        b.fromfile(f)
        f.close()
        
        for n in xrange(20):
            a = bitarray(n)
            f = open(test_support.TESTFN, 'rb')
            a.fromfile(f)
            self.assertEqual(len(a), n + 8)
            self.assertEQUAL(a[-8:], b)
            f.close()

        a = bitarray('ABCDEFGHIJ', 0)
        f = open(test_support.TESTFN, 'wb')
        a.tofile(f)
        f.close()
        
        b = bitarray()
        f = open(test_support.TESTFN, 'rb')
        b.fromfile(f, 1);     self.assertEqual(b.tostring(), 'A')
        f.read(1)
        b = bitarray()
        b.fromfile(f, 2);     self.assertEqual(b.tostring(), 'CD')
        b.fromfile(f, 1);     self.assertEqual(b.tostring(), 'CDE')
        b.fromfile(f, 0);     self.assertEqual(b.tostring(), 'CDE')
        b.fromfile(f);        self.assertEqual(b.tostring(), 'CDEFGHIJ')
        b.fromfile(f);        self.assertEqual(b.tostring(), 'CDEFGHIJ')
        f.close()
        
        b = bitarray()
        f = open(test_support.TESTFN, 'rb')
        f.read(1);            self.assertRaises(EOFError, b.fromfile, f, 10)
        f.close()
        self.assertEqual(b.tostring(), 'BCDEFGHIJ')
        
        b = bitarray()
        f = open(test_support.TESTFN, 'rb')
        b.fromfile(f);        self.assertEqual(b.tostring(), 'ABCDEFGHIJ')
        self.assertRaises(EOFError, b.fromfile, f, 1)
        f.close()
        
        os.unlink(test_support.TESTFN)
        
        
    def test_fromlist(self):
        for a in randombitarrays():
            for blst in randomlists():
                alst = a.tolist()
                c = a
                c.fromlist(blst)
                self.assertEqual(c.tolist(), alst + blst)
                self.assert_(c is a)
                self.check_obj(c)
                
        
    def test_tolist(self):
        for lst in randomlists():
            a = bitarray(lst)
            self.assertEqual(a.tolist(), lst)

        
    def test_fromstring(self):
        a = bitarray()
        a.fromstring('A')
        self.assertEqual(a, bitarray('A', 0))
        b = a
        b.fromstring('BC')
        self.assertEqual(b, bitarray('ABC', 0))
        self.assert_(b is a)
        self.check_obj(b)
        
        a = bitarray('A', 0)
        for n in xrange(20):
            b = bitarray(n)
            c = b.__copy__()
            b.fromstring('A')
            self.assertEqual(len(b), n + 8)
            self.assertEqual(b[-8:], a)
            self.assertEqual(b[:-8], c)


    def test_tostring(self):
        for end in ('big', 'little'):
            a = bitarray('foo', 0, endian=end)
            self.assertEqual(a.tostring(), "foo")
        
        a = bitarray(16)
        a.setall(1)
        self.assertEqual(a.tostring(), '\xff\xff')


    def test_tofrom01(self):
        for a in randombitarrays():
            b = bitarray()
            c = b
            c.from01(a.to01())
            self.assertEqual(a, c)
            self.assert_(b is c)
            self.check_obj(c)
            
        a = bitarray()
        self.assertRaises(ValueError, a.from01, '01201')
        
        a = bitarray()
        a.from01('10');         self.assertEqual(a.to01(), '10')
        a.from01('');           self.assertEqual(a.to01(), '10')
        a.from01('01110');      self.assertEqual(a.to01(), '1001110')
        a.from01('100');        self.assertEqual(a.to01(), '1001110100')


    def test_setall(self):
        for a in randombitarrays():
            val = randint(0, 1)
            b = a
            b.setall(val)
            self.assertEqual(b, bitarray(len(b)*[val]))
            self.assert_(a is b)
            self.check_obj(b)

  
    def test_invert(self):
        for a in randombitarrays():
            aa = a.tolist()
            b = a
            b.invert()
            for i in xrange(len(a)):
                self.assertEqual(b[i], not aa[i])
            self.assert_(a is b)
            self.check_obj(b)


    def test_bytereverse(self):
        for i in xrange(256):
            a = bitarray(chr(i), 0)
            aa = a.tolist()
            b = a
            b.bytereverse()
            self.assertEqual(b, bitarray(aa[::-1]))
            self.assert_(a is b)
            self.check_obj(b)
        a = bitarray('111011')
        a.bytereverse()
        self.assertEqual(a, bitarray('001101'))


    def test_compare(self):
        for a in randombitarrays():
            for b in randombitarrays():
                aa = a.tolist()
                bb = b.tolist()
                self.assertEqual(a == b, aa == bb)
                self.assertEqual(a != b, aa != bb)
                self.assertEqual(a <= b, aa <= bb)
                self.assertEqual(a <  b, aa <  bb)
                self.assertEqual(a >= b, aa >= bb)
                self.assertEqual(a >  b, aa >  bb)


    def test_add(self):
        for a in randombitarrays():
            for b in randombitarrays():
                c = a + b
                self.assertEqual(c, bitarray(a.tolist() + b.tolist()))
                self.assertEqual(c.endian(), a.endian())
                self.check_obj(c)
                
        a = bitarray()
        self.assertRaises(TypeError, a.__add__, 42)


    def test_iadd(self):
        for a in randombitarrays():
            for b in randombitarrays():
                c = bitarray(a)
                d = c
                d += b
                self.assertEqual(d, a + b)
                self.assert_(c is d)
                self.assertEQUAL(c, d)
                self.assertEqual(d.endian(), a.endian())
                self.check_obj(d)
                
        a = bitarray()
        self.assertRaises(TypeError, a.__iadd__, 42)


    def test_mul(self):
        for a in randombitarrays():
            for n in xrange(-10, 20):
                c = a * n
                self.assertEQUAL(c, bitarray(n * a.tolist(),
                                             endian=a.endian()))
                c = n * a
                self.assertEqual(c, bitarray(n * a.tolist(),
                                             endian=a.endian()))

        a = bitarray()
        self.assertRaises(TypeError, a.__mul__, None)
    

    def test_imul(self):
        for a in randombitarrays():
            for n in xrange(-10, 10):
                b = bitarray(a)
                c = b
                c *= n
                self.assertEQUAL(c, bitarray(n * a.tolist(),
                                             endian=a.endian()))
                self.assert_(c is b)
        
        a = bitarray()
        self.assertRaises(TypeError, a.__imul__, None)


    def test_contains(self):
        a = bitarray()
        self.assert_(False not in a)
        self.assert_(True not in a)
        a.append(True)
        self.assert_(True in a)
        self.assert_(False not in a)
        a = bitarray([False])
        self.assert_(False in a)
        self.assert_(True not in a)
        a.append(True)
        self.assert_(0 in a)
        self.assert_(1 in a)
        for n in xrange(2, 100):
            a = bitarray(n)
            a.setall(0)
            self.assert_(False in a)
            self.assert_(True not in a)
            a[randint(0, n-1)] = 1
            self.assert_(True in a)
            self.assert_(False in a)
            a.setall(1)
            self.assert_(True in a)
            self.assert_(False not in a)
            a[randint(0, n-1)] = 0
            self.assert_(True in a)
            self.assert_(False in a)


    def test_remove(self):
        a = bitarray()
        for i in (True, False, 1, 0):
            self.assertRaises(ValueError, a.remove, i)
        a = bitarray('1010110')
        a.remove(False);        self.assertEqual(a, bitarray('110110'))
        a.remove(True);         self.assertEqual(a, bitarray('10110'))
        a.remove(1);            self.assertEqual(a, bitarray('0110'))
        a.remove(0);            self.assertEqual(a, bitarray('110'))
        
        a = bitarray('0010011')
        b = a
        b.remove('1')
        self.assert_(b is a)
        self.assertEQUAL(b, bitarray('000011'))


    def test_pop(self):
        a = bitarray()
        self.assertRaises(IndexError, a.pop)

        for a in randombitarrays():        
            self.assertRaises(IndexError, a.pop, len(a))
            self.assertRaises(IndexError, a.pop, -len(a)-1)
            if len(a) == 0:
                continue
            aa = a.tolist()
            enda = a.endian()
            self.assertEqual(a.pop(), aa[-1])
            self.check_obj(a)
            self.assertEqual(a.endian(), enda)
            
        for a in randombitarrays():
            if len(a) == 0:
                continue
            n = randint(-len(a), len(a)-1)
            aa = a.tolist()
            self.assertEqual(a.pop(n), aa[n])
            self.check_obj(a)
            

    def test_subclassing(self):
        class ExaggeratingBitarray(bitarray):
            
            def __new__(cls, data, offset):
                return bitarray.__new__(cls, data)
            
            def __init__(self, data, offset):
                self.offset = offset

            def __getitem__(self, i):
                return bitarray.__getitem__(self, i - self.offset)
            
        for a in randombitarrays():
            if len(a) == 0:
                continue
            b = ExaggeratingBitarray(a, 1234)
            for i in xrange(len(a)):
                self.assertEqual(a[i], b[i+1234])


    def test_endianness(self):
        self.assertEqual(bitarray('\x01', 0, 'little').to01(), '10000000')
        self.assertEqual(bitarray('\x80', 0, 'little').to01(), '00000001')
        
        self.assertEqual(bitarray('\x80', 0, 'big').to01(), '10000000')
        self.assertEqual(bitarray('\x01', 0, 'big').to01(), '00000001')
        
        self.assertEqual(bitarray('\x01', 0, 'little'),
                         bitarray('\x80', 0, 'big'))
        
        a = bitarray(8, endian='little')
        a.setall(False)
        a[0] = True
        self.assertEqual(a.tostring(), '\x01')
        a[1] = True
        self.assertEqual(a.tostring(), '\x03')
        a.fromstring(' ')
        self.assertEqual(a.tostring(), '\x03 ')
        self.assertEqual(a.to01(), '1100000000000100')
        
        a = bitarray(8, endian='big')
        a.setall(False)
        a[7] = True
        self.assertEqual(a.tostring(), '\x01')
        a[6] = True
        self.assertEqual(a.tostring(), '\x03')
        a.fromstring(' ')
        self.assertEqual(a.tostring(), '\x03 ')
        self.assertEqual(a.to01(), '0000001100100000')
        

def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(Tests)
    runner = unittest.TextTestRunner(verbosity=1)
    return runner.run(suite)


if __name__ == '__main__':
    run()

else:
    from bitarray import __version__
    print 'bitarray is insalled in:', os.path.dirname(__file__)
    print 'bitarray version:', __version__
    print sys.version
