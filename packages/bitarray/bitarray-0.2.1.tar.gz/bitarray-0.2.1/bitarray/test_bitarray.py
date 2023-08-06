import os
import sys
import unittest
import tempfile
import shutil
from random import randint
from cStringIO import StringIO


if __name__ == '__main__':
    from __init__ import bitarray, bits2bytes, _getIndicesEx
    repr_type = "<class '__init__.bitarray'>"
else:
    from bitarray import bitarray, bits2bytes, _getIndicesEx
    repr_type = "<class 'bitarray.bitarray'>"


tests = []


class Util():
    
    def randombitarrays(self, N=20):
        for n in xrange(N):
            yield bitarray([randint(0, 1) for d in xrange(n)],
                           endian='big' if randint(0, 1) else 'little')

    def randomlists(self, N=20):
        for n in xrange(N):
            yield [bool(randint(0, 1)) for d in xrange(n)]

    def rndsliceidx(self, length):
        return randint(-2*length, 2*length-1) if randint(0, 1) == 1 else None

    def slicelen(self, r, length):
        return _getIndicesEx(r, length)[-1]

    def check_obj(self, a):
        self.assertEqual(repr(type(a)), repr_type)
        unused = 8 * a.buffer_info()[1] - a.length()
        self.assert_(0 <= unused < 8)
        self.assertEqual(unused, a.buffer_info()[3])

    def assertEQUAL(self, a, b):
        self.assertEqual(a, b)
        self.assertEqual(a.endian(), b.endian())
        self.check_obj(a)
        self.check_obj(b)

# ---------------------------------------------------------------------------

class TestsModuleFunctions(unittest.TestCase, Util):

    def test_bits2bytes(self):
        for arg in ['foo', [], None, {}]:
            self.assertRaises(TypeError, bits2bytes, arg)
        
        self.assertRaises(TypeError, bits2bytes)
        self.assertRaises(TypeError, bits2bytes, 1, 2)
        
        self.assertRaises(ValueError, bits2bytes, -1)
        self.assertRaises(ValueError, bits2bytes, -924L)
        
        for n in xrange(1000):
            self.assertEqual(bits2bytes(n),
                             0 if n==0 else ((n - 1) / 8 + 1));
        
        for n, m in [(0, 0), (1, 1), (2, 1), (7, 1), (8, 1), (9, 2),
                     (10, 2), (15, 2), (16, 2), (64, 8), (65, 9),
                     (0L, 0), (1L, 1), (65L, 9), (2**29, 2**26),
                     (2**31, 2**28), (2**32, 2**29), (2**34, 2**31),
                     (2**34+793, 2**31+100), (2**35-8, 2**32-1)]:
            self.assertEqual(bits2bytes(n), m)


tests.append(TestsModuleFunctions)

# ---------------------------------------------------------------------------
    
