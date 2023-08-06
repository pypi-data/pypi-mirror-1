/* Bitarray object implementation
   A bitarray is a uniform list -- all items are of type bool.
   
   Author: Ilan Schnell <ilanschnell@gmail.com>
*/

#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#ifdef STDC_HEADERS
#include <stddef.h>
#else  /* !STDC_HEADERS */
#ifdef HAVE_SYS_TYPES_H
#include <sys/types.h>		/* For size_t */
#endif /* HAVE_SYS_TYPES_H */
#endif /* !STDC_HEADERS */

typedef int64_t idx_t;

/* throughout:  0 = little endian    1 = big endian */
#define DEFAULT_ENDIAN 1

typedef struct {
	PyObject_VAR_HEAD
	char *ob_item;
	Py_ssize_t allocated;
	idx_t nbits;
        int endian;
	PyObject *weakreflist;   /* List of weak references */
} bitarrayobject;

static PyTypeObject Bitarraytype;

#define bitarray_Check(obj) PyObject_TypeCheck(obj, &Bitarraytype)


/* Return number of bytes necessary to store nbits */
static inline size_t
bytes_bits(idx_t nbits)
{
	return (nbits == 0)  ?  0  :  ((nbits - 1) / 8 + 1);
}

/* ------------ Low level access to bits in bitarrayobject ------------- */

/* The visible impact of self->endian are the conversions to and from
   machine values: fromfile, tofile, fromstring, tostring
*/
static inline char
bitmask(int endian, idx_t i)
{
        return 1 << (endian  ?  7 - i%8  :  i%8);
}

static inline int
getbit(bitarrayobject *self, idx_t i)
{
        return (self->ob_item[i/8] & bitmask(self->endian, i)) ? 1 : 0;
}

static inline void
setbit(bitarrayobject *self, idx_t i, int bit)
{
	char *cp, mask;

	mask = bitmask(self->endian, i);
	cp = self->ob_item + i/8;
	if (bit)
		*cp |= mask;
	else
		*cp &= ~mask;
}


static int
resize(bitarrayobject *self, Py_ssize_t newsize)
{
	/* Bypass realloc() when a previous overallocation is large enough
	   to accommodate the newsize.  If the newsize is 16 smaller than the
	   current size, then proceed with the realloc() to shrink the list.
	*/
	if (self->allocated >= newsize &&
	    self->ob_size < newsize + 16 &&
	    self->ob_item != NULL) {
		self->ob_size = newsize;
		return 0;
	}
	/* This over-allocates proportional to the bitarray size, making room
	   for additional growth.  The over-allocation is mild, but is
	   enough to give linear-time amortized behavior over a long
	   sequence of appends() in the presence of a poorly-performing
	   system realloc().
	   The growth pattern is:  0, 4, 8, 16, 25, 34, 46, 56, 67, 79, ...
	   Note, the pattern starts out the same as for lists but then
	   grows at a smaller rate so that larger bitarrays only overallocate
	   by about 1/16th -- this is done because bitarrays are assumed to be
	   memory critical.
	 */
	char *item;
	size_t _new_size;
	
	_new_size = (newsize >> 4) + (self->ob_size < 8 ? 3 : 7) + newsize;
	
	item = self->ob_item;
	PyMem_RESIZE(item, char, (_new_size));
	if (item == NULL) {
		PyErr_NoMemory();
		return -1;
	}
	self->ob_item = item;
	self->ob_size = newsize;
	self->allocated = _new_size;
	return 0;
}

static PyObject *
newbitarrayobject(PyTypeObject *type, idx_t nbits, int endian)
{
	bitarrayobject *obj;
	Py_ssize_t nbytes;
	
	assert (endian >= 0 || endian <= 1 && nbits >= 0);
	nbytes = bytes_bits(nbits);
	
	/* Check for overflow */
	if (nbytes != ((nbits == 0) ? 0 : ((nbits - 1) / 8 + 1))) {
		PyErr_NoMemory();
		return NULL;
	}
	obj = (bitarrayobject *) type->tp_alloc(type, 0);
	if (obj == NULL)
		return NULL;
	obj->ob_size = nbytes;
	obj->nbits = nbits;
	obj->endian = endian;
	if (nbytes == 0) {
		obj->ob_item = NULL;
	} else {
		obj->ob_item = PyMem_NEW(char, nbytes);
		if (obj->ob_item == NULL) {
			PyObject_Del(obj);
			PyErr_NoMemory();
			return NULL;
		}
	}
	obj->allocated = nbytes;
	obj->weakreflist = NULL;
	return (PyObject *) obj;
}

static inline int
set_item(bitarrayobject *self, idx_t i, PyObject *v)
{
	long vi;
	
	vi = PyObject_IsTrue(v);
	if (vi < 0 || i < 0 || i >= self->nbits)
		return -1;
	setbit(self, i, vi);
	return 0;
}

static int
append_item(bitarrayobject *self, PyObject *item)
{
	if (self->nbits + 1 > 8 * (idx_t) self->ob_size &&
	    resize(self, self->ob_size + 1) == -1)
		return -1;
	
	return set_item(self, self->nbits++, item);
}

static int
extend_bitarray(bitarrayobject *self, bitarrayobject *b)
{
	idx_t i, newbitsize;
	size_t newsize;

	if (b->nbits == 0)
        	return 0;
	
	newbitsize = self->nbits + b->nbits;
	newsize = bytes_bits(newbitsize);
	PyMem_RESIZE(self->ob_item, char, newsize);
	if (self->ob_item == NULL) {
		PyObject_Del(self);
		PyErr_NoMemory();
		return -1;
	}
	if (self->nbits % 8 == 0 && self->endian == b->endian) {
		memcpy(self->ob_item + self->ob_size, b->ob_item, b->ob_size);
	} else {
		for (i = 0; i < b->nbits; i++)
			setbit(self, self->nbits + i, getbit(b, i));
	}
	self->ob_size = newsize;
	self->allocated = newsize;
	self->nbits = newbitsize;
	
	return 0;
}

