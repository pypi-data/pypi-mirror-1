/* Bitarray object implementation */

/* An bitarray is a uniform list -- all items are of type bool. */

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

typedef struct {
	PyObject_VAR_HEAD
	char *ob_item;
	Py_ssize_t allocated;
	idx_t nbits;
	PyObject *weakreflist;   /* List of weak references */
} bitarrayobject;

static PyTypeObject Bitarraytype;

#define bitarray_Check(op) PyObject_TypeCheck(op, &Bitarraytype)

static int
bitarray_resize(bitarrayobject *self, Py_ssize_t newsize)
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

/* ------------ Low level access to bits in bitarrayobject ------------- */

/* The test suite should work regardless of the value of ENDIANNESS.
   The visible impact of this setting are the conversions to and from
   machine values: fromfile, tofile, fromstring, tostring
 */
#define ENDIANNESS 1

static int
getbit(bitarrayobject *self, idx_t i)
{
	char c;

	c = self->ob_item[i/8];
#if ENDIANNESS
	return (c >> i%8) & 1;
#else
	return (c >> (7 - i%8)) & 1;
#endif
}

static void
setbit(bitarrayobject *self, idx_t i, int bit)
{
	char *cp, x;

	cp = self->ob_item + i/8;
#if ENDIANNESS
	x = 1 << i%8;
#else
	x = 1 << (7 - i%8);
#endif
	if (bit)
		*cp |= x;
	else
		*cp &= ~x;
}
#undef ENDIANNESS

static PyObject *
getitem(bitarrayobject *self, idx_t i)
{
	return PyBool_FromLong(getbit(self, i));
}

static int
setitem(bitarrayobject *self, idx_t i, PyObject *v)
{
	long vi;
	
	vi = PyObject_IsTrue(v);
	if (vi < 0 || i < 0 || i >= self->nbits)
		return -1;
	
	setbit(self, i, vi);
	return 0;
}

/****************************************************************************
Implementations of bitarray object methods.
****************************************************************************/

/* Return number of bytes necessary to store nbits */
static size_t
bytes_bits(idx_t nbits)
{
	return (nbits == 0) ? 0 : ((nbits - 1) / 8 + 1);
}

static PyObject *
newbitarrayobject(PyTypeObject *type, idx_t nbits)
{
	bitarrayobject *op;
	Py_ssize_t nbytes;
	
	if (nbits < 0) {
		PyErr_BadInternalCall();
		return NULL;
	}
	nbytes = bytes_bits(nbits);
	
	/* Check for overflow */
	if (nbytes != ((nbits == 0) ? 0 : ((nbits - 1) / 8 + 1)))
		return PyErr_NoMemory();
	
	op = (bitarrayobject *) type->tp_alloc(type, 0);
	if (op == NULL)
		return NULL;
	
	op->ob_size = nbytes;
	op->nbits = nbits;
	
	if (nbits == 0)
		op->ob_item = NULL;
	else {
		op->ob_item = PyMem_NEW(char, nbytes);
		if (op->ob_item == NULL) {
			PyObject_Del(op);
			return PyErr_NoMemory();
		}
	}
	op->allocated = nbytes;
	op->weakreflist = NULL;
	return (PyObject *) op;
}

static int
appenditem(bitarrayobject *self, PyObject *v)
{
	if (self->nbits + 1 > 8 * (idx_t) self->ob_size &&
	    bitarray_resize(self, self->ob_size + 1) == -1)
		return -1;
	
	return setitem(self, self->nbits++, v);
}

static void
setlastzero(bitarrayobject *self)
{
	idx_t i;
	
	for (i = self->nbits; i < 8 * (idx_t) self->ob_size; i++)
		setbit(self, i, 0);
}

static void
bitarray_dealloc(bitarrayobject *op)
{
	if (op->weakreflist != NULL)
		PyObject_ClearWeakRefs((PyObject *) op);
	
	if (op->ob_item != NULL)
		PyMem_DEL(op->ob_item);
	
	op->ob_type->tp_free((PyObject *) op);
}

/* Methods */

static PyObject *
bitarray_richcompare(PyObject *v, PyObject *w, int op)
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
		else
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
		else
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
	else
		Py_RETURN_FALSE;
}

static PyObject *
bitarray_length(bitarrayobject *a)
{
	return PyLong_FromLongLong(a->nbits);
}

PyDoc_STRVAR(length_doc,
"length()\n\
\n\
Return the length (number of bits) of the bitarray.");