class CreateObjectTests(unittest.TestCase, Util):
    
    def test_noInitializer(self):
        a = bitarray()
        self.assertEqual(len(a), 0)
        self.assertEqual(a.tolist(), [])
        self.check_obj(a)


    def test_endian(self):
        a = bitarray('A', 0, endian='little')
        self.assertEqual(a.endian(), 'little')
        self.check_obj(a)

        b = bitarray('A', 0, endian='big')
        self.assertEqual(b.endian(), 'big')
        self.check_obj(b)

        self.assertEqual(a.tostring(), b.tostring())
        
        a = bitarray(' ', 0, endian=u'little')
        self.assertEqual(a.endian(), 'little')
        self.check_obj(a)

        b = bitarray(' ', 0, endian=u'big')
        self.assertEqual(b.endian(), 'big')
        self.check_obj(b)
        
        self.assertEqual(a.tostring(), b.tostring())
        
        self.assertRaises(TypeError, bitarray.__new__, bitarray, endian=0)
        self.assertRaises(ValueError, bitarray.__new__, bitarray, endian='')


    def test_integers(self):
        for n in xrange(50):
            a = bitarray(n)
            self.assertEqual(len(a), n)
            self.check_obj(a)

            a = bitarray(long(n))
            self.assertEqual(len(a), n)
            self.check_obj(a)
            
        self.assertRaises(ValueError, bitarray.__new__, bitarray, -1)
        self.assertRaises(ValueError, bitarray.__new__, bitarray, -924L)


    def test_list(self):
        lst = ['foo', None, [1], {}]
        a = bitarray(lst)
        self.assertEqual(a.tolist(), [True, False, True, False])
        self.check_obj(a)
        
        for n in xrange(50):
            lst = [bool(randint(0, 1)) for d in xrange(n)]
            a = bitarray(lst)
            self.assertEqual(a.tolist(), lst)
            self.check_obj(a)


    def test_tuple(self):
        tup = ('', True, [], {1:2})
        a = bitarray(tup)
        self.assertEqual(a.tolist(), [False, True, False, True])
        self.check_obj(a)
        
        for n in xrange(50):
            lst = [bool(randint(0, 1)) for d in xrange(n)]
            a = bitarray(tuple(lst))
            self.assertEqual(a.tolist(), lst)
            self.check_obj(a)
        

    def test_iter(self):
        for n in xrange(50):
            lst = [bool(randint(0, 1)) for d in xrange(n)]
            a = bitarray(iter(lst))
            self.assertEqual(a.tolist(), lst)
            self.check_obj(a)

    def test_iter2(self):
        for lst in self.randomlists():
            def foo():
                for x in lst:
                    yield x
            a = bitarray(foo())
            self.assertEqual(a, bitarray(lst))
            self.check_obj(a)


    def test_01(self):
        a = bitarray('0010111')
        self.assertEqual(a.tolist(), [0, 0, 1, 0, 1, 1, 1])
        self.check_obj(a)
        
        for n in xrange(50):
            lst = [bool(randint(0, 1)) for d in xrange(n)]
            s = ''.join('1' if x else '0' for x in lst)
            a = bitarray(s)
            self.assertEqual(a.tolist(), lst)
            self.check_obj(a)
            
        self.assertRaises(ValueError, bitarray.__new__, bitarray, '01012100')
        

    def test_string(self):
        a = bitarray('', 0)
        self.assertEqual(a.tolist(), [])
        self.check_obj(a)
        
        for i in xrange(8):
            self.assertEqual(bitarray('\xff', i).tolist(), (8 - i)*[True])
            self.assertEqual(bitarray('\x00', i).tolist(), (8 - i)*[False])

        a = bitarray('\xff\x00', 0)
        self.assertEqual(a.tolist(), 8*[True] + 8*[False])
        
        for n in xrange(50):
            a = bitarray(n*'A', 0)
            self.assertEqual(a.tostring(), n*'A')
            self.assertEqual(len(a), 8*n)
            self.check_obj(a)


    def test_bitarray(self):
        for n in xrange(50):
            a = bitarray(n)
            b = bitarray(a)
            self.assert_(a is not b)
            self.assertEQUAL(a, b)

        for end in ('little', 'big'):
            a = bitarray(endian=end)
            c = bitarray(a)
            self.assertEqual(c.endian(), end)
            c = bitarray(a, endian='little')
            self.assertEqual(c.endian(), 'little')
            c = bitarray(a, endian='big')
            self.assertEqual(c.endian(), 'big')
    

    def test_None(self):
        self.assertEQUAL(bitarray(), bitarray(0))
        self.assertEQUAL(bitarray(), bitarray(None))
        
        for i in xrange(-10, 20):
            self.assertEQUAL(bitarray(None, i), bitarray())


    def test_WrongArgs(self):
        self.assertRaises(TypeError, bitarray.__new__, bitarray, 'A', 42, 69)
        
        self.assertRaises(TypeError, bitarray.__new__, bitarray, Ellipsis)
        self.assertRaises(TypeError, bitarray.__new__, bitarray, slice(0))
        
        
        self.assertRaises(TypeError, bitarray.__new__, bitarray, 2.345)
        self.assertRaises(TypeError, bitarray.__new__, bitarray, 4+3j)
            
        for i in xrange(1, 20):
            self.assertRaises(ValueError, bitarray.__new__, bitarray, '', i)

        for i in xrange(8, 20):
            self.assertRaises(ValueError, bitarray.__new__, bitarray, 'a', i)
        
        self.assertRaises(TypeError, bitarray.__new__, bitarray, '', 0, 42)
        self.assertRaises(ValueError, bitarray.__new__, bitarray, '', 0, 'foo')
        
        