static int
extend_iter(bitarrayobject *self, PyObject *iter)
{
	PyObject *v;
	
	assert (PyIter_Check(iter));
	while ((v = PyIter_Next(iter)) != NULL) {
		if (append_item(self, v) < 0) {
			Py_DECREF(v);
			return -1;
		}
		Py_DECREF(v);
	}
	if (PyErr_Occurred())
		return -1;

	return 0;
}

static int
extend_list(bitarrayobject *self, PyObject *list)
{
	Py_ssize_t addbits;
	size_t i;
	
	assert (PyList_Check(list));
	addbits = PyList_Size(list);
	if (addbits == 0)
	        return 0;

	self->nbits += addbits;
	if (resize(self, bytes_bits(self->nbits)) == -1)
		return -1;
	
	for (i = 0; i < addbits; i++)
		set_item(self,
			 self->nbits - addbits + i,
			 PyList_GetItem(list, i));
	
	return 0;
}

static int
extend_tuple(bitarrayobject *self, PyObject *tuple)
{
	Py_ssize_t addbits;
	size_t i;
	
	assert (PyTuple_Check(tuple));
	addbits = PyTuple_Size(tuple);
	if (addbits == 0)
	        return 0;

	self->nbits += addbits;
	if (resize(self, bytes_bits(self->nbits)) == -1)
		return -1;
	
	for (i = 0; i < addbits; i++)
		set_item(self,
			 self->nbits - addbits + i,
			 PyTuple_GetItem(tuple, i));
	return 0;
}

static int
extend_string01(bitarrayobject *self, PyObject *string)
{
	Py_ssize_t addbits;
	char c, *str, *item;
	size_t i;
	int vi;

	assert (PyString_Check(string));
	addbits = PyString_Size(string);
	if (addbits == 0)
	        return 0;

	str = PyString_AsString(string);
	item = self->ob_item;
	
	self->nbits += addbits;
	if (resize(self, bytes_bits(self->nbits)) == -1)
		return -1;
	
	for (i = 0; i < addbits; i++) {
		c = *(str + i);
		if (c == '0') {
			vi = 0;
		}
		else if (c == '1') {
			vi = 1;
		}
		else {
			char buff[256];
			sprintf(buff,
				"character must be '0' or '1', "
				"found '%c'", c);
			PyErr_SetString(PyExc_ValueError, buff);
			return -1;
		}
		setbit(self, self->nbits - addbits + i, vi);
	}
	return 0;
}

static int
extend_string(bitarrayobject *self, PyObject *string)
{
	Py_ssize_t addbytes;
	char *str;
	
	assert (PyString_Check(string) || self->nbits % 8 == 0);
	addbytes = PyString_Size(string);
	if (addbytes == 0)
		return 0;
	
	str = PyString_AsString(string);
	
	self->nbits += 8 * (idx_t) addbytes;
	if (resize(self, self->ob_size + addbytes) == -1)
		return -1;
	
	assert (self->nbits == 8 * (idx_t) self->ob_size);
	memcpy(self->ob_item + (self->ob_size - addbytes), str, addbytes);
	
	return 0;
}

static int
setlastzero(bitarrayobject *self)
{
        idx_t i, n, p;
	
	n = 8 * (idx_t) self->ob_size;
	for (i = self->nbits; i < n; i++)
		setbit(self, i, 0);
	p = n - self->nbits;
	assert (p >= 0 && p < 8);
	return (int) p;
}

/* Return number of 1 bits */
static idx_t
count(bitarrayobject *self)
{
	static int bytecount[256];
	static int setup = 0;
	if (!setup) {
		int j, k;
		for (k = 0; k < 256; k++) {
			bytecount[k] = 0;
			for(j = 0; j < 8; j++)
				bytecount[k] += (k >> j) & 1;
		}
		setup = 1;
	}
	idx_t res;
	size_t i;
	int c;

	res = 0;
        setlastzero(self);
	for (i = 0; i < self->ob_size; i++) {
		c = self->ob_item[i];
		/* in case conversion to int puts sign in */
		if (c < 0)
		        c += 256;
		res += bytecount[c];
	}
	return res;
}

static void
dealloc(bitarrayobject *obj)
{
	if (obj->weakreflist != NULL)
		PyObject_ClearWeakRefs((PyObject *) obj);
	
	if (obj->ob_item != NULL)
		PyMem_DEL(obj->ob_item);
	
	obj->ob_type->tp_free((PyObject *) obj);
}

/*  Return index of first occurence of x, -1 when x is not in found. */
static idx_t
findfirst(bitarrayobject *self, int bit)
{
	size_t n;
	idx_t i;
	char c;
	
	if (bit)
	        bit = 1;
	assert (bit == 0 || bit == 1);
	
	/* skip ahead by checking whole bytes */
	c = 0xff * (1-bit);
	for (n = 0; n < self->ob_size; n++)
		if (c ^ self->ob_item[n])
			break;
	if (n == self->ob_size)
                n--;
	if (n < 0)
                n = 0;
	
	/* fine graded search within byte */
	for (i = 8 * (idx_t) n; i < self->nbits; i++)
		if (getbit(self, i) == bit)
			return i;

	return -1;
}