static PyObject *
bitarray_copy(bitarrayobject *a, PyObject *unused)
{
	PyObject *b;
	
	b = newbitarrayobject(a->ob_type, a->nbits);
	memcpy(((bitarrayobject *) b)->ob_item, a->ob_item, a->ob_size);
	return b;
}

PyDoc_STRVAR(copy_doc,
"copy(bitarray)\n\
\n\
Return a copy of the bitarray.");


static int
bitarray_iter_extend(bitarrayobject *self, PyObject *bb)
{
	PyObject *it, *v;
	
	it = PyObject_GetIter(bb);
	if (it == NULL)
		return -1;
	
	while ((v = PyIter_Next(it)) != NULL) {
		if (appenditem(self, v) < 0) {
			Py_DECREF(v);
			Py_DECREF(it);
			return -1;
		}
		Py_DECREF(v);
	}
	Py_DECREF(it);
	if (PyErr_Occurred())
		return -1;
	return 0;
}


static PyObject *
bitarray_count(bitarrayobject *self, PyObject *v)
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
	idx_t count = 0;
	size_t i;
	long vi;
	int c;
	
	vi = PyObject_IsTrue(v);
	if (vi < 0)
		return NULL;
	
	setlastzero(self);
	for (i = 0; i < self->ob_size; i++) {
		c = self->ob_item[i];
		if (c < 0) c += 256;
		count += bytecount[c];
	}
	if (vi == 0)
		count = self->nbits - count;
	
	return PyLong_FromLongLong(count);
}

PyDoc_STRVAR(count_doc,
"count(x)\n\
\n\
Return number of occurences of x in the bitarray.");


/* Return index of first occurence of x in the bitarrayobject.
   Return -2 when x is not in found, -1 on error.
*/
static idx_t
bitarray_findfirst(bitarrayobject *self, int bit)
{
	size_t n;
	idx_t i;
	char c;

	if (bit < 0 || bit > 1)
		return -1;

	/* skip ahead by checking bytes */
	c = 0xff * (1-bit);
	for (n = 0; n < self->ob_size; n++)
		if (c ^ self->ob_item[n])
			break;
	if (n == self->ob_size) n--;
	if (n < 0) n = 0;
	
	/* fine graded search within byte */
	for (i = 8 * (idx_t) n; i < self->nbits; i++)
		if (getbit(self, i) == bit)
			return i;
	return -2;
}


static PyObject *
bitarray_index(bitarrayobject *self, PyObject *v)
{
	idx_t i;
	long vi;
	
	vi = PyObject_IsTrue(v);
	if (vi < 0 ||
	    (i = bitarray_findfirst(self, vi)) == -1)
		return NULL;
	
	if (i >= 0)
		return PyLong_FromLongLong(i);
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
	if (vi < 0 ||
	    (i = bitarray_findfirst(self, vi)) == -1)
		return NULL;
	
	if (i >= 0)
		Py_RETURN_TRUE;
	else
		Py_RETURN_FALSE;
}

PyDoc_STRVAR(contains_doc,
"__contains__(x)\n\
\n\
Return True if bitarray contains x, False otherwise.");


static PyObject *
bitarray_extend(bitarrayobject *self, PyObject *bb)
{
	idx_t i, newbitsize;
	size_t newsize;
	
	if (!bitarray_Check(bb)) {                           /* iterable */
		if (bitarray_iter_extend(self, bb) == -1)
			return NULL;
		Py_RETURN_NONE;
	}
#define b  ((bitarrayobject *) bb)
	newbitsize = self->nbits + b->nbits;                 /* bitarray */
	newsize = bytes_bits(newbitsize);
        PyMem_RESIZE(self->ob_item, char, newsize);
        if (self->ob_item == NULL) {
		PyObject_Del(self);
		return PyErr_NoMemory();
	}
	for (i = 0; i < b->nbits; i++)
		setbit(self, self->nbits + i, getbit(b, i));
#undef b	
	self->ob_size = newsize;
	self->allocated = newsize;
	self->nbits = newbitsize;
	
	Py_RETURN_NONE;
}

PyDoc_STRVAR(extend_doc,
"extend(bitarray or iterable)\n\
\n\
Append bits to the end of the bitarray.\n\
When you want to extend from a list, it's faster to use fromlist.");