tests.append(CreateObjectTests)

# ---------------------------------------------------------------------------

class MetaDataTests(unittest.TestCase):
    
    def test_buffer_info(self):
        a = bitarray('0000111100001', endian='little')
        self.assertEqual(a.buffer_info()[1:], (2, 'little', 3))
        
        a = bitarray()
        self.assertRaises(TypeError, a.buffer_info, 42)
        
        bi = a.buffer_info()
        self.assert_(isinstance(bi, tuple))
        self.assertEqual(len(bi), 4)
        
        self.assert_(isinstance(bi[0], (int, long)))
        self.assert_(isinstance(bi[1], int))
        self.assert_(isinstance(bi[2], str))
        self.assert_(isinstance(bi[3], int))
        
        for n in xrange(50):
            bi = bitarray(n).buffer_info()
            self.assertEqual(bi[1], bits2bytes(n))
            self.assertEqual(bi[3], 8 * bits2bytes(n) - n)
        
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
        for n in xrange(1000):
            a = bitarray(n)
            self.assertEqual(len(a), n)
            self.assertEqual(a.length(), n)


tests.append(MetaDataTests)

# ---------------------------------------------------------------------------

class SliceTests(unittest.TestCase, Util):
    
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
        
        for a in self.randombitarrays():
            aa = a.tolist()
            la = len(a)
            if la == 0: continue
            for dum in xrange(10):
                step = self.rndsliceidx(la)
                if step == 0: step = None
                s = slice(self.rndsliceidx(la),
                          self.rndsliceidx(la), step)
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
        
        for a in self.randombitarrays():
            la = len(a)
            if la == 0: continue
            for dum in xrange(3):
                step = self.rndsliceidx(la)
                if step == 0: step = None
                s = slice(self.rndsliceidx(la),
                          self.rndsliceidx(la), step)
                for b in self.randombitarrays():
                    if len(b) == self.slicelen(s, len(a)) or step is None:
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
        
        for a in self.randombitarrays():
            la = len(a)
            if la == 0: continue
            for dum in xrange(10):
                step = self.rndsliceidx(la)
                if step == 0: step = None
                s = slice(self.rndsliceidx(la),
                          self.rndsliceidx(la), step)
                c = bitarray(a)
                d = c
                del c[s]
                self.assert_(c is d)
                self.check_obj(c)
                cc = a.tolist()
                del cc[s]
                self.assertEQUAL(c, bitarray(cc, endian=c.endian()))


tests.append(SliceTests)

# ---------------------------------------------------------------------------

class MiscTests(unittest.TestCase, Util):

    def test_booleanness(self):
        self.assertEqual(bool(bitarray('')), False)
        self.assertEqual(bool(bitarray('0')), True)
        self.assertEqual(bool(bitarray('1')), True)


    def test_iterate(self):
        for lst in self.randomlists():
            acc = []
            for b in bitarray(lst):
                acc.append(b)
            self.assertEqual(acc, lst)


    def test_asDictKey(self):
        d = {bitarray('011') : 3,
             bitarray('101') : 5,
             bitarray('001') : 1,
             bitarray('000') : 0,
             bitarray('1111') : 15}

        self.assertEqual(d[bitarray('000')], 0)


    def test_subclassing(self):
        class ExaggeratingBitarray(bitarray):
            
            def __new__(cls, data, offset):
                return bitarray.__new__(cls, data)
            
            def __init__(self, data, offset):
                self.offset = offset

            def __getitem__(self, i):
                return bitarray.__getitem__(self, i - self.offset)
            
        for a in self.randombitarrays():
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
        
        a = bitarray('00100000', endian='big')
        self.assertEqual(a.tostring(), ' ')
        
        b = bitarray('00000100', endian='little')
        self.assertEqual(b.tostring(), ' ')

        self.assertNotEqual(a, b)

        a = bitarray('11100000', endian='little')
        b = bitarray(a, endian='big')
        self.assertNotEqual(a, b)
        self.assertEqual(a.tostring(), b.tostring())


    def test_pickle(self):
        from pickle import loads, dumps
        for a in self.randombitarrays():
            b = loads(dumps(a))
            self.assert_(b is not a)
            self.assertEQUAL(a, b)


    def test_cPickle(self):
        from cPickle import loads, dumps
        for a in self.randombitarrays():
            b = loads(dumps(a))
            self.assert_(b is not a)
            self.assertEQUAL(a, b)


