/*
Bitarray object implementation
This file is part of the bitarray module.

    http://pypi.python.org/pypi/bitarray/

Author: Ilan Schnell
*/

#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"

#ifdef STDC_HEADERS
#include <stddef.h>
#else  /* !STDC_HEADERS */
#ifdef HAVE_SYS_TYPES_H
#include <sys/types.h>      /* For size_t */
#endif /* HAVE_SYS_TYPES_H */
#endif /* !STDC_HEADERS */


typedef int64_t idx_t;

/* throughout:  0 = little endian   1 = big endian */
#define DEFAULT_ENDIAN  1

typedef struct {
    PyObject_VAR_HEAD
    char *ob_item;
    Py_ssize_t allocated;
    idx_t nbits;
    int endian;
    PyObject *weakreflist;   /* List of weak references */
} bitarrayobject;

static PyTypeObject Bitarraytype;

#define bitarray_Check(obj)  PyObject_TypeCheck(obj, &Bitarraytype)

#define BITS(bytes)  (((idx_t) 8) * ((idx_t) (bytes)))

#define BYTES(bits)  (((bits) == 0) ? 0 : (((bits) - 1) / 8 + 1))

#define BITMASK(endian, i)  (((char) 1) << ((endian) ? 7-(i)%8 : (i)%8))

/* ------------ Low level access to bits in bitarrayobject ------------- */

static inline int
getbit(bitarrayobject *self, idx_t i)
{
    return (self->ob_item[i/8] & BITMASK(self->endian, i)) ? 1 : 0;
}

static inline void
setbit(bitarrayobject *self, idx_t i, int bit)
{
    char *cp, mask;

    mask = BITMASK(self->endian, i);
    cp = self->ob_item + i/8;
    if (bit)
	*cp |= mask;
    else
        *cp &= ~mask;
}