static PyObject *
bitarray_buffer_info(bitarrayobject *self, PyObject *unused)
{
	PyObject* retval = NULL;
	retval = PyTuple_New(2);
	if (!retval)
		return NULL;
	
	PyTuple_SET_ITEM(retval, 0, PyLong_FromVoidPtr(self->ob_item));
	PyTuple_SET_ITEM(retval, 1, PyInt_FromLong((long) (self->ob_size)));
	
	return retval;
}

PyDoc_STRVAR(buffer_info_doc,
"buffer_info()\n\
\n\
Return a tuple (address, length) giving the current memory address and the\n\
length in bytes used to hold the bitarray's contents.  The length in bytes\n\
multiplied by 8 is slightly larger than the number of bits the bitarray\n\
holds.");


static PyObject *
bitarray_append(bitarrayobject *self, PyObject *v)
{
	if (appenditem(self, v) < 0)
		return NULL;
	
	Py_RETURN_NONE;
}

PyDoc_STRVAR(append_doc,
"append(x)\n\
\n\
Append new value bool(x) to the end of the bitarray.");


static PyObject *
bitarray_reduce(bitarrayobject *self)
{
	PyObject *dict, *result;
	int ignore;
	
	dict = PyObject_GetAttrString((PyObject *)self, "__dict__");
	if (dict == NULL) {
		PyErr_Clear();
		dict = Py_None;
		Py_INCREF(dict);
	}
	ignore = 8 * (idx_t) (self->ob_size) - self->nbits;
	result = Py_BuildValue("O(s#i)O",
			       self->ob_type,
			       self->ob_item,
			       self->ob_size,
			       ignore,
			       dict);
	Py_DECREF(dict);
	return result;
}

PyDoc_STRVAR(reduce_doc, "Return state information for pickling.");