tests.append(MiscTests)

# ---------------------------------------------------------------------------

class SpecialMethodTests(unittest.TestCase, Util):

    def test_all(self):
        a = bitarray()
        self.assertTrue(a.all())
        
        for a in self.randombitarrays():
            self.assertEqual(all(a),          a.all())
            self.assertEqual(all(a.tolist()), a.all())

            
    def test_any(self):
        a = bitarray()
        self.assertFalse(a.any())
        
        for a in self.randombitarrays():
            self.assertEqual(any(a),          a.any())
            self.assertEqual(any(a.tolist()), a.any())


    def test_repr(self):
        a = bitarray()
        self.assertEqual(repr(a), "bitarray()")
        
        a = bitarray('10111')
        self.assertEqual(repr(a), "bitarray('10111')")
        
        for a in self.randombitarrays():
            b = eval(repr(a))
            self.assert_(b is not a)
            self.assertEqual(a, b)
            self.check_obj(b)


    def test_copy(self):
        import copy
        for a in self.randombitarrays():
            b = copy.copy(a)
            self.assert_(b is not a)
            self.assertEQUAL(a, b)
            
            b = copy.deepcopy(a)
            self.assert_(b is not a)
            self.assertEQUAL(a, b)


    def test_compare(self):
        for a in self.randombitarrays():
            aa = a.tolist()
            
            for b in self.randombitarrays():
                bb = b.tolist()
                self.assertEqual(a == b, aa == bb)
                self.assertEqual(a != b, aa != bb)
                self.assertEqual(a <= b, aa <= bb)
                self.assertEqual(a <  b, aa <  bb)
                self.assertEqual(a >= b, aa >= bb)
                self.assertEqual(a >  b, aa >  bb)


    def test_add(self):
        c = bitarray('001') + bitarray('110')
        self.assertEQUAL(c, bitarray('001110'))
        
        for a in self.randombitarrays():
            for b in self.randombitarrays():
                c = a + b
                self.assertEqual(c, bitarray(a.tolist() + b.tolist()))
                self.assertEqual(c.endian(), a.endian())
                self.check_obj(c)
                
        a = bitarray()
        self.assertRaises(TypeError, a.__add__, 42)


    def test_iadd(self):
        c = bitarray('001')
        c += bitarray('110')
        self.assertEQUAL(c, bitarray('001110'))
        
        for a in self.randombitarrays():
            for b in self.randombitarrays():
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
        c = 0 * bitarray('1001111')
        self.assertEQUAL(c, bitarray())
        
        c = 3 * bitarray('001')
        self.assertEQUAL(c, bitarray('001001001'))

        c = bitarray('110') * 3
        self.assertEQUAL(c, bitarray('110110110'))
        
        for a in self.randombitarrays():
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
        c = bitarray('1101110011')
        c *= 0
        self.assertEQUAL(c, bitarray())
        
        c = bitarray('110')
        c *= 3
        self.assertEQUAL(c, bitarray('110110110'))
        
        for a in self.randombitarrays():
            for n in xrange(-10, 10):
                b = bitarray(a)
                c = b
                c *= n
                self.assertEQUAL(c, bitarray(n * a.tolist(),
                                             endian=a.endian()))
                self.assert_(c is b)
        
        a = bitarray()
        self.assertRaises(TypeError, a.__imul__, None)


tests.append(SpecialMethodTests)

# ---------------------------------------------------------------------------