static int
resize(bitarrayobject *self, Py_ssize_t newsize)
{
    assert (newsize >= 0);
    
    /* Bypass realloc() when a previous overallocation is large enough
       to accommodate the newsize.  If the newsize is 16 smaller than the
       current size, then proceed with the realloc() to shrink the list.
    */
    if (self->allocated >= newsize &&
        self->ob_size < newsize + 16 &&
        self->ob_item != NULL)
    {
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

static int
check_overflow(idx_t nbits)
{
    assert (nbits >= 0);
    
    if (nbits > BITS(PY_SSIZE_T_MAX)) {
	char buff[256];
	sprintf(buff, "cannot create bitarray of size %lld, max size is %lld",
		nbits, BITS(PY_SSIZE_T_MAX));
	PyErr_SetString(PyExc_OverflowError, strdup(buff));
        return -1;
    }
    return 0;
}

/* Create new bitarray object without initialization of buffer */
static PyObject *
newbitarrayobject(PyTypeObject *type, idx_t nbits, int endian)
{
    bitarrayobject *obj;
    Py_ssize_t nbytes;
    
    assert (nbits >= 0);
    nbytes = BYTES(nbits);
    
    if (check_overflow(nbits) < 0)
        return NULL;
    
    obj = (bitarrayobject *) type->tp_alloc(type, 0);
    if (obj == NULL)
        return NULL;
    
    obj->ob_size = nbytes;
    obj->nbits = nbits;
    obj->endian = endian;
    if (nbytes == 0) {
        obj->ob_item = NULL;
    }
    else {
        obj->ob_item = PyMem_NEW(char, (size_t) nbytes);
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

static void
dealloc(bitarrayobject *self)
{
    if (self->weakreflist != NULL)
        PyObject_ClearWeakRefs((PyObject *) self);
    
    if (self->ob_item != NULL)
        PyMem_DEL(self->ob_item);
    
    self->ob_type->tp_free((PyObject *) self);
}

/* copy n bits from other (starting at b) onto self (starting at a) */
static void
bitcopy(bitarrayobject *self, idx_t a,
        bitarrayobject *other, idx_t b, idx_t n)
{
    /* XXX: This function can be highly optimized using memcpy 
       when self and other have same endianness, and other != self
    */
    idx_t i;
    
    assert (a >= 0 && b >= 0 && n >= 0);
    /* clip n, such that only memory with ob_size is accessed */
    if (a + n > BITS(self->ob_size))  n = BITS(self->ob_size) - a;
    if (b + n > BITS(other->ob_size)) n = BITS(other->ob_size) - b;
    
    /* the different type of looping is only relevant when other is self */
    if (a < b) {
        for (i = 0; i < n; i++)             /* loop forward (delete) */
            setbit(self, i + a, getbit(other, i + b));
    }
    else {
        for (i = n - 1; i >= 0; i--)      /* loop backwards (insert) */
            setbit(self, i + a, getbit(other, i + b));  
    }
}

/* starting at start, delete n bits from self */
static int
delete(bitarrayobject *self, idx_t start, idx_t n)
{
    assert (start >= 0 && start <= self->nbits);
    assert (n >= 0 && start + n <= self->nbits);
    if (n == 0)
        return 0;
    
    bitcopy(self, start, self, start + n, self->nbits - start);
    self->nbits -= n;
    if (resize(self, BYTES(self->nbits)) < 0)
        return -1;
    return 0;
}

/* at start, insert n (arbitrary) bits into self */
static int
insert(bitarrayobject *self, idx_t start, idx_t n)
{
    assert (start >= 0 && start <= self->nbits);
    assert (n >= 0);
    if (n == 0)
        return 0;

    self->nbits += n;   
    if (resize(self, BYTES(self->nbits)) < 0)
        return -1;

    bitcopy(self, start + n, self, start, self->nbits - start);
    return 0;
}

/* set the bits from start to stop (excluded) in self to val */
static void
setrange(bitarrayobject *self, idx_t start, idx_t stop, int val)
{
    /* XXX: This function can be highly optimized using memset */
    idx_t i;
    
    assert (start >= 0 && start <= self->nbits);
    assert (stop  >= 0 && stop  <= self->nbits);
    assert (start <= stop);
    
    for (i = start; i < stop; i++)
        setbit(self, i, val);
}

/* Set ususet bits to 0, without changing slef->nbits, return bits set */
static int
setunused(bitarrayobject *self)
{
    idx_t i, n;
    int res;

    res = 0;
    n = BITS(self->ob_size);
    for (i = self->nbits; i < n; i++) {
        setbit(self, i, 0);
        res++;
    }
    assert (res >= 0 && res < 8);
    return res;
}

/* Reverse the order of bits in each byte of the buffer */
static void
bytereverse(bitarrayobject *self)
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
    Py_ssize_t i;
    int c;
        
    setunused(self);
    for (i = 0; i < self->ob_size; i++) {
        c = self->ob_item[i];
        /* in case conversion to int puts a sign in */
        if (c < 0) c += 256;
        self->ob_item[i] = trans[c];
    }
}

/* Returns number of 1 bits */
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
    Py_ssize_t i;
    int c;
    
    res = 0;
    setunused(self);
    for (i = 0; i < self->ob_size; i++) {
        c = self->ob_item[i];
        /* in case conversion to int puts a sign in */
        if (c < 0) c += 256;
        res += bytecount[c];
    }
    return res;
}

/* Return index of first occurrence of bit, -1 when x is not in found. */
static idx_t
findfirst(bitarrayobject *self, int vi)
{
    Py_ssize_t j;
    idx_t i;
    char c;
    
    if (self->ob_size == 0)
        return -1;
    
    c = vi ? 0x00 : 0xff;  /* inverse! */
    
    /* skip ahead by checking whole bytes */
    for (j = 0; j < self->ob_size; j++)
        if (c ^ self->ob_item[j])
            break;
    
    if (j == self->ob_size)
        j--;
    
    /* fine graded search within byte */
    for (i = BITS(j); i < self->nbits; i++)
        if (getbit(self, i) == vi)
            return i;
    
    return -1;
}

static int
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
    self->nbits++;
    if (self->nbits > BITS(self->ob_size) &&
        resize(self, self->ob_size + 1) < 0)
        return -1;
    
    return set_item(self, self->nbits - 1, item);
}

static PyObject *
unpack(bitarrayobject *self, char zero, char one)
{
    PyObject *res;
    Py_ssize_t i;
    char *str;
    
    if (self->nbits > PY_SSIZE_T_MAX) {
	PyErr_SetString(PyExc_OverflowError, "bitarray too large to unpack");
        return NULL;
    }
    
    if ((str = malloc((size_t) self->nbits)) == NULL) {
        PyErr_NoMemory();
        return NULL;
    }
    for (i = 0; i < self->nbits; i++) {
        *(str + i) = getbit(self, i) ? one : zero;
    }
    res = PyString_FromStringAndSize(str, self->nbits);
    free(str);
    return res;
}

static int
extend_bitarray(bitarrayobject *self, bitarrayobject *other)
{
    idx_t sumbits;

    if (other->nbits == 0)
        return 0;
    
    sumbits = self->nbits + other->nbits;
    if (check_overflow(sumbits) < 0)
	return -1;
    
    if (resize(self, BYTES(sumbits)) < 0)
        return -1;
    
    bitcopy(self, self->nbits, other, 0, other->nbits);
    self->nbits += other->nbits;
    return 0;
}

static int
extend_iter(bitarrayobject *self, PyObject *iter)
{
    PyObject *item;
    
    assert (PyIter_Check(iter));
    while ((item = PyIter_Next(iter)) != NULL) {
        if (append_item(self, item) < 0) {
            Py_DECREF(item);
            return -1;
        }
        Py_DECREF(item);
    }
    if (PyErr_Occurred())
        return -1;

    return 0;
}

static int
extend_list(bitarrayobject *self, PyObject *list)
{
    PyObject *item;
    Py_ssize_t addbits, i;
    
    assert (PyList_Check(list));
    addbits = PyList_Size(list);
    if (addbits == 0)
        return 0;

    if (check_overflow(self->nbits + addbits) < 0)
	return -1;
    
    if (resize(self, BYTES(self->nbits + addbits)) < 0)
        return -1;
    self->nbits += addbits;
    
    for (i = 0; i < addbits; i++) {
        item = PyList_GetItem(list, i);
        if (item == NULL)
            return -1;
        set_item(self, self->nbits - addbits + i, item);
    }
    return 0;
}

static int
extend_tuple(bitarrayobject *self, PyObject *tuple)
{
    PyObject *item;
    Py_ssize_t addbits, i;
    
    assert (PyTuple_Check(tuple));
    addbits = PyTuple_Size(tuple);
    if (addbits == 0)
        return 0;
    
    if (check_overflow(self->nbits + addbits) < 0)
	return -1;
    
    if (resize(self, BYTES(self->nbits + addbits)) < 0)
        return -1;
    self->nbits += addbits;
    
    for (i = 0; i < addbits; i++) {
        item = PyTuple_GetItem(tuple, i);
        if (item == NULL)
            return -1;
        set_item(self, self->nbits - addbits + i, item);
    }
    return 0;
}

/* extend_string(): extend the bitarray from a string, where each whole
   characters is converted to a single bit
*/
enum {
    STR_01,    /*  '0' -> 0    '1'  -> 1   no other characters allowed */
    STR_RAW,   /*  '\0' -> 0   other -> 1                              */
};

static int
extend_string(bitarrayobject *self, PyObject *string, int kind)
{
    Py_ssize_t addbits, i;
    char c, buff[256], *str, *item;
    int bit;

    assert (PyString_Check(string));
    addbits = PyString_Size(string);
    if (addbits == 0)
        return 0;
    
    if (check_overflow(self->nbits + addbits) < 0)
	return -1;
    
    str = PyString_AsString(string);
    item = self->ob_item;
    
    if (resize(self, BYTES(self->nbits + addbits)) < 0)
        return -1;
    self->nbits += addbits;
    
    for (i = 0; i < addbits; i++) {
        c = *(str + i);
        /* depending on type, map c to bit */
        switch (kind) {
        case STR_01:
            switch (c) {
            case '0': bit = 0; break;
            case '1': bit = 1; break;
            default:
                sprintf(buff, "character must be '0' or '1', found '%c'", c);
                PyErr_SetString(PyExc_ValueError, strdup(buff));
                return -1;
            }
            break;
        case STR_RAW:
            bit = (c == '\0') ? 0 : 1;
            break;
        }
        setbit(self, self->nbits - addbits + i, bit);
    }
    return 0;
}

static int
extend_rawstring(bitarrayobject *self, PyObject *string)
{
    Py_ssize_t addbytes;
    char *str;
    
    assert (PyString_Check(string) && self->nbits % 8 == 0);
    addbytes = PyString_Size(string);
    if (addbytes == 0)
        return 0;
    
    if (check_overflow(self->nbits + BITS(addbytes)) < 0)
	return -1;
    
    str = PyString_AsString(string);
    
    self->nbits += BITS(addbytes);
    if (resize(self, self->ob_size + addbytes) < 0)
        return -1;
    
    assert (self->nbits == BITS(self->ob_size));
    memcpy(self->ob_item + (self->ob_size - addbytes), str, addbytes);
    
    return 0;
}

/* --------- helper functions not involving bitarrayobjects ------------ */

#define ENDIANSTR(x)  ((x) ? "big" : "little")

#define ISINDEX(x)  (PyInt_Check(x) || PyLong_Check(x) || PyIndex_Check(x))

/* Extract a slice index from a PyInt or PyLong or an object with the
   nb_index slot defined, and store in *i.  Return 0 on error, 1 on success.
   
   This is almost _PyEval_SliceIndex() with Py_ssize_t replaced by idx_t
*/
static int
getIndex(PyObject *v, idx_t *i)
{
    idx_t x;
    
    if (PyInt_Check(v)) {
	x = PyInt_AS_LONG(v);
    }
    else if (PyLong_Check(v)) {
	x = PyLong_AsLongLong(v);
    }
    else if (PyIndex_Check(v)) {
	x = PyNumber_AsSsize_t(v, NULL);
	if (x == -1 && PyErr_Occurred())
	    return 0;
    }
    else {
	PyErr_SetString(PyExc_TypeError,
			"slice indices must be integers or "
			"None or have an __index__ method");
	return 0;
    }
    *i = x;
    return 1;
}

/* This is PySlice_GetIndicesEx() with Py_ssize_t replaced by idx_t */
static int
slice_GetIndicesEx(PySliceObject *r, idx_t length,
                   idx_t *start, idx_t *stop, idx_t *step, idx_t *slicelength)
{
    idx_t defstart, defstop;
    
    if (r->step == Py_None) {
	*step = 1;
    } 
    else {
	if (!getIndex(r->step, step))
	    return -1;
	
	if (*step == 0) {
	    PyErr_SetString(PyExc_ValueError, "slice step cannot be zero");
	    return -1;
	}
    }
    defstart = *step < 0 ? length-1 : 0;
    defstop = *step < 0 ? -1 : length;
    
    if (r->start == Py_None) {
	*start = defstart;
    }
    else {
	if (!getIndex(r->start, start)) return -1;
	if (*start < 0) *start += length;
	if (*start < 0) *start = (*step < 0) ? -1 : 0;
	if (*start >= length) 
	    *start = (*step < 0) ? length - 1 : length;
    }
    
    if (r->stop == Py_None) {
	*stop = defstop;
    }
    else {
	if (!getIndex(r->stop, stop)) return -1;
	if (*stop < 0) *stop += length;
	if (*stop < 0) *stop = -1;
	if (*stop > length) *stop = length;
    }
    
    if ((*step < 0 && *stop >= *start) || (*step > 0 && *start >= *stop)) {
	*slicelength = 0;
    }
    else if (*step < 0) {
	*slicelength = (*stop - *start + 1) / (*step) + 1;
    }
    else {
	*slicelength = (*stop - *start - 1) / (*step) + 1;
    }
    
    return 0;
}

/****************************************************************************
                     Implementations of API methods follow.
****************************************************************************/

static PyObject *
bitarray_length(bitarrayobject *self)
{
    return PyLong_FromLongLong(self->nbits);
}

PyDoc_STRVAR(length_doc,
"length()\n\
\n\
Return the length, i.e. number of bits stored in the bitarray.\n\
This method is preferred over __len__, [used when typing ``len(a)``],\n\
since __len__ will fail for a bitarray object with 2^31 or more elements\n\
on a 32bit machine, whereas this method will return the correct value,\n\
on 32bit and 64bit machines.");

PyDoc_STRVAR(len_doc,
"__len__()\n\
\n\
Return the length, i.e. number of bits stored in the bitarray.\n\
This method will fail for a bitarray object with 2^31 or more elements\n\
on a 32bit machine.  Use bitarray.length() instead.");


static PyObject *
bitarray_copy(bitarrayobject *self)
{
    PyObject *res;
    
    res = newbitarrayobject(self->ob_type, self->nbits, self->endian);
    if (res == NULL)
        return NULL;
    
    memcpy(((bitarrayobject *) res)->ob_item,
           self->ob_item, self->ob_size);
    return res;
}

PyDoc_STRVAR(copy_doc,
"copy()\n\
\n\
Return a copy of the bitarray.");


static PyObject *
bitarray_count(bitarrayobject *self, PyObject *v)
{
    idx_t n1;
    long vi;
    
    vi = PyObject_IsTrue(v);
    if (vi < 0)
        return NULL;
    
    n1 = count(self);
    return PyLong_FromLongLong(vi ? n1 : self->nbits - n1);
}

PyDoc_STRVAR(count_doc,
"count(x)\n\
\n\
Return number of occurrences of x in the bitarray.");


static PyObject *
bitarray_index(bitarrayobject *self, PyObject *v)
{
    idx_t i;
    long vi;
    
    vi = PyObject_IsTrue(v);
    if (vi < 0)
        return NULL;
    
    i = findfirst(self, vi);
    if (i < 0) {
        PyErr_SetString(PyExc_ValueError, "index(x): x not in bitarray");
        return NULL;
    }
    return PyLong_FromLongLong(i);
}

PyDoc_STRVAR(index_doc,
"index(x)\n\
\n\
Return index of first occurrence of x in the bitarray.\n\
It is an error when x does not occur in the bitarray");


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
    if (bitarray_Check(obj)) {                            /* bitarray */
        if (extend_bitarray(self, (bitarrayobject *) obj) < 0)
            return NULL;
        Py_RETURN_NONE;
    }
    if (PyList_Check(obj)) {                                  /* list */
        if (extend_list(self, obj) < 0)
            return NULL;
        Py_RETURN_NONE;
    }
    if (PyTuple_Check(obj)) {                                /* tuple */
        if (extend_tuple(self, obj) < 0)
            return NULL;
        Py_RETURN_NONE;
    }
    if (PyString_Check(obj)) {                               /* str01 */
        if (extend_string(self, obj, STR_01) < 0)
            return NULL;
        Py_RETURN_NONE;
    }
    if (PyIter_Check(obj)) {                                  /* iter */
        if (extend_iter(self, obj) < 0)
            return NULL;
        Py_RETURN_NONE;
    }
    /* finally, try to get the iterator of the object */
    PyObject *iter;
    
    iter = PyObject_GetIter(obj);
    if (iter == NULL) {
        PyErr_SetString(PyExc_TypeError, "could not extend bitarray");
        return NULL;
    }
    if (extend_iter(self, iter) < 0)
        return NULL;
    Py_DECREF(iter);
    Py_RETURN_NONE;
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
    
    res = PyTuple_New(5);
    if (res == NULL)
        return NULL;
    
    PyTuple_SET_ITEM(res, 0, PyLong_FromVoidPtr(self->ob_item));
    PyTuple_SET_ITEM(res, 1, PyLong_FromLongLong(self->ob_size));
    PyTuple_SET_ITEM(res, 2, PyString_FromString(ENDIANSTR(self->endian)));
    PyTuple_SET_ITEM(res, 3, PyInt_FromLong(BITS(self->ob_size) - self->nbits));
    PyTuple_SET_ITEM(res, 4, PyLong_FromLongLong(self->allocated));
    return res;
}