static PyObject *
bitarray_fromfile(bitarrayobject *self, PyObject *args)
{
	PyObject *f;
	Py_ssize_t nbytes = -1;
	FILE *fp;
	
        if (!PyArg_ParseTuple(args, "O|n:fromfile", &f, &nbytes))
		return NULL;
	
	fp = PyFile_AsFile(f);
	if (fp == NULL) {
		PyErr_SetString(PyExc_TypeError, "arg1 must be open file");
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
		
		if (fseek (fp, 0L, SEEK_END) ||
		    (nbytes = ftell (fp)) == -1L)
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
		
		if (newsize <= 0)
			return PyErr_NoMemory();
		
		PyMem_RESIZE(item, char, newsize);
		if (item == NULL)
			return PyErr_NoMemory();
		
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

PyDoc_STRVAR(fromfile_doc,
"fromfile(f[, n])\n\
\n\
Read n bytes (not bits) from the file object f and append them to the end\n\
of the bitarray, i.e. 8*n bits will be added.\n\
When n is omitted, as many bytes are read until EOF is reached.");


static PyObject *
bitarray_tofile(bitarrayobject *self, PyObject *f)
{
	FILE *fp;
	
	fp = PyFile_AsFile(f);
	if (fp == NULL) {
		PyErr_SetString(PyExc_TypeError, "arg must be open file");
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
bitarray_fromlist(bitarrayobject *self, PyObject *list)
{
	Py_ssize_t newbits;
	
	if (!PyList_Check(list)) {
		PyErr_SetString(PyExc_TypeError, "arg must be list");
		return NULL;
	}
	newbits = PyList_Size(list);
	if (newbits > 0) {
		size_t i;
		char *item = self->ob_item;
		
		self->nbits += newbits;
		self->ob_size = bytes_bits(self->nbits);
		
		PyMem_RESIZE(item, char, self->ob_size);
		if (item == NULL)
			return PyErr_NoMemory();
		
		self->ob_item = item;
		self->allocated = self->ob_size;
		
		for (i = 0; i < newbits; i++)
			setitem(self,
				self->nbits - newbits + i,
				PyList_GetItem(list, i));
	}
	Py_RETURN_NONE;
}

PyDoc_STRVAR(fromlist_doc,
"fromlist(list)\n\
\n\
Append bits to bitarray from list.");


static PyObject *
bitarray_tolist(bitarrayobject *self, PyObject *unused)
{
	Py_ssize_t nbits = self->nbits;
	
	if (nbits != self->nbits) {
		PyErr_SetString(PyExc_ValueError,
				"bitarray is too large to convert to list");
		return NULL;
	}
	PyObject *list = PyList_New(nbits);
	if (list == NULL)
		return NULL;
	
	idx_t i;
	for (i = 0; i < nbits; i++) {
		PyObject *v = getitem(self, i);
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
bitarray_fromstring(bitarrayobject *self, PyObject *args)
{
	char *str;
	Py_ssize_t nbytes;

	if (self->nbits % 8) {
		char buff[256];
		sprintf(buff, "current size is %lld, which is not "
			      "a multiple of 8", self->nbits);
		PyErr_SetString(PyExc_ValueError, strdup(buff));
		return NULL;
	}
        if (!PyArg_ParseTuple(args, "s#:fromstring", &str, &nbytes))
		return NULL;
	
	if (nbytes > 0) {
		char *item = self->ob_item;
		PyMem_RESIZE(item, char, self->ob_size + nbytes);
		if (item == NULL)
			return PyErr_NoMemory();
		
		self->ob_item = item;
		self->ob_size += nbytes;
		self->nbits += 8 * (idx_t) nbytes;
		self->allocated = self->ob_size;
		memcpy(item + self->ob_size - nbytes, str, nbytes);
	}
	Py_RETURN_NONE;
}

PyDoc_STRVAR(fromstring_doc,
"fromstring(string)\n\
\n\
Appends bits from the string, interpreting it as an bitarray of machine\n\
values, as if it had been read from a file using the fromfile() method).");


static PyObject *
bitarray_tostring(bitarrayobject *self, PyObject *unused)
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
bitarray_from01(bitarrayobject *self, PyObject *args)
{
	char *str, c;
	Py_ssize_t newbits, i;

	if (!PyArg_ParseTuple(args, "s#:from01", &str, &newbits))
		return NULL;

	if (newbits > 0) {
		char *item = self->ob_item;
		int vi;
		
		self->ob_size = bytes_bits(self->nbits + newbits);
		self->allocated = self->ob_size;
		PyMem_RESIZE(item, char, self->ob_size);
		if (item == NULL)
			return PyErr_NoMemory();
		
		self->ob_item = item;

		for (i = 0; i<newbits; i++) {
			c = *(str + i);
			if (c == '0')
				vi = 0;
			else if (c == '1')
				vi = 1;
			else {
				char buff[256];
				sprintf(buff,
					"character must be '0' or '1', "
					"found '%c'", c);
				PyErr_SetString(PyExc_ValueError, buff);
				return NULL;
			}
			setbit(self, self->nbits + i, vi);
		}
		self->nbits += newbits;
	}
	Py_RETURN_NONE;
}

PyDoc_STRVAR(from01_doc,
"from01(string)\n\
\n\
Appends items from the string (containing '0's and '1's) to the bitarray.");


static PyObject *
bitarray_to01(bitarrayobject *self, PyObject *unused)
{
	Py_ssize_t i, nbits = self->nbits;
	PyObject *a;

	if (nbits != self->nbits) {
		PyErr_SetString(PyExc_ValueError,
				"bitarray is too large to convert to string "
				"of '0's and '1's");
                return NULL;
	}
	char *s;
	if ((s = malloc(nbits)) == NULL)
		return PyErr_NoMemory();

	for (i = 0; i < nbits; i++)
		*(s + i) = '0' + getbit(self, i);

	a = PyString_FromStringAndSize(s, nbits);
	free(s);
	return a;
}

PyDoc_STRVAR(to01_doc,
"to01(string)\n\
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
bitarray_fill(bitarrayobject *self, PyObject *unused)
{
	setlastzero(self);
	self->nbits = 8 * (idx_t) self->ob_size;
        Py_RETURN_NONE;
}

PyDoc_STRVAR(fill_doc,
"fill()\n\
\n\
When the length of the bitarray is not a mutiple of 8, increase the length\n\
slightly such that the new length is a mutiple of 8, and set the few new\n\
bits to zero.");


static PyObject *
bitarray_invert(bitarrayobject *self, PyObject *unused)
{
	size_t i;
	
	for (i = 0; i < self->ob_size; i++)
		self->ob_item[i] = ~self->ob_item[i];
        Py_RETURN_NONE;
}

PyDoc_STRVAR(invert_doc,
"invert(x)\n\
\n\
Invert all bits in the bitarray, i.e. convert each 1-bit into a 0-bit\n\
and vice versa.");


static PyObject *
bitarray_bytereverse(bitarrayobject *self, PyObject *unused)
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
Reverse the order of all bits for all machine values representing the\n\
bitarray.");


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
	return getitem(self, i);
}


static PyObject *
bitarray_gscr3(bitarrayobject *self, PyObject *args)
{
	idx_t start, stop, step, slicelength, cur, i;
	PyObject *a;
	
	if (!PyArg_ParseTuple(args, "LLLL:gscr3",
			      &start, &stop, &step, &slicelength))
		return NULL;
	
	a = newbitarrayobject(self->ob_type, slicelength);
	if (a == NULL)
		return NULL;
	
	for (i = 0, cur = start; i < slicelength; i++, cur += step)
		setbit((bitarrayobject *) a, i, getbit(self, cur));
	
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
	setitem(self, i, v);
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
	
	if (newsize < 0)
		return PyErr_NoMemory();
	
	if (bitshift > 0) {
		PyMem_RESIZE(item, char, newsize);
		if (item == NULL)
			return PyErr_NoMemory();
		self->ob_item = item;
		
		for (i = oldbitsize-1; i >= start + slicelength; i--)
			setbit(self, i + bitshift, getbit(self, i));
	}
	else { /* bitshift < 0 */
		for (i = start + slicelength; i < oldbitsize; i++)
			setbit(self, i + bitshift, getbit(self, i));
		
		PyMem_RESIZE(item, char, newsize);
		if (item == NULL)
			return PyErr_NoMemory();
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
	
	if (newsize < 0)
		return PyErr_NoMemory();
	
	if (step < 0) {
		stop = start + 1;
		start = stop + step * (slicelength - 1) - 1;
		step = -step;
	}
	
	for (cur = i = start; i < oldbitsize; i++)
		if ((i - start) % step != 0 || i >= stop)
			setbit(self, cur++, getbit(self, i));
	
	PyMem_RESIZE(item, char, newsize);
	if (item == NULL)
		return PyErr_NoMemory();
	
	self->ob_item = item;
	self->ob_size = newsize;
	self->nbits = newbitsize;
	self->allocated = self->ob_size;
	
	Py_RETURN_NONE;
}


PyMethodDef bitarray_methods[] = {
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
	{"extend",      (PyCFunction)bitarray_extend,	METH_O,
	 extend_doc},
	{"fill",	(PyCFunction)bitarray_fill,	METH_NOARGS,
	 fill_doc},
	{"fromfile",	(PyCFunction)bitarray_fromfile,	METH_VARARGS,
	 fromfile_doc},
	{"fromlist",	(PyCFunction)bitarray_fromlist,	METH_O,
	 fromlist_doc},
	{"fromstring",	(PyCFunction)bitarray_fromstring, METH_VARARGS,
	 fromstring_doc},
	{"from01",      (PyCFunction)bitarray_from01,   METH_VARARGS,
         from01_doc},
	{"index",	(PyCFunction)bitarray_index,	METH_O,
	 index_doc},
	{"invert",	(PyCFunction)bitarray_invert,	METH_NOARGS,
	 invert_doc},
	{"length",	(PyCFunction)bitarray_length,	METH_NOARGS,
	 length_doc},
	{"__reduce__",	(PyCFunction)bitarray_reduce,	METH_NOARGS,
	 reduce_doc},
	{"setall",	(PyCFunction)bitarray_setall,	METH_O,
	 setall_doc},
	{"tofile",	(PyCFunction)bitarray_tofile,	METH_O,
	 tofile_doc},
	{"tolist",	(PyCFunction)bitarray_tolist,	METH_NOARGS,
	 tolist_doc},
	{"tostring",	(PyCFunction)bitarray_tostring,	METH_NOARGS,
	 tostring_doc},
	{"to01",        (PyCFunction)bitarray_to01,     METH_NOARGS,
         to01_doc},
	
	/* the remaining methods are for internal use only, i.e. they
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
	
	v = bitarray_to01(self, NULL);
	
	t = PyObject_Repr(v);
	Py_XDECREF(v);
	
	s = PyString_FromString("bitarray(");
	PyString_ConcatAndDel(&s, t);
        PyString_ConcatAndDel(&s, PyString_FromString(")"));
        return s;
}


static PyObject *
bitarray_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyObject *initial = NULL, *a;
	idx_t i, len;
	int ignored = -1; /* number of bits at the end which are ignored */
	
	if (!_PyArg_NoKeywords("bitarray.bitarray()", kwds))
		return NULL;
	
	if (!PyArg_ParseTuple(args, "|Oi:bitarray", &initial, &ignored))
		return NULL;
	
	/* no arg or None */
	if (initial == NULL || initial == Py_None)
	        return newbitarrayobject(type, 0);
	
	if (!PyString_Check(initial) && ignored >= 0) {
		PyErr_SetString(PyExc_TypeError, "1 argument expected");
		return NULL;
	}
	
        /* int, long */
        if (PyInt_Check(initial) || PyLong_Check(initial)) {
	        len = (PyInt_Check(initial)) ?
			PyInt_AS_LONG(initial) :
			PyLong_AsLongLong(initial);
		if (len < 0) {
			PyErr_SetString(PyExc_ValueError, "cannot create "
					"bitarray of negative length");
			return NULL;
		}
		a = newbitarrayobject(type, len);
	        return a;
	}
	
	/* list, tuple */
	if (PyList_Check(initial) || PyTuple_Check(initial)) {
		len = PySequence_Size(initial);
		a = newbitarrayobject(type, len);
		if (a == NULL)
		        return NULL;
		for (i = 0; i < len; i++) {
                        PyObject *v = PySequence_GetItem(initial, i);
			if (v == NULL) {
				Py_DECREF(a);
				return NULL;
			}
			setitem((bitarrayobject *) a, i, v);
			Py_DECREF(v);
		}
		return a;
	}
	
	/* str */
	if (PyString_Check(initial)) {
	        a = newbitarrayobject(type, 0);
		PyObject *v, *t;

		t = PyTuple_Pack(1, initial);
                if (t == NULL) {
                        Py_DECREF(a);
                        return NULL;
                }
		if (ignored == -1)
			v = bitarray_from01((bitarrayobject *) a, t);
		else
			v = bitarray_fromstring((bitarrayobject *) a, t);
		
		Py_DECREF(t);
		if (v == NULL) {
		        Py_DECREF(a);
			return NULL;
		}
		Py_DECREF(v);
		if (ignored == -1)
			return a;
		
		if (ignored < 0 || ignored >= 8) {
			PyErr_SetString(PyExc_TypeError, "ignored not 0..7");
			return NULL;
		}
#define nbits  ((*(bitarrayobject *) a).nbits)
		assert(nbits % 8 == 0);
		if (nbits == 0 && ignored > 0) {
			PyErr_SetString(PyExc_TypeError, 
					"ignored > 0 given but empty string");
			return NULL;
		}
		nbits -= ignored;
#undef nbits
		return a;
	}
	
	/* iter */
	if (PyIter_Check(initial)) { 
                PyObject *it;
		it = PyObject_GetIter(initial);
		if (it == NULL)
			return NULL;
 		a = newbitarrayobject(type, 0);
		if (bitarray_iter_extend((bitarrayobject *)a, it) == -1) {
			Py_DECREF(it);
			Py_DECREF(a);
			return NULL;
		}
		Py_DECREF(it);
		return a;
	}
	
	/* from bitarray itself */
	if (bitarray_Check(initial)) {
		bitarrayobject *np;
		np = (bitarrayobject *) initial;
		
		a = newbitarrayobject(type, np->nbits);
		memcpy(((bitarrayobject *) a)->ob_item,
		       np->ob_item,
		       np->ob_size);
                return a;
	}
	
	PyErr_SetString(PyExc_TypeError,
			"wrong args for creating new bitarray object");
	return NULL;
} /* END bitarray_new */


static PyObject *bitarray_iter(bitarrayobject *self);

static PyTypeObject Bitarraytype = {
	PyObject_HEAD_INIT(NULL)
	0,
	"_bitarray._bitarray",
	sizeof(bitarrayobject),
	0,
	(destructor) bitarray_dealloc,		/* tp_dealloc */
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
	bitarray_richcompare,			/* tp_richcompare */
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

#define PyBitarrayIter_Check(op) PyObject_TypeCheck(op, &PyBitarrayIter_Type)

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
	assert(PyBitarrayIter_Check(it));
	if (it->index < it->ao->nbits)
		return getitem(it->ao, it->index++);
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


/*********************** Install Module **************************/

/* No functions in bitarray module. */
static PyMethodDef a_methods[] = {
	{NULL, NULL, 0, NULL}        /* Sentinel */
};


PyMODINIT_FUNC
init_bitarray(void)
{
	PyObject *m;
	
	Bitarraytype.ob_type = &PyType_Type;
	PyBitarrayIter_Type.ob_type = &PyType_Type;
	m = Py_InitModule3("_bitarray", a_methods, 0);
	if (m == NULL)
		return;
	
        Py_INCREF((PyObject *) &Bitarraytype);
	PyModule_AddObject(m, "_bitarray", (PyObject *) &Bitarraytype);
}