class SequenceTests(unittest.TestCase, Util):

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


tests.append(SequenceTests)

# ---------------------------------------------------------------------------

class MethodTests(unittest.TestCase, Util):

    def test_append(self):
        a = bitarray()
        a.append(True)
        a.append(False)
        a.append(False)
        self.assertEQUAL(a, bitarray('100'))
        
        for a in self.randombitarrays():
            aa = a.tolist()
            b = a
            b.append(1)
            self.assert_(a is b)
            self.check_obj(b)
            self.assertEQUAL(b, bitarray(aa+[1], endian=a.endian()))
            b.append('')
            self.assertEQUAL(b, bitarray(aa+[1, 0], endian=a.endian()))


    def test_extend(self): # FIXME: This sould be in its own test class
        a = bitarray()
        a.extend([-1, None, 1, 0, 2])
        self.assertEQUAL(a, bitarray('10101'))

        self.assertRaises(TypeError, a.extend)
        self.assertRaises(TypeError, a.extend, None)
        self.assertRaises(TypeError, a.extend, True)
        self.assertRaises(TypeError, a.extend, 24)
        self.assertRaises(ValueError, a.extend, '0011201')
        
        a = bitarray()
        a.extend(bitarray('01'))
        a.extend([0, 1])
        a.extend((0, 1))
        a.extend('01')
        self.assertEqual(a, bitarray('01010101'))
        
        for a in self.randomlists():
            for b in self.randombitarrays():
                c = bitarray(a)
                idc = id(c)
                c.extend(b)                             # bitarray
                self.assertEqual(id(c), idc)
                self.assertEqual(c, bitarray(a + b.tolist()))

            for b in self.randomlists():
                c = bitarray(a)
                idc = id(c)
                c.extend(b)                               # list
                self.assertEqual(id(c), idc)
                self.assertEqual(c.tolist(), a + b)
                self.check_obj(c)

                def foo():
                    for e in b:
                        yield e
                c = bitarray(a)
                idc = id(c)
                c.extend(foo())                          # iterable
                self.assertEqual(id(c), idc)
                self.assertEqual(c.tolist(), a + b)
                self.check_obj(c)

                c = bitarray(a)
                idc = id(c)
                c.extend(tuple(b))                          # tuple
                self.assertEqual(id(c), idc)
                self.assertEqual(c.tolist(), a + b)
                self.check_obj(c)

                c = bitarray(a)
                idc = id(c)
                c.extend(iter(b))                          # iter
                self.assertEqual(id(c), idc)
                self.assertEqual(c.tolist(), a + b)
                self.check_obj(c)

                c = bitarray(a)
                idc = id(c)
                c.extend(''.join(('1' if x else '0')
                                 for x in b))                 # string01
                self.assertEqual(id(c), idc)
                self.assertEqual(c.tolist(), a + b)
                self.check_obj(c)

                def foo():
                    for x in b:
                        yield x
                c = bitarray(a)
                idc = id(c)
                c.extend(foo())                             # iter2
                self.assertEqual(id(c), idc)
                self.assertEqual(c.tolist(), a + b)
                self.check_obj(c)


    def test_insert(self):
        a = bitarray()
        b = a
        a.insert(0, True)
        self.assert_(a is b)
        self.assertEqual(a, bitarray('1'))
        self.assertRaises(TypeError, a.insert)
        self.assertRaises(TypeError, a.insert, None)

        for a in self.randombitarrays():
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


    def test_count(self):
        a = bitarray('10011')
        self.assertEqual(a.count(True), 3)
        self.assertEqual(a.count(False), 2)
        self.assertEqual(a.count('foo'), 3)
        self.assertEqual(a.count({}), 2)
        for a in self.randombitarrays():
            self.assertEqual(a.count(1), a.to01().count('1'))
            self.assertEqual(a.count(0), a.to01().count('0'))


    def test_fill(self):
        a = bitarray('')
        self.assertEqual(a.fill(), 0)
        self.assertEqual(len(a), 0)
        
        a = bitarray('101')
        self.assertEqual(a.fill(), 5)
        self.assertEQUAL(a, bitarray('10100000'))
        self.assertEqual(a.fill(), 0)
        self.assertEQUAL(a, bitarray('10100000'))
        
        for a in self.randombitarrays():
            aa = a.tolist()
            la = len(a)
            b = a
            self.assert_(0 <= b.fill() < 8)
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
        

    def test_sort(self):
        a = bitarray('1101000')
        a.sort()
        self.assertEqual(a, bitarray('0000111'))
        
        for a in self.randombitarrays():
            ida = id(a)
            a.sort()
            self.assertEqual(a, bitarray(sorted(a.tolist())))
            self.assertEqual(id(a), ida)


    def test_reverse(self):
        self.assertRaises(TypeError, bitarray().reverse, 42)

        a = bitarray()
        a.reverse()
        self.assertEQUAL(a, bitarray())

        a = bitarray('1001111')
        a.reverse()
        self.assertEQUAL(a, bitarray('1111001'))

        a = bitarray('11111000011')
        a.reverse()
        self.assertEQUAL(a, bitarray('11000011111'))
        
        for a in self.randombitarrays(100):
            aa = a.tolist()
            ida = id(a)
            a.reverse()
            self.assertEqual(ida, id(a))
            self.assertEQUAL(a, bitarray(aa[::-1], endian=a.endian()))


    def test_fromlist(self):
        a = bitarray()
        a.fromlist([]);         self.assertEQUAL(a, bitarray())
        a.fromlist([1]);        self.assertEQUAL(a, bitarray('1'))
        a.fromlist([0, 1, 1]);  self.assertEQUAL(a, bitarray('1011'))
        
        for a in self.randombitarrays():
            for blst in self.randomlists():
                alst = a.tolist()
                c = a
                c.fromlist(blst)
                self.assertEqual(c.tolist(), alst + blst)
                self.assert_(c is a)
                self.check_obj(c)
                
        
    def test_tolist(self):
        a = bitarray()
        self.assertEqual(a.tolist(), [])
        
        a = bitarray('110')
        self.assertEqual(a.tolist(), [True, True, False])
        
        for lst in self.randomlists():
            a = bitarray(lst)
            self.assertEqual(a.tolist(), lst)
       

    def test_remove(self):
        a = bitarray()
        for i in (True, False, 1, 0):
            self.assertRaises(ValueError, a.remove, i)

        a = bitarray(21)
        a.setall(0)
        self.assertRaises(ValueError, a.remove, 1)
        a.setall(1)
        self.assertRaises(ValueError, a.remove, 0)

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
        
        for a in self.randombitarrays():        
            self.assertRaises(IndexError, a.pop, len(a))
            self.assertRaises(IndexError, a.pop, -len(a)-1)
            if len(a) == 0:
                continue
            aa = a.tolist()
            enda = a.endian()
            self.assertEqual(a.pop(), aa[-1])
            self.check_obj(a)
            self.assertEqual(a.endian(), enda)
            
        for a in self.randombitarrays():
            if len(a) == 0:
                continue
            n = randint(-len(a), len(a)-1)
            aa = a.tolist()
            self.assertEqual(a.pop(n), aa[n])
            self.check_obj(a)
            

    def test_setall(self):
        a = bitarray(5)
        a.setall(True)
        self.assertEQUAL(a, bitarray('11111'))
        
        for a in self.randombitarrays():
            val = randint(0, 1)
            b = a
            b.setall(val)
            self.assertEqual(b, bitarray(len(b)*[val]))
            self.assert_(a is b)
            self.check_obj(b)

  
    def test_invert(self):
        a = bitarray()
        a.invert()
        self.assertEQUAL(a, bitarray())
        
        a = bitarray('11011')
        a.invert()
        self.assertEQUAL(a, bitarray('00100'))
        
        for a in self.randombitarrays():
            aa = a.tolist()
            b = a
            b.invert()
            for i in xrange(len(a)):
                self.assertEqual(b[i], not aa[i])
            self.assert_(a is b)
            self.check_obj(b)


    def test_bytereverse(self):
        a = bitarray()
        a.bytereverse()
        self.assertEqual(a, bitarray())
        
        a = bitarray('1011')
        a.bytereverse()
        self.assertEqual(a, bitarray('0000'))
        
        a = bitarray('111011')
        a.bytereverse()
        self.assertEqual(a, bitarray('001101'))
        
        a = bitarray('11101101')
        a.bytereverse()
        self.assertEqual(a, bitarray('10110111'))
        
        for i in xrange(256):
            a = bitarray(chr(i), 0)
            aa = a.tolist()
            b = a
            b.bytereverse()
            self.assertEqual(b, bitarray(aa[::-1]))
            self.assert_(a is b)
            self.check_obj(b)