static PyObject *
richcompare(PyObject *v, PyObject *w, int op)
{
	bitarrayobject *va, *wa;
	int cmp, k;
	int vi=0, wi=0; /* avoid uninitialized warning for some compilers */
	idx_t i;
	
	if (!bitarray_Check(v) || !bitarray_Check(w)) {
		Py_INCREF(Py_NotImplemented);
		return Py_NotImplemented;
	}
	va = (bitarrayobject *)v;
	wa = (bitarrayobject *)w;
	if (va->nbits != wa->nbits && (op == Py_EQ || op == Py_NE)) {
		/* Shortcut: if the lengths differ, the bitarrays differ */
		if (op == Py_EQ)
			Py_RETURN_FALSE;
		
		Py_RETURN_TRUE;
	}
	/* Search for the first index where items are different */
	k = 1;
	for (i = 0; i < va->nbits && i < wa->nbits; i++) {
		vi = getbit(va, i);
		wi = getbit(wa, i);
		k = (vi == wi);
		if (k == 0)
			break;
	}
	if (k) {
		/* No more items to compare -- compare sizes */
		idx_t vs = va->nbits;
		idx_t ws = wa->nbits;
		switch (op) {
		case Py_LT: cmp = vs <  ws; break;
		case Py_LE: cmp = vs <= ws; break;
		case Py_EQ: cmp = vs == ws; break;
		case Py_NE: cmp = vs != ws; break;
		case Py_GT: cmp = vs >  ws; break;
		case Py_GE: cmp = vs >= ws; break;
		default: return NULL; /* cannot happen */
		}
		if (cmp)
			Py_RETURN_TRUE;
		
		Py_RETURN_FALSE;
	}
	/* We have an item that differs.  First, shortcuts for EQ/NE */
	if (op == Py_EQ)
		Py_RETURN_FALSE;
	
	if (op == Py_NE)
		Py_RETURN_TRUE;

	/* Compare the final item using the proper operator */
	switch (op) {
	case Py_LT: cmp = vi <  wi; break;
	case Py_LE: cmp = vi <= wi; break;
	case Py_EQ: cmp = vi == wi; break;
	case Py_NE: cmp = vi != wi; break;
	case Py_GT: cmp = vi >  wi; break;
	case Py_GE: cmp = vi >= wi; break;
	default: return NULL; /* cannot happen */
	}
	if (cmp)
		Py_RETURN_TRUE;
	
	Py_RETURN_FALSE;
}

/****************************************************************************
               Implementations of bitarray object methods follow.
****************************************************************************/

static PyObject *
bitarray_length(bitarrayobject *self)
{
	return PyLong_FromLongLong(self->nbits);
}

PyDoc_STRVAR(length_doc,
"length()\n\
\n\
Return the length (number of bits) of the bitarray.");


static PyObject *
bitarray_copy(bitarrayobject *a)
{
	PyObject *b;
	
	b = newbitarrayobject(a->ob_type, a->nbits, a->endian);
	memcpy(((bitarrayobject *) b)->ob_item, a->ob_item, a->ob_size);
	return b;
}

PyDoc_STRVAR(copy_doc,
"copy(bitarray)\n\
\n\
Return a copy of the bitarray.");


static PyObject *
bitarray_count(bitarrayobject *self, PyObject *v)
{
        idx_t res;
	long vi;
	
	vi = PyObject_IsTrue(v);
	if (vi < 0)
		return NULL;
	if (vi)
	        res = count(self);
	else
         	res = self->nbits - count(self);
	
	return PyLong_FromLongLong(res);
}

PyDoc_STRVAR(count_doc,
"count(x)\n\
\n\
Return number of occurences of x in the bitarray.");


static PyObject *
bitarray_index(bitarrayobject *self, PyObject *v)
{
	idx_t i;
	long vi;
	
	vi = PyObject_IsTrue(v);
	if (vi < 0)
		return NULL;
	
	i = findfirst(self, vi);
	if (i >= 0) {
		return PyLong_FromLongLong(i);
	}
	else {
		PyErr_SetString(PyExc_ValueError,
				"bitarray.index(x): x not in bitarray");
		return NULL;
	}
}

PyDoc_STRVAR(index_doc,
"index(x)\n\
\n\
Return index of first occurence of x in the bitarray.  It is an error when x\n\
does not occur in the bitarray");


static PyObject *
bitarray_contains(bitarrayobject *self, PyObject *v)
{
	idx_t i;
	long vi;
	
	vi = PyObject_IsTrue(v);
	if (vi < 0)
		return NULL;
	i = findfirst(self, vi);
	if (i >= 0)
		Py_RETURN_TRUE;
	Py_RETURN_FALSE;
}

PyDoc_STRVAR(contains_doc,
"__contains__(x)\n\
\n\
Return True if bitarray contains x, False otherwise.");


static PyObject *
bitarray_extend(bitarrayobject *self, PyObject *obj)
{
        /* dispatch on type */
	if (bitarray_Check(obj)) {                           /* bitarray */
		if (extend_bitarray(self, (bitarrayobject *) obj) == -1)
			return NULL;
		Py_RETURN_NONE;
	}
	if (PyList_Check(obj)) {                                 /* list */
		if (extend_list(self, obj) == -1)
			return NULL;
		Py_RETURN_NONE;
	}
	if (PyTuple_Check(obj)) {                               /* tuple */
		if (extend_tuple(self, obj) == -1)
			return NULL;
		Py_RETURN_NONE;
	}
	if (PyString_Check(obj)) {                              /* str01 */
		if (extend_string01(self, obj) == -1)
			return NULL;
		Py_RETURN_NONE;
	}
	if (PyIter_Check(obj)) {                                 /* iter */
		if (extend_iter(self, obj) == -1)
			return NULL;
		Py_RETURN_NONE;
	}
                                  /* finally, try to convert to iterable */
	PyObject *iter;
	if ((iter = PyObject_GetIter(obj)) != NULL) {
		if (extend_iter(self, iter) == -1)
			return NULL;
		Py_RETURN_NONE;
	}
	PyErr_SetString(PyExc_TypeError, "could not extend bitarray");
	return NULL;
}

PyDoc_STRVAR(extend_doc,
"extend(object)\n\
\n\
Append bits to the end of the bitarray.  The objects which can be passed\n\
to this method are the same which can given to a bitarray object upon\n\
upon initialization.");


static PyObject *
bitarray_buffer_info(bitarrayobject *self)
{
	PyObject* res;
	
	res = PyTuple_New(4);
	if (res == NULL)
		return NULL;
	
	PyTuple_SET_ITEM(res, 0, PyLong_FromVoidPtr(self->ob_item));
	PyTuple_SET_ITEM(res, 1, PyInt_FromLong((long) (self->ob_size)));
	PyTuple_SET_ITEM(res, 2,
			 PyString_FromString(self->endian ? "big" : "little"));
	PyTuple_SET_ITEM(res, 3, PyInt_FromLong((long)
	    ((idx_t) 8 * (idx_t) self->ob_size - self->nbits)));
	return res;
}