PyDoc_STRVAR(buffer_info_doc,
"buffer_info()\n\
\n\
Return a tuple (address, size, endianness, unused, allocated) giving the\n\
current memory address, the size (in bytes) used to hold the bitarray's\n\
contents, the bit endianness as a string, the number of unused bits\n\
(e.g. a bitarray of length 11 will have a buffer size of 2 bytes and\n\
5 unused bits), and the size (in bytes) of the allocated memory.");


static PyObject *
bitarray_endian(bitarrayobject *self)
{
    return PyString_FromString(ENDIANSTR(self->endian));
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
Append the value bool(x) to the end of the bitarray.");


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
Returns True when all bits in the array are True.");


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
Returns True when any bit in the array is True.");


static PyObject *
bitarray_reduce(bitarrayobject *self)
{
    PyObject *dict, *result;
    int unusedbits;
    
    dict = PyObject_GetAttrString((PyObject *) self, "__dict__");
    if (dict == NULL) {
        PyErr_Clear();
        dict = Py_None;
        Py_INCREF(dict);
    }
    unusedbits = (int) (BITS(self->ob_size) - self->nbits);
    result = Py_BuildValue("O(s#is)O",
                           self->ob_type,
                           self->ob_item, self->ob_size,
                           unusedbits,
			   ENDIANSTR(self->endian),
                           dict);
    Py_DECREF(dict);
    return result;
}

PyDoc_STRVAR(reduce_doc, "Return state information for pickling.");


static PyObject *
bitarray_reverse(bitarrayobject *self)
{
    PyObject *t;    /* temp bitarray to store lower half of self */
    idx_t i, m;
    
    if (self->nbits < 2)
        Py_RETURN_NONE;
    
    t = newbitarrayobject(self->ob_type, self->nbits / 2, self->endian);
    if (t == NULL)
        return NULL;
    
#define tt  ((bitarrayobject *) t)
    /* copy first half of array into tmp array */
    memcpy(tt->ob_item, self->ob_item, tt->ob_size);
    
    m = self->nbits - 1;
    
    /* Reverse the upper half onto the lower half. */
    for (i = 0; i < tt->nbits; i++)
        setbit(self, i, getbit(self, m - i));
    
    /* Revert the stored away lower half onto the upper half. */
    for (i = 0; i < tt->nbits; i++)
        setbit(self, m - i, getbit(tt, i));
#undef tt
    Py_DECREF(t);
    Py_RETURN_NONE;
}

PyDoc_STRVAR(reverse_doc,
"reverse()\n\
\n\
Reverse the order of bits in the array (in-place).");


static PyObject *
bitarray_fill(bitarrayobject *self)
{
    long p;
    
    p = setunused(self);
    self->nbits += p;
    return PyInt_FromLong(p);
}

PyDoc_STRVAR(fill_doc,
"fill()\n\
\n\
Returns the number of bits added (0..7) at the end of the array.\n\
When the length of the bitarray is not a multiple of 8, increase the length\n\
slightly such that the new length is a multiple of 8, and set the few new\n\
bits to False.");


static PyObject *
bitarray_invert(bitarrayobject *self)
{
    Py_ssize_t i;
    
    for (i = 0; i < self->ob_size; i++)
        self->ob_item[i] = ~self->ob_item[i];
    
    Py_RETURN_NONE;
}

PyDoc_STRVAR(invert_doc,
"invert(x)\n\
\n\
Invert all bits in the array (in-place),\n\
i.e. convert each 1-bit into a 0-bit and vice versa.");


static PyObject *
bitarray_bitwise(bitarrayobject *self, PyObject *args)
{
    PyObject *other;
    char *operation;
    enum { AND, OR, XOR } op_type;
    Py_ssize_t i;
    bitarrayobject *s, *o;
    
    if (!PyArg_ParseTuple(args, "Os:_bitwise", &other, &operation))
        return NULL;
    
    if (!bitarray_Check(other)) {
	PyErr_SetString(PyExc_TypeError,
			"bitarray objects expected for bitwise operation");
	return NULL;
    }
    if (strcmp(operation, "and") == 0) { op_type = AND; }
    else if (strcmp(operation, "or") == 0) { op_type = OR; }
    else if (strcmp(operation, "xor") == 0) { op_type = XOR; }
    else {
	PyErr_SetString(PyExc_ValueError, "bitwise operation unknown");
	return NULL;
    }
    s = (bitarrayobject *) self;
    o = (bitarrayobject *) other;
    
    if (s->nbits != o->nbits) {
	PyErr_SetString(PyExc_ValueError,
			"bitarrays of equal length expected "
			"for bitwise operation");
	return NULL;
    }
    switch (op_type) {
    case AND:
	for (i = 0; i < self->ob_size; i++)
	    s->ob_item[i] &= o->ob_item[i];
	break;
    case OR:
	for (i = 0; i < self->ob_size; i++)
	    s->ob_item[i] |= o->ob_item[i];
	break;
    case XOR:
	for (i = 0; i < self->ob_size; i++)
	    s->ob_item[i] ^= o->ob_item[i];
	break;
    }
    Py_RETURN_NONE;
}

PyDoc_STRVAR(bitwise_doc,
"_bitwise(other, operation)\n\
\n\
Perform in-place bitwise operations, operations is a string specifying the\n\
operation ('and', 'or', 'xor').  This method is not meant to be called\n\
directly, but from, it is called by __and__, __iadd__, etc....");


static PyObject *
bitarray_bytereverse(bitarrayobject *self)
{
    bytereverse(self);
    Py_RETURN_NONE;
}

PyDoc_STRVAR(bytereverse_doc,
"bytereverse()\n\
\n\
For all bytes representing the bitarray, reverse the bit order (in-place).\n\
Note: This method changes the actual machine values representing the\n\
bitarray; it does not change the endianness of the bitarray object.");


static PyObject *
bitarray_setall(bitarrayobject *self, PyObject *v)
{
    long vi;
    
    vi = PyObject_IsTrue(v);
    if (vi < 0)
        return NULL;

    memset(self->ob_item, vi ? 0xff : 0x00, self->ob_size);
    Py_RETURN_NONE;
}

PyDoc_STRVAR(setall_doc,
"setall(x)\n\
\n\
Set all bits in the bitarray to bool(x).");


static PyObject *
bitarray_sort(bitarrayobject *self)
{
    idx_t n, n0;

    n = self->nbits;
    n0 = n - count(self);
    setrange(self, 0, n0, 0);
    setrange(self, n0, n, 1);
    Py_RETURN_NONE;
}

PyDoc_STRVAR(sort_doc,
"sort()\n\
\n\
Sort the bits in the array (in-place).");


static PyObject *
bitarray_fromfile(bitarrayobject *self, PyObject *args)
{
    PyObject *f;
    Py_ssize_t nbytes;
    FILE *fp;
    long cur;
    
    nbytes = -1;
    if (!PyArg_ParseTuple(args, "O|n:fromfile", &f, &nbytes))
        return NULL;
    
    fp = PyFile_AsFile(f);
    if (fp == NULL) {
        PyErr_SetString(PyExc_TypeError,
                        "first argument must be an open file");
        return NULL;
    }
    
     /* find number of bytes till EOF */
    if (nbytes < 0) {
        if ((cur = ftell (fp)) < 0)
            goto EOFerror;
        
        if (fseek (fp, 0L, SEEK_END) || (nbytes = ftell (fp)) < 0)
            goto EOFerror;
        
        nbytes -= cur;
        if (fseek (fp, cur, SEEK_SET)) {
        EOFerror:
            PyErr_SetString(PyExc_EOFError, "could not find EOF");
            return NULL;
        }
    }
    assert (nbytes >= 0);
    if (nbytes == 0)
        Py_RETURN_NONE;

    /* File exists and there are more than zero bytes to read */
    char *item;
    size_t nread, newsize;
    idx_t t1, t2, t3, i, n, p;
    
    t1 = self->nbits;
    t2 = self->nbits = BITS(self->ob_size);
    p = t2 - t1;      /* number of bits by which size has increased */
    assert (p >= 0 && p < 8);

    newsize = self->ob_size + nbytes;
    item = self->ob_item;

    PyMem_RESIZE(item, char, newsize);
    if (item == NULL) {
        PyErr_NoMemory();
        return NULL;
    }
    self->ob_item = item;
    self->ob_size = newsize;
    self->nbits = BITS(newsize);
    self->allocated = self->ob_size;
    nread = fread(item + (self->ob_size - nbytes), 1, nbytes, fp);
    if (nread < nbytes) {
        newsize -= nbytes - nread;
        self->ob_size = newsize;
        self->nbits = BITS(newsize);
        PyMem_RESIZE(item, char, newsize);
        self->ob_item = item;
        self->allocated = self->ob_size;
        PyErr_SetString(PyExc_EOFError, "not enough items in file");
        return NULL;
    }
    
    t3 = self->nbits;
    n = t3 - t2;         /* number of bits read from string */
    assert (n >= 0 && n % 8 == 0);
    for (i = 0; i < n; i++)
        setbit(self, t1 + i, getbit(self, t2 + i));
    self->nbits -= p;
    Py_RETURN_NONE;
}

PyDoc_STRVAR(fromfile_doc,
"fromfile(f [, n])\n\
\n\
Read n bytes from the file object f and append them to the bitarray\n\
interpreted as machine values.  When n is omitted, as many bytes are\n\
read until EOF is reached.");


static PyObject *
bitarray_tofile(bitarrayobject *self, PyObject *f)
{
    FILE *fp;
    
    fp = PyFile_AsFile(f);
    if (fp == NULL) {
        PyErr_SetString(PyExc_TypeError, "open file expected");
        return NULL;
    }
    if (self->ob_size == 0)
        Py_RETURN_NONE;
    
    setunused(self);
    if (fwrite(self->ob_item, 1, self->ob_size, fp) !=
        (size_t) self->ob_size) {
        PyErr_SetFromErrno(PyExc_IOError);
        clearerr(fp);
        return NULL;
    }
    Py_RETURN_NONE;
}

PyDoc_STRVAR(tofile_doc,
"tofile(f)\n\
\n\
Write all bits (as machine values) to the file object f.\n\
When the length of the bitarray is not a multiple of 8,\n\
the remaining bits (1..7) are set to 0.");


static PyObject *
bitarray_tolist(bitarrayobject *self)
{
    PyObject *list, *item;
    idx_t i;
    
    list = PyList_New(self->nbits);
    if (list == NULL)
        return NULL;
    
    for (i = 0; i < self->nbits; i++) {
        item = PyBool_FromLong(getbit(self, i));
        if (item == NULL) {
            Py_DECREF(list);
            return NULL;
        }
        PyList_SetItem(list, i, item);
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
    idx_t t1, t2, t3, i, n, p;
    
    if (!PyString_Check(string)) {
        PyErr_SetString(PyExc_TypeError, "string expected");
        return NULL;
    }
    t1 = self->nbits;
    t2 = self->nbits = BITS(self->ob_size);
    p = t2 - t1;      /* number of bits by which size has increased */
    assert (p >= 0 && p < 8);
    if (extend_rawstring(self, string) < 0)
        return NULL;
    
    t3 = self->nbits;
    n = t3 - t2;         /* number of bits read from string */
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
    setunused(self);
    return PyString_FromStringAndSize(self->ob_item, self->ob_size);
}

PyDoc_STRVAR(tostring_doc,
"tostring()\n\
\n\
Return the string representing (machine values) of the bitarray.\n\
When the length of the bitarray is not a multiple of 8, the few remaining\n\
bits (1..7) are set to 0.");


static PyObject *
bitarray_to01(bitarrayobject *self)
{
    return unpack(self, '0', '1');
}

PyDoc_STRVAR(to01_doc,
"to01()\n\
\n\
Return a string containing '0's and '1's, representing the bits in the\n\
bitarray object.");


static PyObject *
bitarray_unpack(bitarrayobject *self, PyObject *args, PyObject *kwds)
{
    char zero = 0x00, one = 0xff;
    static char* kwlist[] = {"zero", "one", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|cc:unpack", kwlist,
				     &zero, &one))
        return NULL;
    
    return unpack(self, zero, one);
}

PyDoc_STRVAR(unpack_doc,
"unpack(zero='\\x00', one='\\xff')\n\
\n\
Return a string containing one character for each bit in the bitarray,\n\
using the specifield mapping.\n\
Note that unpack('0', '1') has the same effect as to01().\n\
See also the pack method.");


static PyObject *
bitarray_pack(bitarrayobject *self, PyObject *string)
{
    if (!PyString_Check(string)) {
        PyErr_SetString(PyExc_TypeError, "string expected");
        return NULL;
    }
    if (extend_string(self, string, STR_RAW) < 0)
        return NULL;

    Py_RETURN_NONE;
}

PyDoc_STRVAR(pack_doc,
"pack(string)\n\
\n\
Extend the bitarray from a string, where each characters corresponds to\n\
a single bit.  The character '\\x00' maps to bit 0 and all other characters\n\
map to bit 1.\n\
This method, as well as the unpack method, are meant for efficient\n\
transfer of data between bitarray objects to other python objects\n\
(for example NumPy's ndarray object) which have a different view of memory.");


static PyObject *
bitarray_repr(bitarrayobject *self)
{
    PyObject *string;
    
    if (self->nbits == 0)
        return PyString_FromString("bitarray()");
    
    string = PyString_FromString("bitarray(\'");
    PyString_ConcatAndDel(&string, unpack(self, '0', '1'));
    PyString_ConcatAndDel(&string, PyString_FromString("\')"));
    return string;
}


static PyObject *
bitarray_insert(bitarrayobject *self, PyObject *args)
{
    idx_t i;
    PyObject *v;
    
    if (!PyArg_ParseTuple(args, "LO:insert", &i, &v))
        return NULL;
    
    if (i < 0) {
        i += self->nbits;
        if (i < 0)
            i = 0;
    }
    if (i >= self->nbits)
        i = self->nbits;
    
    if (insert(self, i, 1) < 0)
        return NULL;
    
    set_item(self, i, v);
    Py_RETURN_NONE;
}

PyDoc_STRVAR(insert_doc,
"insert(i, x)\n\
\n\
Insert a new item x into the bitarray before position i.");


static PyObject *
bitarray_pop(bitarrayobject *self, PyObject *args)
{
    idx_t i = -1;
    long tmp;
    
    if (!PyArg_ParseTuple(args, "|L:pop", &i))
        return NULL;
    
    if (self->nbits == 0) {
        PyErr_SetString(PyExc_IndexError, "pop from empty bitarray");
        return NULL;
    }
    if (i < 0)
        i += self->nbits;
    
    if (i < 0 || i >= self->nbits) {
        PyErr_SetString(PyExc_IndexError, "pop index out of range");
        return NULL;
    }
    tmp = getbit(self, i);
    if (delete(self, i, 1) < 0)
        return NULL;
    return PyBool_FromLong(tmp);
}

PyDoc_STRVAR(pop_doc,
"pop([i])\n\
\n\
Return the i-th element and delete it from the bitarray. i defaults to -1.");


static PyObject *
bitarray_remove(bitarrayobject *self, PyObject *v)
{
    idx_t i;
    long vi;
    
    vi = PyObject_IsTrue(v);
    if (vi < 0)
        return NULL;

    i = findfirst(self, vi);
    if (i < 0) {
        PyErr_SetString(PyExc_ValueError, "remove(x): x not in bitarray");
        return NULL;
    }
    if (delete(self, i, 1) < 0)
        return NULL;
    Py_RETURN_NONE;
}

PyDoc_STRVAR(remove_doc,
"remove(x)\n\
\n\
Remove the first occurrence of x in the bitarray.");


static PyObject *
bitarray_getitem(bitarrayobject *self, PyObject *a)
{
    PyObject *res;
    idx_t start, stop, step, slicelength, cur, i;
    
    if (ISINDEX(a)) {
	getIndex(a, &i);
	
	if (i < 0)
            i += self->nbits;
	
        if (i < 0 || i >= self->nbits) {
            PyErr_SetString(PyExc_IndexError, "bitarray index out of range");
            return NULL;
        }
        return PyBool_FromLong(getbit(self, i));
    }
    if (PySlice_Check(a)) {
        if(slice_GetIndicesEx((PySliceObject *) a, self->nbits,
			      &start, &stop, &step, &slicelength) < 0) {
	    return NULL;
        }
        res = newbitarrayobject(self->ob_type, slicelength, self->endian);
        if (res == NULL)
            return NULL;
        
        for (i = 0, cur = start; i < slicelength; i++, cur += step)
            setbit((bitarrayobject *) res, i, getbit(self, cur));
        
        return res;
    }
    PyErr_SetString(PyExc_TypeError, "index or slice expected");
    return NULL;
}

static PyObject *
bitarray_setitem(bitarrayobject *self, PyObject *args)
{
    PyObject *a, *v;
    idx_t start, stop, step, slicelength, i, j;
    
    if (!PyArg_ParseTuple(args, "OO|__setitem__", &a, &v))
        return NULL;
    
    if (ISINDEX(a)) {
	getIndex(a, &i);
	
        if (i < 0)
            i += self->nbits;
	
        if (i < 0 || i >= self->nbits) {
            PyErr_SetString(PyExc_IndexError, "bitarray index out of range");
            return NULL;
        }
        set_item(self, i, v);
        Py_RETURN_NONE;
    }
    if (PySlice_Check(a)) {
        if(slice_GetIndicesEx((PySliceObject *) a, self->nbits,
			      &start, &stop, &step, &slicelength) < 0) {
            return NULL;
        }
        if (!bitarray_Check(v)) {
            PyErr_SetString(PyExc_IndexError,
			    "bitarray expected in slice assignment");
            return NULL;
        }
#define vv  ((bitarrayobject *) v)
        if (vv->nbits == slicelength) {
            for (i = 0, j = start; i < slicelength; i++, j += step)
                setbit(self, j, getbit(vv, i));
            Py_RETURN_NONE;
        }
        if (step != 1) {
            char buff[256];
            sprintf(buff,
		    "attempt to assign sequence of size %lld "
                    "to extended slice of size %lld",
                    vv->nbits, (idx_t) slicelength);
            PyErr_SetString(PyExc_ValueError, strdup(buff));
            return NULL;
        }
        assert (step == 1);
        
        /* make self bigger or smaller */
        if (vv->nbits > slicelength) {
            if (insert(self, start, vv->nbits - slicelength) < 0)
                return NULL;
        }
        else {
            if (delete(self, start, slicelength - vv->nbits) < 0)
                return NULL;
        }
        /* copy the new values into self */
        bitcopy(self, start, vv, 0, vv->nbits);
        Py_RETURN_NONE;
#undef vv
    }
    PyErr_SetString(PyExc_TypeError, "index or slice expected");
    return NULL;
}

static PyObject *
bitarray_delitem(bitarrayobject *self, PyObject *a)
{
    idx_t start, stop, step, slicelength, cur, i;
    
    if (ISINDEX(a)) {
	getIndex(a, &i);
	
        if (i < 0)
            i += self->nbits;
	
        if (i < 0 || i >= self->nbits) {
            PyErr_SetString(PyExc_IndexError,
                            "bitarray assignment index out of range");
            return NULL;
        }
        if (delete(self, i, 1) < 0)
            return NULL;
        Py_RETURN_NONE;
    }
    if (PySlice_Check(a)) {
        if(slice_GetIndicesEx((PySliceObject *) a, self->nbits,
			      &start, &stop, &step, &slicelength) < 0) {
            return NULL;
        }
        if (slicelength == 0)
            Py_RETURN_NONE;
        
        if (step < 0) {
            stop = start + 1;
            start = stop + step * (slicelength - 1) - 1;
            step = -step;
        }
        if (step == 1) {
            assert (stop - start == slicelength);
            if (delete(self, start, slicelength) < 0)
                return NULL;
            Py_RETURN_NONE;
        }
        /* This is the only complicated part when step > 1 */
        for (cur = i = start; i < self->nbits; i++)
            if ((i - start) % step != 0 || i >= stop)
                setbit(self, cur++, getbit(self, i));
        self->nbits -= slicelength;
        resize(self, BYTES(self->nbits));
        Py_RETURN_NONE;
    }
    PyErr_SetString(PyExc_TypeError, "index or slice expected");
    return NULL;
}

/******************* variable length encoding and decoding ***************/

static int
check_CodeDict(PyObject *dict)
{
    PyObject *values = NULL, *bits;
    Py_ssize_t N, i;
    int ret = -1;
    
    if (!PyDict_Check(dict)) {
        PyErr_SetString(PyExc_TypeError, "dictionary expected");
        goto error;
    }
    N = PyDict_Size(dict);
    if (N == 0) {
        PyErr_SetString(PyExc_ValueError, "dict is empty");
        goto error;
    }
    values = PyDict_Values(dict);
    if (values == NULL || PyList_Size(values) != N)
        goto error;
    
    for (i = 0; i < N; i++) {
        bits = PyList_GetItem(values, i);
        if (bits == NULL)
            goto error;
        
        if (!bitarray_Check(bits)) {
            PyErr_SetString(PyExc_TypeError,
                            "bitarray expected for dictionary value");
            goto error;
        }
    }
    ret = 0; /* success */
 error:
    Py_XDECREF(values);
    return ret;
}

static PyObject *
bitarray_encode(bitarrayobject *self, PyObject *args)
{
    PyObject *codedict, *iterable, *iter, *symbol, *bits;
    
    if (!PyArg_ParseTuple(args, "OO:encode", &codedict, &iterable))
        return NULL;

    if (check_CodeDict(codedict) < 0)
        return NULL;

    iter = PyObject_GetIter(iterable);
    if (iter == NULL) {
        PyErr_SetString(PyExc_TypeError, "iterable object expected");
        return NULL;
    }
    /* Extend self with the bitarrays from codedict */
    while ((symbol = PyIter_Next(iter)) != NULL) {
        bits = PyDict_GetItem(codedict, symbol);
        Py_DECREF(symbol);
        if (bits == NULL) {
            PyErr_SetString(PyExc_ValueError, "symbol not found in code");    
            Py_DECREF(iter);
            return NULL;
        }
        bitarray_extend(self, bits);
    }
    Py_DECREF(iter);
    if (PyErr_Occurred())
        return NULL;
    
    Py_RETURN_NONE;
}

PyDoc_STRVAR(encode_doc,
"encode(code, iterable)\n\
\n\
Given a code (a dict mapping symbols to bitarrays),\n\
iterates over iterable object with symbols, and extends the bitarray\n\
with the corresponding bitarray for each symbols, using the code.");


static PyObject *
bitarray_decode(bitarrayobject *self, PyObject *codedict)
{
    PyObject *res, *item, *d, *b;
    idx_t pos = 0;
    int i, size, minsize = 1, maxsize = 100;

    if (check_CodeDict(codedict) < 0)
        return NULL;

    res = PyList_New(0);        /* list of symbols to be returned */
    
    // XXX
    while (pos < self->nbits) {
        for (size = minsize; size < maxsize; size++) {
            //printf("size = %d\n", size);
            b = newbitarrayobject(self->ob_type, size, self->endian);
            for (i = 0; i < size; i++)
                setbit((bitarrayobject *) b, i,
                       getbit(self, i + pos));
            
            item = PyDict_GetItem(d, b);
            dealloc((bitarrayobject *) b);
            if (item != NULL) {
                PyList_Append(res, item);
                pos += size;
                break;
            }
        }
        if (size > 95)
            break;
    }
    return res;
}

PyDoc_STRVAR(decode_doc,
"decode(code)\n\
\n\
Given a code (a dict mapping symbols to bitarrays),\n\
decode the content of the bitarray and return the list of symbols.");


/*************************** Method definitions *************************/

static PyMethodDef
bitarray_methods[] = {
    {"all",          (PyCFunction)bitarray_all,         METH_NOARGS,
     all_doc},
    {"any",          (PyCFunction)bitarray_any,         METH_NOARGS,
     any_doc},
    {"append",       (PyCFunction)bitarray_append,      METH_O,
     append_doc},
    {"_bitwise",     (PyCFunction)bitarray_bitwise,     METH_VARARGS,
     bitwise_doc},
    {"buffer_info",  (PyCFunction)bitarray_buffer_info, METH_NOARGS,
     buffer_info_doc},
    {"bytereverse",  (PyCFunction)bitarray_bytereverse, METH_NOARGS,
     bytereverse_doc},
    {"__contains__", (PyCFunction)bitarray_contains,    METH_O,
     contains_doc},
    {"copy",         (PyCFunction)bitarray_copy,        METH_NOARGS,
     copy_doc},
    {"__copy__",     (PyCFunction)bitarray_copy,        METH_NOARGS,
     copy_doc},
    {"count",        (PyCFunction)bitarray_count,       METH_O,
     count_doc},
    {"__deepcopy__", (PyCFunction)bitarray_copy,        METH_O,
     copy_doc},
    {"__delitem__",  (PyCFunction)bitarray_delitem,     METH_O,
     0},
    {"_decode",       (PyCFunction)bitarray_decode,     METH_O,
     decode_doc},
    {"_encode",       (PyCFunction)bitarray_encode,     METH_VARARGS,
     encode_doc},
    {"endian",       (PyCFunction)bitarray_endian,      METH_NOARGS,
     endian_doc},
    {"extend",       (PyCFunction)bitarray_extend,      METH_O,
     extend_doc},
    {"fill",         (PyCFunction)bitarray_fill,        METH_NOARGS,
     fill_doc},
    {"fromfile",     (PyCFunction)bitarray_fromfile,    METH_VARARGS,
     fromfile_doc},
    {"fromstring",   (PyCFunction)bitarray_fromstring,  METH_O,
     fromstring_doc},
    {"__getitem__",  (PyCFunction)bitarray_getitem,     METH_O,
     0},
    {"index",        (PyCFunction)bitarray_index,       METH_O,
     index_doc},
    {"insert",       (PyCFunction)bitarray_insert,      METH_VARARGS,
     insert_doc},
    {"invert",       (PyCFunction)bitarray_invert,      METH_NOARGS,
     invert_doc},
    {"__len__",      (PyCFunction)bitarray_length,      METH_NOARGS,
     len_doc},
    {"length",       (PyCFunction)bitarray_length,      METH_NOARGS,
     length_doc},
    {"pack",         (PyCFunction)bitarray_pack,        METH_O,
     pack_doc},
    {"pop",          (PyCFunction)bitarray_pop,         METH_VARARGS,
     pop_doc},
    {"__reduce__",   (PyCFunction)bitarray_reduce,      METH_NOARGS,
     reduce_doc},
    {"remove",       (PyCFunction)bitarray_remove,      METH_O,
     remove_doc},
    {"reverse",      (PyCFunction)bitarray_reverse,     METH_NOARGS,
     reverse_doc},
    {"setall",       (PyCFunction)bitarray_setall,      METH_O,
     setall_doc},
    {"__setitem__",  (PyCFunction)bitarray_setitem,     METH_VARARGS,
     0},
    {"sort",         (PyCFunction)bitarray_sort,        METH_NOARGS,
     sort_doc},
    {"tofile",       (PyCFunction)bitarray_tofile,      METH_O,
     tofile_doc},
    {"tolist",       (PyCFunction)bitarray_tolist,      METH_NOARGS,
     tolist_doc},
    {"tostring",     (PyCFunction)bitarray_tostring,    METH_NOARGS,
     tostring_doc},
    {"to01",         (PyCFunction)bitarray_to01,        METH_NOARGS,
     to01_doc},
    {"unpack",       (PyCFunction)bitarray_unpack,      METH_VARARGS |
                                                        METH_KEYWORDS,
     unpack_doc},
    {NULL,      NULL}       /* sentinel */
};


static PyObject *
bitarray_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *initial;
    int unusedbits = -1;
    char *endianStr = "<NOT_PROVIDED>";
    int endian = DEFAULT_ENDIAN;
    static char* kwlist[] = {"initial", "unusedbits", "endian", NULL};
    
    initial = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, kwds,
                                     "|Ois:bitarray", kwlist,
                                     &initial, &unusedbits, &endianStr)) {
        return NULL;
    }
    if (strcmp(endianStr, "little") == 0) {
        endian = 0;
    }
    else if (strcmp(endianStr, "big") == 0) {
        endian = 1;
    }
    else if (strcmp(endianStr, "<NOT_PROVIDED>") == 0) {
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
    if (ISINDEX(initial)) {
	idx_t nbits;
	getIndex(initial, &nbits);
	
        if (nbits < 0) {
            PyErr_SetString(PyExc_ValueError,
                            "cannot create bitarray with negative length");
            return NULL;
        }
        return newbitarrayobject(type, nbits, endian);
    }
    PyObject *a;  /* to be returned */
    
    /* from bitarray itself */
    if (bitarray_Check(initial)) {
#define np  ((bitarrayobject *) initial)
        a = newbitarrayobject(type, np->nbits,
                              (strcmp(endianStr, "<NOT_PROVIDED>") == 0  ?
                               np->endian : endian));
        
        memcpy(((bitarrayobject *) a)->ob_item, np->ob_item, np->ob_size);
#undef np
        return a;
    }
    
    /* the following cases extend a */
    a = newbitarrayobject(type, 0, endian);
    
    /* raw string, for pickling and expert use only */
    if (PyString_Check(initial) && unusedbits >= 0) {
        if (unusedbits >= 8) {
            PyErr_SetString(PyExc_ValueError, "unusedbits not 0..7");
            return NULL;
        }
        if (extend_rawstring((bitarrayobject *) a, initial) < 0)
            return NULL;
        
#define abits  (((bitarrayobject *) a)->nbits)
        assert (abits % 8 == 0);
        if (abits == 0 && unusedbits > 0) {
            PyErr_SetString(PyExc_ValueError, 
                            "unusedbits > 0 given but string is empty");
            return NULL;
        }
        abits -= unusedbits;
#undef abits
        return a;
    }

    /* leave remaining type  dispatch to the extend method */
    if (bitarray_extend((bitarrayobject *) a, initial) == NULL)
        return NULL;
    
    return a;
} /* END bitarray_new */