tests.append(MethodTests)

# ---------------------------------------------------------------------------

class StringTests(unittest.TestCase, Util):
    
    def randomstrings(self):
        for n in xrange(1, 20):
            yield ''.join(chr(randint(0, 255)) for x in xrange(n))


    def test_fromstring(self):
        a = bitarray()
        a.fromstring('A')
        self.assertEqual(a, bitarray('A', 0))
        
        b = a
        b.fromstring('BC')
        self.assertEQUAL(b, bitarray('ABC', 0))
        self.assert_(b is a)
        
        for b in self.randombitarrays():
            c = b.__copy__()
            b.fromstring('')
            self.assertEQUAL(b, c)
        
        for b in self.randombitarrays():
            for s in self.randomstrings():
                a = bitarray(s, 0, endian=b.endian())
                c = b.__copy__()
                b.fromstring(s)
                self.assertEQUAL(b[-len(a):], a)
                self.assertEQUAL(b[:-len(a)], c)
                self.assertEQUAL(c + a, b)
 

    def test_tostring(self):
        a = bitarray()
        self.assertEqual(a.tostring(), '')
        
        for end in ('big', 'little'):
            a = bitarray('foo', 0, endian=end)
            self.assertEqual(a.tostring(), "foo")

            for s in self.randomstrings():
                a = bitarray(endian=end)
                a.fromstring(s)
                self.assertEqual(a.tostring(), s)

        for n, s in [(1, '\x01'), (2, '\x03'), (3, '\x07'), (4, '\x0f'),
                     (5, '\x1f'), (6, '\x3f'), (7, '\x7f'), (8, '\xff'),
                     (12, '\xff\x0f'), (15, '\xff\x7f'), (16, '\xff\xff'),
                     (17, '\xff\xff\x01'), (24, '\xff\xff\xff')]:
            a = bitarray(n, endian='little')
            a.setall(1)
            self.assertEqual(a.tostring(), s)


    def test_tofrom01(self):
        for a in self.randombitarrays():
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