PyDoc_STRVAR(buffer_info_doc,
"buffer_info()\n\
\n\
Return a tuple (address, length, endianness, unused) giving the current\n\
memory address, the length in bytes used to hold the bitarray's contents,\n\
the bit endianness as a string, and the number of unused bits (0..7).");


static PyObject *
bitarray_endian(bitarrayobject *self)
{
	return PyString_FromString(self->endian ? "big" : "little");
}

PyDoc_STRVAR(endian_doc,
"endian()\n\
\n\
Return the bit endianness as a string (either 'little' or 'big').");


static PyObject *
bitarray_append(bitarrayobject *self, PyObject *v)
{
	if (append_item(self, v) < 0)
		return NULL;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(append_doc,
"append(x)\n\
\n\
Append new value bool(x) to the end of the bitarray.");


static PyObject *
bitarray_all(bitarrayobject *self)
{
	if (findfirst(self, 0) >= 0)
		Py_RETURN_FALSE;
	Py_RETURN_TRUE;
}

PyDoc_STRVAR(all_doc,
"all()\n\
\n\
Returns True when all bits are 1.");


static PyObject *
bitarray_any(bitarrayobject *self)
{
	if (findfirst(self, 1) >= 0)
		Py_RETURN_TRUE;
	Py_RETURN_FALSE;
}

PyDoc_STRVAR(any_doc,
"any()\n\
\n\
Returns True when any bit is 1.");


static PyObject *
bitarray_reduce(bitarrayobject *self)
{
	PyObject *dict, *result;
	int unusedbits;
	
	dict = PyObject_GetAttrString((PyObject *)self, "__dict__");
	if (dict == NULL) {
		PyErr_Clear();
		dict = Py_None;
		Py_INCREF(dict);
	}
	unusedbits = 8 * (idx_t) (self->ob_size) - self->nbits;
	result = Py_BuildValue("O(s#is)O",
			       self->ob_type,
			       self->ob_item,
			       self->ob_size,
			       unusedbits,
			       self->endian ? "big" : "little",
			       dict);
	Py_DECREF(dict);
	return result;
}

PyDoc_STRVAR(reduce_doc, "Return state information for pickling.");


static PyObject *
bitarray_reverse(bitarrayobject *self)
{
        PyObject *tt;    /* for tmp bitarray to store lower half of self */
	idx_t i, m, t_bits;
	
	if (self->nbits < 2)
		Py_RETURN_NONE;

	m = self->nbits - 1;            /* highest bit in self */
	t_bits = (self->nbits / 2);     /* # of bits in t */
	tt = newbitarrayobject(self->ob_type,
			       8 * bytes_bits(t_bits),
			       self->endian);
#define t  ((bitarrayobject *) tt)
	/* Copy first half of array into tmp array */
	memcpy(t->ob_item, self->ob_item, t->ob_size);
	
	/* Reverse the upper half onto the lower half. */
	for (i = 0; i < t_bits; i++)
		setbit(self, i, getbit(self, m - i));
	
	/* Revert the stored away lower half onto the upper half. */
	for (i = 0; i < t_bits; i++)
		setbit(self, m - i, getbit(t, i));
	dealloc(t);
#undef t
	Py_RETURN_NONE;
}

PyDoc_STRVAR(reverse_doc,
"reverse()\n\
\n\
Reverse the order of bits, IN PLACE.");


static PyObject *
bitarray_sort(bitarrayobject *self)
{
        idx_t i, n, n0;

	n = self->nbits;
	n0 = n - count(self);
	for (i = 0; i < n0; i++)
	        setbit(self, i, 0);
	for (i = n0; i < n; i++)
                setbit(self, i, 1);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(sort_doc,
"sort()\n\
\n\
sort, IN PLACE.");


static PyObject *
bitarray_fromfile(bitarrayobject *self, PyObject *args)
{
	PyObject *f;
	Py_ssize_t nbytes;
	FILE *fp;
	
        if (!PyArg_ParseTuple(args, "On", &f, &nbytes))
		return NULL;
	
	fp = PyFile_AsFile(f);
	if (fp == NULL) {
		PyErr_SetString(PyExc_TypeError,
				"first argument must be an open file");
		return NULL;
	}
	if (self->nbits % 8) {
		char buff[256];
		sprintf(buff, "current size is %lld "
			      "which is not multiple of 8", self->nbits);
		PyErr_SetString(PyExc_ValueError, strdup(buff));
		return NULL;
	}
	if (nbytes < 0) { /* find number of bytes till EOF */
		long cur;
		if ((cur = ftell (fp)) == -1L)
			goto eoferr;
		
		if (fseek (fp, 0L, SEEK_END) || (nbytes = ftell (fp)) == -1L)
			goto eoferr;
		
		nbytes -= cur;
		if (fseek (fp, cur, SEEK_SET)) {
		eoferr:
			PyErr_SetString(PyExc_EOFError,
					"could not find EOF");
			return NULL;
		}
	}
	if (nbytes > 0) {
		char *item = self->ob_item;
		size_t nread, newsize = self->ob_size + nbytes;
		
		if (newsize <= 0) {
			PyErr_NoMemory();
			return NULL;
		}
		PyMem_RESIZE(item, char, newsize);
		if (item == NULL) {
			PyErr_NoMemory();
			return NULL;
		}		
		self->ob_item = item;
		self->ob_size = newsize;
		self->nbits = 8 * (idx_t) newsize;
		self->allocated = self->ob_size;
		nread = fread(item + (self->ob_size - nbytes), 1, nbytes, fp);
		if (nread < (size_t) nbytes) {
			newsize -= nbytes - nread;
			self->ob_size = newsize;
			self->nbits = 8 * (idx_t) newsize;
			PyMem_RESIZE(item, char, newsize);
			self->ob_item = item;
			self->allocated = self->ob_size;
			PyErr_SetString(PyExc_EOFError,
					"not enough items in file");
			return NULL;
		}
	}
	Py_RETURN_NONE;
}


static PyObject *
bitarray_tofile(bitarrayobject *self, PyObject *f)
{
	FILE *fp;
	
	fp = PyFile_AsFile(f);
	if (fp == NULL) {
		PyErr_SetString(PyExc_TypeError, "open file expected");
		return NULL;
	}
	if (self->ob_size > 0) {
		setlastzero(self);
		if (fwrite(self->ob_item, 1, self->ob_size, fp) !=
		    (size_t) self->ob_size)
			{
				PyErr_SetFromErrno(PyExc_IOError);
				clearerr(fp);
				return NULL;
			}
	}
	Py_RETURN_NONE;
}

PyDoc_STRVAR(tofile_doc,
"tofile(f)\n\
\n\
Write all bits (as machine values) to the file object f.\n\
When the length of the bitarray is not a mutiple of 8,\n\
the few remaining bits are filled with zeros.");


static PyObject *
bitarray_tolist(bitarrayobject *self)
{
        PyObject *list, *v;
	Py_ssize_t nbits;
	idx_t i;
	
	nbits = self->nbits;
	if (nbits != self->nbits) {
		PyErr_SetString(PyExc_ValueError,
				"bitarray is too large to convert to list");
		return NULL;
	}
	list = PyList_New(nbits);
	if (list == NULL)
		return NULL;
	
	for (i = 0; i < nbits; i++) {
		v = PyBool_FromLong(getbit(self, i));
		if (v == NULL) {
			Py_DECREF(list);
			return NULL;
		}
		PyList_SetItem(list, i, v);
	}
	return list;
}

PyDoc_STRVAR(tolist_doc,
"tolist()\n\
\n\
Return an ordinary list with the items in the bitarray.");


static PyObject *
bitarray_fromstring(bitarrayobject *self, PyObject *string)
{
        idx_t i, t1, t2, t3, n;
	int p;
	
	if (!PyString_Check(string)) {
		PyErr_SetString(PyExc_TypeError, "string expected");
		return NULL;
	}
	t1 = self->nbits;
	t2 = self->nbits = 8 * (idx_t) self->ob_size;
	p = t2 - t1;      /* number of bits by which size has increased */
	assert (p >= 0 && p < 8);
	if (extend_string(self, string) == -1)
		return NULL;
	
	t3 = self->nbits;
	n = t3 - t2;       /* number of bits read from string */
	assert (n >= 0 && n % 8 == 0);
	for (i = 0; i < n; i++)
		setbit(self, t1 + i, getbit(self, t2 + i));
	self->nbits -= p;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(fromstring_doc,
"fromstring(string)\n\
\n\
Append from a string, interpreting the string as machine values.");


static PyObject *
bitarray_tostring(bitarrayobject *self)
{
	setlastzero(self);
	return PyString_FromStringAndSize(self->ob_item, self->ob_size);
}

PyDoc_STRVAR(tostring_doc,
"tostring()\n\
\n\
Return the string representing (machine values) of the bitarray.\n\
When the length of the bitarray is not a mutiple of 8, the few remaining\n\
bits are filled with zeros.");


static PyObject *
bitarray_to01(bitarrayobject *self)
{
	Py_ssize_t i, nbits;
	PyObject *a;
	char *s;

	nbits = self->nbits;
	if (nbits != self->nbits) {
		PyErr_SetString(PyExc_ValueError,
				"bitarray is too large to convert to string "
				"of '0's and '1's");
                return NULL;
	}
	if ((s = malloc(nbits)) == NULL) {
		PyErr_NoMemory();
		return NULL;
	}
	for (i = 0; i < nbits; i++) {
		*(s + i) = '0' + getbit(self, i);
	}
	a = PyString_FromStringAndSize(s, nbits);
	free(s);
	return a;
}

PyDoc_STRVAR(to01_doc,
"to01())\n\
\n\
Return a string containing '0's and '1's, representing the bits in the\n\
bitarray object.");


static PyObject *
bitarray_setall(bitarrayobject *self, PyObject *v)
{
	long vi;
	
	vi = PyObject_IsTrue(v);
	if (vi < 0)
		return NULL;
	
	memset(self->ob_item, (char) (0xff * vi), self->ob_size);
        Py_RETURN_NONE;
}

PyDoc_STRVAR(setall_doc,
"setall(x)\n\
\n\
Set all bits in the bitarray to x.");


static PyObject *
bitarray_fill(bitarrayobject *self)
{
        int p;
	
	p = setlastzero(self);
	self->nbits = 8 * (idx_t) self->ob_size;
        return PyInt_FromLong((long) p);
}

PyDoc_STRVAR(fill_doc,
"fill()\n\
\n\
When the length of the bitarray is not a mutiple of 8, increase the length\n\
slightly such that the new length is a mutiple of 8, and set the few new\n\
bits to zero.  Returns the number of bits added (0..7).");


static PyObject *
bitarray_invert(bitarrayobject *self)
{
	size_t i;
	
	for (i = 0; i < self->ob_size; i++) {
		self->ob_item[i] = ~self->ob_item[i];
	}
        Py_RETURN_NONE;
}

PyDoc_STRVAR(invert_doc,
"invert(x)\n\
\n\
Invert all bits in the bitarray IN PLACE,\n\
i.e. convert each 1-bit into a 0-bit and vice versa.");


static PyObject *
bitarray_bytereverse(bitarrayobject *self)
{
	static char trans[256];
	static int setup = 0;
	if (!setup) {
		int j, k;
		for (k = 0; k < 256; k++) {
			trans[k] = '\0';
			for(j = 0; j < 8; j++)
				if (1 << (7 - j) & k)
					trans[k] |= 1 << j;
		}
		setup = 1;
	}
	size_t i;
	int c;
	
	setlastzero(self);
	for (i = 0; i < self->ob_size; i++) {
		c = self->ob_item[i];
		if (c < 0) c += 256;
		self->ob_item[i] = trans[c];
	}
        Py_RETURN_NONE;
}

PyDoc_STRVAR(bytereverse_doc,
"bytereverse()\n\
\n\
For all bytes representing the bitarray, reverse the bit order.");


static PyObject *
bitarray_gscr1(bitarrayobject *self, PyObject *v)
{
	idx_t i;

	i = PyLong_AsLongLong(v);

	if (i < 0)
		i += self->nbits;
	
	if (i < 0 || i >= self->nbits) {
		PyErr_SetString(PyExc_IndexError,
				"bitarray index out of range");
		return NULL;
	}
	return PyBool_FromLong(getbit(self, i));
}


static PyObject *
bitarray_gscr3(bitarrayobject *self, PyObject *args)
{
	idx_t start, stop, step, slicelength, cur, i;
	PyObject *a;
	
	if (!PyArg_ParseTuple(args, "LLLL:gscr3",
			      &start, &stop, &step, &slicelength))
		return NULL;
	
	a = newbitarrayobject(self->ob_type, slicelength, self->endian);
	if (a == NULL)
		return NULL;
	
	for (i = 0, cur = start; i < slicelength; i++, cur += step) {
		setbit((bitarrayobject *) a, i, getbit(self, cur));
	}
	return a;
}

static PyObject *
bitarray_sscr1(bitarrayobject *self, PyObject *args)
{
	idx_t i;
	PyObject *v;
	
	if (!PyArg_ParseTuple(args, "LO:sscr1", &i, &v))
		return NULL;
	
	if (i < 0)
		i += self->nbits;
	
	if (i < 0 || i >= self->nbits) {
		PyErr_SetString(PyExc_IndexError,
				"bitarray assignment index out of range");
		return NULL;
	}
	set_item(self, i, v);
	Py_RETURN_NONE;
}

static PyObject *
bitarray_sscr3(bitarrayobject *self, PyObject *args)
{
	idx_t start, stop, step, slicelength, cur, i;
	PyObject *v;

	if (!PyArg_ParseTuple(args, "LLLLO:sscr3",
			      &start, &stop, &step, &slicelength, &v))
		return NULL;
	
	if (!bitarray_Check(v)) {
		PyErr_SetString(PyExc_IndexError,
				"can only assign slice to bitarray");
		return NULL;
	}
	bitarrayobject *a;
	a = (bitarrayobject *) v;
	
	if (a->nbits == slicelength) {
		for (i = 0, cur = start; i < slicelength; i++, cur += step)
			setbit(self, cur, getbit(a, i));
		Py_RETURN_NONE;
	}
	if (step != 1) {
		char buff[256];
		sprintf(buff,
			"attempt to assign sequence of size %lld "
			"to extended slice of size %lld",
			a->nbits, slicelength);
		PyErr_SetString(PyExc_ValueError, strdup(buff));
		return NULL;
	}
	idx_t bitshift = a->nbits - slicelength;
	idx_t oldbitsize = self->nbits;
	idx_t newbitsize = oldbitsize + bitshift;
	size_t newsize = bytes_bits(newbitsize);
	char *item = self->ob_item;
	
	if (newsize < 0) {
		PyErr_NoMemory();
		return NULL;
	}
	if (bitshift > 0) {
		PyMem_RESIZE(item, char, newsize);
		if (item == NULL) {
			PyErr_NoMemory();
			return NULL;
		}
		self->ob_item = item;
		
		for (i = oldbitsize-1; i >= start + slicelength; i--)
			setbit(self, i + bitshift, getbit(self, i));
	}
	else { /* bitshift < 0 */
		for (i = start + slicelength; i < oldbitsize; i++)
			setbit(self, i + bitshift, getbit(self, i));
		
		PyMem_RESIZE(item, char, newsize);
		if (item == NULL) {
			PyErr_NoMemory();
			return NULL;
		}
		self->ob_item = item;
	}
	for (i = 0; i < a->nbits; i++)
		setbit(self, i + start, getbit(a, i));
	
	self->ob_size = newsize;
	self->nbits = newbitsize;
	self->allocated = self->ob_size;
	
	Py_RETURN_NONE;
}


static PyObject *
bitarray_dscr3(bitarrayobject *self, PyObject *args)
{
	idx_t start, stop, step, slicelength, cur, i;
	
	if (!PyArg_ParseTuple(args, "LLLL:dscr3",
			      &start, &stop, &step, &slicelength))
		return NULL;
	
	if (slicelength == 0)
		Py_RETURN_NONE;
	
	idx_t oldbitsize = self->nbits;
	idx_t newbitsize = oldbitsize - slicelength;
	size_t newsize = bytes_bits(newbitsize);
	char *item = self->ob_item;
	
	if (newsize < 0) {
		PyErr_NoMemory();
		return NULL;
	}
	
	if (step < 0) {
		stop = start + 1;
		start = stop + step * (slicelength - 1) - 1;
		step = -step;
	}
	
	for (cur = i = start; i < oldbitsize; i++)
		if ((i - start) % step != 0 || i >= stop)
			setbit(self, cur++, getbit(self, i));
	
	PyMem_RESIZE(item, char, newsize);
	if (item == NULL) {
		PyErr_NoMemory();
		return NULL;
	}
	self->ob_item = item;
	self->ob_size = newsize;
	self->nbits = newbitsize;
	self->allocated = self->ob_size;
	
	Py_RETURN_NONE;
}


static PyMethodDef
bitarray_methods[] = {
	{"all", 	(PyCFunction)bitarray_all,	METH_NOARGS,
	 all_doc},
	{"any", 	(PyCFunction)bitarray_any,	METH_NOARGS,
	 any_doc},
	{"append",	(PyCFunction)bitarray_append,	METH_O,
	 append_doc},
	{"buffer_info", (PyCFunction)bitarray_buffer_info, METH_NOARGS,
	 buffer_info_doc},
	{"bytereverse", (PyCFunction)bitarray_bytereverse, METH_NOARGS,
	 bytereverse_doc},
	{"__copy__",	(PyCFunction)bitarray_copy,	METH_NOARGS,
	 copy_doc},
	{"__deepcopy__",(PyCFunction)bitarray_copy,	METH_O,
	 copy_doc},
	{"count",	(PyCFunction)bitarray_count,	METH_O,
	 count_doc},
	{"__contains__",(PyCFunction)bitarray_contains,	METH_O,
	 contains_doc},
	{"endian",      (PyCFunction)bitarray_endian,	METH_NOARGS,
	 endian_doc},
	{"extend",      (PyCFunction)bitarray_extend,	METH_O,
	 extend_doc},
	{"fill",	(PyCFunction)bitarray_fill,	METH_NOARGS,
	 fill_doc},
	{"fromfile",	(PyCFunction)bitarray_fromfile,	METH_VARARGS,
	 0},
	{"fromstring",	(PyCFunction)bitarray_fromstring, METH_O,
 	 fromstring_doc},
	{"index",	(PyCFunction)bitarray_index,	METH_O,
	 index_doc},
	{"invert",	(PyCFunction)bitarray_invert,	METH_NOARGS,
	 invert_doc},
	{"length",	(PyCFunction)bitarray_length,	METH_NOARGS,
	 length_doc},
	{"__len__",	(PyCFunction)bitarray_length,	METH_NOARGS,
	 length_doc},
	{"__reduce__",	(PyCFunction)bitarray_reduce,	METH_NOARGS,
	 reduce_doc},
	{"reverse",	(PyCFunction)bitarray_reverse,	METH_NOARGS,
	 reverse_doc},
	{"setall",	(PyCFunction)bitarray_setall,	METH_O,
	 setall_doc},
	{"sort",	(PyCFunction)bitarray_sort,	METH_NOARGS,
	 sort_doc},
	{"tofile",	(PyCFunction)bitarray_tofile,	METH_O,
	 tofile_doc},
	{"tolist",	(PyCFunction)bitarray_tolist,	METH_NOARGS,
	 tolist_doc},
	{"tostring",	(PyCFunction)bitarray_tostring,	METH_NOARGS,
	 tostring_doc},
	{"to01",        (PyCFunction)bitarray_to01,     METH_NOARGS,
         to01_doc},
	/*
           the remaining methods are for internal use only, i.e. they
	   are not meant to be called directly, only from within the
	   methods of the class bitarray(_bitarray)
	*/
	{"_gscr1",	(PyCFunction)bitarray_gscr1,	METH_O,       0},
	{"_gscr3",	(PyCFunction)bitarray_gscr3,	METH_VARARGS, 0},
	{"_sscr1",	(PyCFunction)bitarray_sscr1,	METH_VARARGS, 0},
	{"_sscr3",	(PyCFunction)bitarray_sscr3,	METH_VARARGS, 0},
	{"_dscr3",	(PyCFunction)bitarray_dscr3,	METH_VARARGS, 0},
	{NULL,		NULL}		/* sentinel */
};


static PyObject *
bitarray_repr(bitarrayobject *self)
{
	PyObject *s, *t, *v = NULL;
	
	if (self->nbits == 0)
		return PyString_FromString("bitarray()");
	
	v = bitarray_to01(self);
	
	t = PyObject_Repr(v);
	Py_XDECREF(v);
	
	s = PyString_FromString("bitarray(");
	PyString_ConcatAndDel(&s, t);
	/*
	if (self->endian != DEFAULT_ENDIAN) {
       	        PyString_ConcatAndDel(&s, PyString_FromString(", endian='"));
		PyString_ConcatAndDel(&s,
		    PyString_FromString(self->endian ? "big" : "little"));
		PyString_ConcatAndDel(&s, PyString_FromString("'"));
	}
	*/
        PyString_ConcatAndDel(&s, PyString_FromString(")"));
        return s;
}


static PyObject *
bitarray_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyObject *initial;
	int unusedbits = -1;
	char *endianStr = "not_provided";
	int endian = DEFAULT_ENDIAN;
	
	static char* kwlist[] = {"initial", "unusedbits", "endian", NULL};
	initial = NULL;
        if (!PyArg_ParseTupleAndKeywords(args, kwds,
                                         "|Ois:bitarray", kwlist,
                                         &initial, &unusedbits, &endianStr))
	        return NULL;
	
	if (strcmp(endianStr, "little") == 0) {
	        endian = 0;
	}
	else if (strcmp(endianStr, "big") == 0) {
	        endian = 1;
	}
	else if (strcmp(endianStr, "not_provided") == 0) {
                /* keep the default value */
	}
	else {
	        PyErr_SetString(PyExc_ValueError,
				"endian must be 'little' or 'big'");
		return NULL;
	}
	/* no arg or None */
	if (initial == NULL || initial == Py_None)
		return newbitarrayobject(type, 0, endian);
	
        /* int, long */
        if (PyInt_Check(initial) || PyLong_Check(initial)) {
                idx_t len;
		
	        len = PyInt_Check(initial)  ?
		                PyInt_AS_LONG(initial)  :
		                PyLong_AsLongLong(initial);
		if (len < 0) {
			PyErr_SetString(PyExc_ValueError,
					"cannot create "
					"bitarray with negative length");
			return NULL;
		}
		return newbitarrayobject(type, len, endian);
	}
	PyObject *a;  /* to be returned */
	
	/* from bitarray itself */
	if (bitarray_Check(initial)) {
		bitarrayobject *np;
		
		np = (bitarrayobject *) initial;
		a = newbitarrayobject(type, np->nbits,
				      (strcmp(endianStr, "not_provided") == 0
				       ?  np->endian : endian));
		memcpy(((bitarrayobject *) a)->ob_item,
		       np->ob_item,
		       np->ob_size);
                return a;
	}
	/* the following cases extend this object */
	a = newbitarrayobject(type, 0, endian);

	/* str */
	if (PyString_Check(initial) && unusedbits >= 0) {
		if (unusedbits >= 8) {
			PyErr_SetString(PyExc_ValueError,
					"unusedbits not 0..7");
			return NULL;
		}
		if (extend_string((bitarrayobject *) a, initial) == -1) {
			return NULL;
		}
#define nbits  (((bitarrayobject *) a)->nbits)
		assert (nbits % 8 == 0);
		if (nbits == 0 && unusedbits > 0) {
			PyErr_SetString(PyExc_ValueError, 
			     "unusedbits > 0 given but string is empty");
			return NULL;
		}
		nbits -= unusedbits;
#undef nbits
		return a;
	}

	/* str01 */
	if (PyString_Check(initial) && unusedbits < 0) {
		if (extend_string01((bitarrayobject *) a, initial) == -1) {
			return NULL;
		}
		return a;
	}
	
	/* leave the remaining dispatch to the extend method */
	if (bitarray_extend((bitarrayobject *) a, initial) == NULL)
	        return NULL;

	return a;
} /* END bitarray_new */


static PyObject *bitarray_iter(bitarrayobject *self);


static PyTypeObject Bitarraytype = {
	PyObject_HEAD_INIT(NULL)
	0,
	"_bitarray._bitarray",
	sizeof(bitarrayobject),
	0,
	(destructor) dealloc,	        	/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	(reprfunc) bitarray_repr,        	/* tp_repr */
	0,					/* tp_as_number*/
	0,                      		/* tp_as_sequence*/
	0,                    			/* tp_as_mapping*/
	0, 					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	PyObject_GenericGetAttr,		/* tp_getattro */
	0,					/* tp_setattro */
	0,                   			/* tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_WEAKREFS,
	                                        /* tp_flags */
	0,               			/* tp_doc */
 	0,					/* tp_traverse */
	0,                                	/* tp_clear */
	richcompare,        			/* tp_richcompare */
	offsetof(bitarrayobject, weakreflist),	/* tp_weaklistoffset */
	(getiterfunc) bitarray_iter,		/* tp_iter */
	0,					/* tp_iternext */
	bitarray_methods,			/* tp_methods */
	0,					/* tp_members */
	0,	             			/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	PyType_GenericAlloc,			/* tp_alloc */
	bitarray_new,				/* tp_new */
	PyObject_Del,				/* tp_free */
};


/*********************** Bitarray Iterator **************************/

typedef struct {
	PyObject_HEAD
	idx_t   	    index;
	bitarrayobject*     ao;
} bitarrayiterobject;

static PyTypeObject PyBitarrayIter_Type;

#define PyBitarrayIter_Check(op)  PyObject_TypeCheck(op, &PyBitarrayIter_Type)

static PyObject *
bitarray_iter(bitarrayobject *self)
{
	bitarrayiterobject *it;
	
	if (!bitarray_Check(self)) {
		PyErr_BadInternalCall();
		return NULL;
	}
	it = PyObject_GC_New(bitarrayiterobject, &PyBitarrayIter_Type);
	if (it == NULL)
		return NULL;
	
	Py_INCREF(self);
	it->ao = self;
	it->index = 0;
	PyObject_GC_Track(it);
	return (PyObject *) it;
}

static PyObject *
bitarrayiter_next(bitarrayiterobject *it)
{
	assert (PyBitarrayIter_Check(it));
	if (it->index < it->ao->nbits) {
		return PyBool_FromLong(getbit(it->ao, it->index++));
	}
	return NULL;
}

static void
bitarrayiter_dealloc(bitarrayiterobject *it)
{
	PyObject_GC_UnTrack(it);
	Py_XDECREF(it->ao);
	PyObject_GC_Del(it);
}

static int
bitarrayiter_traverse(bitarrayiterobject *it, visitproc visit, void *arg)
{
	Py_VISIT(it->ao);
	return 0;
}

static PyTypeObject PyBitarrayIter_Type = {
	PyObject_HEAD_INIT(NULL)
	0,                                      /* ob_size */
	"bitarrayiterator",                     /* tp_name */
	sizeof(bitarrayiterobject),             /* tp_basicsize */
	0,                                      /* tp_itemsize */
	/* methods */
	(destructor) bitarrayiter_dealloc,	/* tp_dealloc */
	0,                                      /* tp_print */
	0,                                      /* tp_getattr */
	0,                                      /* tp_setattr */
	0,                                      /* tp_compare */
	0,                                      /* tp_repr */
	0,                                      /* tp_as_number */
	0,                                      /* tp_as_sequence */
	0,                                      /* tp_as_mapping */
	0,                                      /* tp_hash */
	0,                                      /* tp_call */
	0,                                      /* tp_str */
	PyObject_GenericGetAttr,                /* tp_getattro */
	0,                                      /* tp_setattro */
	0,                                      /* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,/* tp_flags */
	0,                                      /* tp_doc */
	(traverseproc)bitarrayiter_traverse,	/* tp_traverse */
	0,					/* tp_clear */
	0,                                      /* tp_richcompare */
	0,                                      /* tp_weaklistoffset */
	PyObject_SelfIter,			/* tp_iter */
	(iternextfunc) bitarrayiter_next,	/* tp_iternext */
	0,					/* tp_methods */
};

/*************************** Functions **********************/

static PyObject *
bits2bytes(PyObject *self, PyObject *v)
{
	idx_t n;
	
	if (!PyInt_Check(v) && !PyLong_Check(v)) {
		PyErr_SetString(PyExc_TypeError, "integer argument expected");
		return NULL;
	}
	n = PyInt_Check(v)  ?  PyInt_AS_LONG(v)  :  PyLong_AsLongLong(v);
	if (n < 0) {
		PyErr_SetString(PyExc_ValueError,
				"number of bits negative");
		return NULL;
	}
	return PyLong_FromLongLong(bytes_bits(n));
}

PyDoc_STRVAR(bits2bytes_doc,
"bits2bytes(n)\n\
\n\
Return the number of bytes necessary to store n bits.");


static PyMethodDef module_functions[] = {
        {"bits2bytes",  bits2bytes,  METH_O,  bits2bytes_doc},
	{NULL, NULL, 0, NULL}        /* Sentinel */
};

/*********************** Install Module **************************/

PyMODINIT_FUNC
init_bitarray(void)
{
	PyObject *m;
	
	Bitarraytype.ob_type = &PyType_Type;
	PyBitarrayIter_Type.ob_type = &PyType_Type;
	m = Py_InitModule3("_bitarray", module_functions, 0);
	if (m == NULL) {
		return;
	}
        Py_INCREF((PyObject *) &Bitarraytype);
	PyModule_AddObject(m, "_bitarray", (PyObject *) &Bitarraytype);
}