static PyObject *
richcompare(PyObject *v, PyObject *w, int op)
{
    int cmp, k, vi, wi;
    idx_t i;
    
    if (!bitarray_Check(v) || !bitarray_Check(w)) {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }
#define va  ((bitarrayobject *) v)
#define wa  ((bitarrayobject *) w)
    if (va->nbits != wa->nbits && (op == Py_EQ || op == Py_NE)) {
        /* Shortcut: if the lengths differ, the bitarrays differ */
        if (op == Py_EQ)
            Py_RETURN_FALSE;
        
        Py_RETURN_TRUE;
    }
    /* to avoid uninitialized warning for some compilers */
    vi = wi = 0;
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
#undef va
#undef wa
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


static PyObject *bitarray_iter(bitarrayobject *self);


static PyTypeObject Bitarraytype = {
    PyObject_HEAD_INIT(NULL)
    0,
    "_bitarray._bitarray",
    sizeof(bitarrayobject),
    0,
    (destructor) dealloc,                     /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    (reprfunc) bitarray_repr,                 /* tp_repr */
    0,                                        /* tp_as_number*/
    0,                                        /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    0,                                        /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    PyObject_GenericGetAttr,                  /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_WEAKREFS,
                                              /* tp_flags */
    0,                                        /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    richcompare,                              /* tp_richcompare */
    offsetof(bitarrayobject, weakreflist),    /* tp_weaklistoffset */
    (getiterfunc) bitarray_iter,              /* tp_iter */
    0,                                        /* tp_iternext */
    bitarray_methods,                         /* tp_methods */
    0,                                        /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    PyType_GenericAlloc,                      /* tp_alloc */
    bitarray_new,                             /* tp_new */
    PyObject_Del,                             /* tp_free */
};


/*********************** Bitarray Iterator **************************/

typedef struct {
    PyObject_HEAD
    idx_t           index;
    bitarrayobject*     ao;
} bitarrayiterobject;

static PyTypeObject BitarrayIter_Type;

#define BitarrayIter_Check(op)  PyObject_TypeCheck(op, &BitarrayIter_Type)

static PyObject *
bitarray_iter(bitarrayobject *self)
{
    bitarrayiterobject *it;
    
    if (!bitarray_Check(self)) {
        PyErr_BadInternalCall();
        return NULL;
    }
    it = PyObject_GC_New(bitarrayiterobject, &BitarrayIter_Type);
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
    assert (BitarrayIter_Check(it));
    if (it->index < it->ao->nbits)
        return PyBool_FromLong(getbit(it->ao, it->index++));
    
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

static PyTypeObject BitarrayIter_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "bitarrayiterator",                       /* tp_name */
    sizeof(bitarrayiterobject),               /* tp_basicsize */
    0,                                        /* tp_itemsize */
    /* methods */
    (destructor) bitarrayiter_dealloc,        /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    0,                                        /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    0,                                        /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    PyObject_GenericGetAttr,                  /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,  /* tp_flags */
    0,                                        /* tp_doc */
    (traverseproc) bitarrayiter_traverse,     /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    PyObject_SelfIter,                        /* tp_iter */
    (iternextfunc) bitarrayiter_next,         /* tp_iternext */
    0,                                        /* tp_methods */
};

/*************************** Functions **********************/

static PyObject *
bits2bytes(PyObject *self, PyObject *v)
{
    idx_t n;
    
    if (ISINDEX(v)) {
	getIndex(v, &n);
	if (n >= 0)
	    return PyLong_FromLongLong(BYTES(n));
	
	PyErr_SetString(PyExc_ValueError, "positive value expected");
	return NULL;
    }
    PyErr_SetString(PyExc_TypeError, "integer expected");
    return NULL;
}

PyDoc_STRVAR(bits2bytes_doc,
"bits2bytes(n)\n\
\n\
Return the number of bytes necessary to store n bits.");


static PyMethodDef module_functions[] = {
    {"bits2bytes",   bits2bytes,   METH_O,  bits2bytes_doc},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

/*********************** Install Module **************************/

PyMODINIT_FUNC
init_bitarray(void)
{
    PyObject *m;
    
    Bitarraytype.ob_type = &PyType_Type;
    BitarrayIter_Type.ob_type = &PyType_Type;
    m = Py_InitModule3("_bitarray", module_functions, 0);
    if (m == NULL)
	return;
    
    Py_INCREF((PyObject *) &Bitarraytype);
    PyModule_AddObject(m, "_bitarray", (PyObject *) &Bitarraytype);
}