tests.append(StringTests)

# ---------------------------------------------------------------------------

class FileTests(unittest.TestCase, Util):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.tmpfname = os.path.join(self.tmpdir, 'testfile')
        

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


    def test_cPickle(self):
        from cPickle import load, dump

        for a in self.randombitarrays():
            fo = open(self.tmpfname, 'wb')
            dump(a, fo)
            fo.close()
            
            b = load(open(self.tmpfname, 'rb'))
            
            self.assert_(b is not a)
            self.assertEQUAL(a, b)


    def test_fromfile_wrong_args(self):
        b = bitarray()
        self.assertRaises(TypeError, b.fromfile)
        self.assertRaises(TypeError, b.fromfile, StringIO()) # not open
        self.assertRaises(TypeError, b.fromfile, 42)
        self.assertRaises(TypeError, b.fromfile, 'bar')


    def test_from_empty_file(self):
        fo = open(self.tmpfname, 'wb')
        fo.close()

        a = bitarray()
        a.fromfile(open(self.tmpfname, 'rb'))
        self.assertEqual(a, bitarray())


    def test_fromfile_Foo(self):
        fo = open(self.tmpfname, 'wb')
        fo.write('Foo\n')
        fo.close()

        a = bitarray(endian='big')
        a.fromfile(open(self.tmpfname, 'rb'))
        self.assertEqual(a, bitarray('01000110011011110110111100001010'))

        a = bitarray(endian='little')
        a.fromfile(open(self.tmpfname, 'rb'))
        self.assertEqual(a, bitarray('01100010111101101111011001010000'))

        a = bitarray('1', endian='little')
        a.fromfile(open(self.tmpfname, 'rb'))
        self.assertEqual(a, bitarray('101100010111101101111011001010000'))

        for n in xrange(20):
            a = bitarray(n, endian='little')
            a.setall(1)
            a.fromfile(open(self.tmpfname, 'rb'))
            self.assertEqual(a,
                             n*bitarray('1') +
                             bitarray('01100010111101101111011001010000'))


    def test_fromfile_n(self):
        a = bitarray('ABCDEFGHIJ', 0)
        fo = open(self.tmpfname, 'wb')
        a.tofile(fo)
        fo.close()
        
        b = bitarray()
        f = open(self.tmpfname, 'rb')
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
        f = open(self.tmpfname, 'rb')
        f.read(1);
        self.assertRaises(EOFError, b.fromfile, f, 10)
        f.close()
        self.assertEqual(b.tostring(), 'BCDEFGHIJ')
        
        b = bitarray()
        f = open(self.tmpfname, 'rb')
        b.fromfile(f);
        self.assertEqual(b.tostring(), 'ABCDEFGHIJ')
        self.assertRaises(EOFError, b.fromfile, f, 1)
        f.close()

        
    def test_tofile(self):
        a = bitarray()
        f = open(self.tmpfname, 'wb')
        a.tofile(f)
        f.close()

        fi = open(self.tmpfname, 'rb')
        self.assertEqual(fi.read(), '')
        fi.close()

        a = bitarray('01000110011011110110111100001010', endian='big')
        f = open(self.tmpfname, 'wb')
        a.tofile(f)
        f.close()

        fi = open(self.tmpfname, 'rb')
        self.assertEqual(fi.read(), 'Foo\n')
        fi.close()

        for a in self.randombitarrays():
            b = bitarray(a, endian='big')
            fo = open(self.tmpfname, 'wb')
            b.tofile(fo)
            fo.close()
            
            s = open(self.tmpfname, 'rb').read()
            self.assertEqual(len(s), a.buffer_info()[1])

        for n in xrange(10):
            a = bitarray(n * 'A', 0)
            self.assertRaises(TypeError, a.tofile)
            self.assertRaises(TypeError, a.tofile, StringIO())
            
            f = open(self.tmpfname, 'wb')
            a.tofile(f)
            f.close()
            self.assertRaises(TypeError, a.tofile, f)

        for n in xrange(20):
            a = n * bitarray('1', endian='little')
            fo = open(self.tmpfname, 'wb')
            a.tofile(fo)
            fo.close()
            
            s = open(self.tmpfname, 'rb').read()
            self.assertEqual(len(s), a.buffer_info()[1])
            
            b = a.__copy__()
            b.fill()
            self.assertEqual(bitarray(s, 0, endian='little'), b)


tests.append(FileTests)

# ---------------------------------------------------------------------------

def pages():
    dat = open('/proc/%i/statm' % os.getpid()).read()
    return int(dat.split()[0])


def run(verbosity, chk_mem_leaks=False):
    suite = unittest.TestSuite()
    for cls in tests:
        suite.addTest(unittest.makeSuite(cls))
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    res = runner.run(suite)

    if chk_mem_leaks:
        if sys.platform.startswith('linux'):
            a = pages()
            for x in xrange(100):
                runner.run(suite)
                print 'pages:', pages()
            b = pages()
            print 'Pages before and after tests:', a, b
        else:
            print 'Sorry, can only test for memory leaks on Linux.'

    return res


if __name__ == '__main__':
    # For development
    arg = ''
    if len(sys.argv)==2:
        arg = sys.argv[1]
    
    run(verbosity     = 2 if 'v' in arg else 1,
        chk_mem_leaks = bool('m' in arg),
        )

else:
    from bitarray import __version__
    print 'bitarray is installed in:', os.path.dirname(__file__)
    print 'bitarray version:', __version__
    print sys.version
