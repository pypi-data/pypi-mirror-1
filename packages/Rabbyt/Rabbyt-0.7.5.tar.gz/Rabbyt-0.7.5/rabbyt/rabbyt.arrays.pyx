"""
This module is ALPHA!  There might be API changes in the future.  This doesn't
mean that you shouldn't use it, just don't get mad if you have to make a few
minor changes in the future.

AND it's mostly undocumented.  The tests might get you started.

AND it's unoptimized.  Right now it's pretty slow.
"""

__credits__ = (
"""
Copyright (C) 2007  Matthew Marshall

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
""")

# FIXME Check for dependency array size changes.

__author__ = "Matthew Marshall <matthew@matthewmarshall.org>"


cdef extern from "stdlib.h":
    ctypedef unsigned int size_t
    cdef void *malloc(size_t size)
    cdef void free(void *ptr)
    cdef void *realloc(void *ptr, size_t size)


cdef extern from "Python.h":
    object PyObject_GenericGetAttr(object o, object name)
    int PyObject_GenericSetAttr(object o, object name, object value)


cdef class _BaseArray:

    cdef void _sync_data_ptr(self):
       if not self._is_data_owner:
           self.data_owner._sync_data_ptr()
           self._data = self.data_owner._data
           self._count = self.data_owner._count

    cdef float _getitem(self, int index):
        return self._data[index*self._stride]

    cdef void _setitem(self, int index, float value):
        raise NotImplemented


    def __dealloc__(self):
        # We need this as well as data_owner because we might not be an
        # object anymore.
        if self._is_data_owner:
            free(self._data)
            self._data = NULL

    def __init__(self, _BaseArray data_owner):
        #self._borrowers = []

        self._is_assignable = False

        self.data_owner = data_owner
        if data_owner == self:
            self._is_data_owner = True
            self._data = NULL
            self._allocated_size = 0
        else:
            self._is_data_owner = False
            self._sync_data_ptr()
            self._stride = data_owner._stride
            #data_owner._add_borrower(self)

    cdef int _convert_index(self, int raw):
        return raw

    def _size_changed(self, int new_size):
        self._count = new_size

    def __len__(self):
        self._sync_data_ptr()
        return self._count

    def _grow(self, int additional_size, exact):
        cdef int new_size, i
        self._count = self._count + additional_size
        if exact:
            new_size = self._count
        else:
            new_size = self._allocated_size/sizeof(float) + 1
            while self._count > new_size:
                new_size = new_size * 2
        if new_size*sizeof(float) > self._allocated_size:
            self._data = <float*>realloc(self._data,
                    sizeof(float)*self._stride*new_size)
            # TODO Give the data some defaults
            self._allocated_size = self._stride*new_size
        self._size_changed(self._count)

    def set_size(self, int size):
        """
        ``set_size(size)``

        Sets the size explicitly.

        This is an alternative to using ``append`` and ``extend``.  (It should
        be a little faster.)
        """
        if self.data_owner != self:
            raise RuntimeError("Not data owner")
        if size > self._count:
            self._grow(size-self._count, True)
        elif size < self._count:
            self._count = size
            self._allocated_size = self._stride*size
            self._data = <float*>realloc(self._data,
                    sizeof(float)*self._allocated_size)
            self._size_changed(self._count)

    def append(self, item):
        """
        ``append(item)``

        Appends an item to the array.

        """
        if self.data_owner != self:
            raise RuntimeError("Not data owner")
        self._grow(1, False)
        try:
            self[self._count - 1] = item
        except:
            # If there was an error assigning the item, we don't want to leave
            # dead vertex behind.
            self._count = self._count - 1
            raise

    def extend(self, vertexes):
        """
        ``extend(vertexes)``

        Iterates over vertexes, calling ``append(vertex)`` on each one.
        """
        for v in vertexes:
            self.append(v)

    def get_data_addr(self):
        self._sync_data_ptr()
        return <unsigned long>self._data

    def get_data_stride(self):
        self._sync_data_ptr()
        return self._stride*sizeof(float)

cdef class ItemInfo # Forward declaration

cdef class Array2d(_BaseArray):

    cdef object _attributes
    cdef object _attribute_arrays, _column_arrays
    cdef object _swizzles
    cdef object _defaults

    def __init__(self, attributes, initial_data=[], swizzles={}, size=0,
            defaults=None):
        _BaseArray.__init__(self, data_owner=self)
        cdef int i
        self._stride = len(attributes)
        self._attributes = list(attributes)
        self._swizzles = swizzles

        self._is_assignable = False

        if not defaults:
            self._defaults = [0] * len(self._attributes)
        else:
            self._defaults = defaults

        size = max(len(initial_data), size)
        self.set_size(size)

        self._attribute_arrays = {}
        self._column_arrays = []
        for i, name in enumerate(self._attributes):
            if isinstance(name, basestring):
                array = OffsetArray(self, i)
                self._attribute_arrays[name] = array
                self._column_arrays.append(array)
            else:
                assert len(name) == 4
                for j, bytename in enumerate(name):
                    array = OffsetUByteArray(self, i, j)
                    self._attribute_arrays[bytename] = array
                    self._column_arrays.append(array)

        cdef initial_len
        initial_len = len(initial_data)
        for i from 0 <= i < initial_len:
            self[i] = initial_data[i]
        for i from initial_len <= i < size:
            self[i] = self._defaults

    def __getattr__(self, name):
        if self._attribute_arrays is not None and\
                name in self._attribute_arrays:
            return self._attribute_arrays[name]
        else:
            return PyObject_GenericGetAttr(self, name)

    def __setattr__(self, name, value):
        if self._attribute_arrays is not None and\
                name in self._attribute_arrays:
            self._attribute_arrays[name].assign_from(value)
        elif self._swizzles is not None and name in self._swizzles:
            raise NotImplemented
        else:
            PyObject_GenericSetAttr(self, name, value)

    def __getitem__(self, int index):
        if index >= len(self):
            raise IndexError(index)
        return ItemInfo(self, self._convert_index(index))

    def __setitem__(self, int index, value):
        if index >= len(self):
            raise IndexError(index)
        ItemInfo(self, self._convert_index(index))._update(value)


cdef class _BaseArray1d(_BaseArray):
    def __init__(self, data_owner):
        _BaseArray.__init__(self, data_owner=data_owner)

    cdef void _setitem(self, int index, float value):
        self._data[self._convert_index(index)*self._stride] = value

    cdef float _getitem(self, int index):
        return self._data[self._convert_index(index)*self._stride]

    def __setitem__(self, int index, float value):
        self._sync_data_ptr()
        if not self._is_assignable:
            raise ValueError("This array is not assignable.")
        if index >= len(self):
            raise IndexError
        self._setitem(index, value)

    def __getitem__(self, int index):
        self._sync_data_ptr()
        if index >= len(self):
            raise IndexError
        return self._getitem(index)

    def __add__(self, other):
        return ArrayOpAdd(self, other)

    def __sub__(self, other):
        return ArrayOpSub(self, other)

    def __mul__(self, other):
        return ArrayOpMul(self, other)

    def __div__(self, other):
        return ArrayOpDiv(self, other)

    def __iadd__(self, other):
        ArrayOpAdd(self, other).assign_to(self)
        return self

    def __isub__(self, other):
        ArrayOpSub(self, other).assign_to(self)
        return self

    def __imul__(self, other):
        ArrayOpMul(self, other).assign_to(self)
        return self

    def __idiv__(self, other):
        ArrayOpDiv(self, other).assign_to(self)
        return self


    def assign_from(self, source):
        """
        assigns our value *from* other array/iter/operation.
        """
        self._sync_data_ptr()
        if not self._is_assignable:
            raise ValueError("This array is not assignable")
        cdef int i
        cdef float f
        try:
            f = float(source) #Test if it's a number
            for i from 0 <= i < self._count:
                self._setitem(i, f)
            return
        except TypeError:
            pass
        # If that didn't work, try for it being something with a length.
        if not len(source) == len(self):
            raise ValueError("Mismatched lengths")
        if hasattr(source, 'assign_to'):
            source.assign_to(self)
        else:
            for i from 0 <= i < self._count:
                self._setitem(i, source[i])

    def assign_to(self, _BaseArray1d target):
        """
        Assigns our value *to* another array.
        """
        self._sync_data_ptr()
        target._sync_data_ptr()
        if not len(target) == len(self):
            raise ValueError("Mismatched lengths")
        if not target._is_assignable:
            raise ValueError("Array is not assignable")
        cdef int i
        for i from 0 <= i < target._count:
            target._setitem(i, self._getitem(i))

    def __repr__(self):
        items = []
        for f in self:
            items.append(str(f))
        return "<%s [%s]>" % (self.__class__.__name__, ', '.join(items))

    def stretch(self, int times):
        """
        ``stretch(times)``

        Returns a new stretched version of this array.  Each item is
        duplicated ``times`` times.

        For example, ``Array1d([1,2,3]).stretch(3)`` will appear as
        ``Array1d([1,1,1,2,2,2,3,3,3])``.

        Note that what ``stretch`` returns is a new array, so you can perform
        arithmetic operations on it and such, but *no data* is copied.  If
        you make a modification to the origial array it will appear in the
        stretched version, and vice-versa.
        """
        return _StretchedArray1d(self, times)

    def repeat(self, int times):
        """
        ``repeat(times)``

        Returns a repeated version of this array.

        For example, ``Array1d([1,2,3]).repeat(3)`` will appear like
        ``Array1d([1,2,3,1,2,3,1,2,3])``.

        Just like ``stretch()``, ``repeat()`` is lazy.  No data is copied, and
        if you modify the origial array the repeated array will change with
        it.
        """
        return _RepeatedArray1d(self,times)

    def copy(self):
        """
        ``copy()``

        Returns a new ``Array1d`` with a copy of our data.  (The data is
        copied immediately; there's nothing lazy here.)
        """
        s = Array1d(size=len(self))
        self.assign_to(s)
        return s


cdef class Array1d(_BaseArray1d):
    """
    ``Array1d(initial_data=[], size=0, default=0)``

    This is a single dimensional array.

    ``initial_data`` can be used to populate the array.  ``Array1d(range(10))``
    works as you would expect :)

    ``size`` is the initial size of the array.  (Unless the length of
    ``initial_data`` is bigger, in which case it is used.)

    ``default`` is the default value for the array items.

    Note that you can use both ``initial_data`` and ``size`` at the same time.
    If ``size`` larger than the length of ``initial_data``, the rest of the
    array will be filled with ``default``.
    ``Array1d(range(3), size=8, default=6)`` would result in
    ``[0, 1, 2, 6, 6, 6, 6, 6]``.
    """
    cdef float _default
    def __init__(self, initial_data=[], size=0, default=0):
        _BaseArray1d.__init__(self, data_owner=self)
        self._stride = 1
        self._is_assignable = True

        self._default = default

        size = max(len(initial_data), size)
        self.set_size(size)

        cdef int i, initial_len
        initial_len = len(initial_data)
        for i from 0 <= i < initial_len:
            self[i] = initial_data[i]
        if self._default:
            for i from initial_len <= i < size:
                self[i] = self._default

cdef class OffsetArray(_BaseArray1d):
    """
    An array that accesses it's data from an offset inside of another array.
    """
    cdef int _offset
    def __init__(self, _BaseArray array not None, int offset):
        self._offset = offset
        _BaseArray.__init__(self, data_owner=array)
        self._is_assignable = True

    cdef void _sync_data_ptr(self):
        if not self._is_data_owner:
            self.data_owner._sync_data_ptr()
            self._data = self.data_owner._data + self._offset
            self._count = self.data_owner._count


# TODO ItemInfo has no knowledge of this!
cdef class OffsetUByteArray(_BaseArray1d):
    """
    An array that accesses it's data from an offset inside of another array.
    """
    cdef unsigned char * _uchar_data
    cdef int _uchar_stride
    cdef int _offset, _uchar_offset
    def __init__(self, _BaseArray array not None, int offset,
            int uchar_offset):
        self._offset = offset
        self._uchar_offset = uchar_offset
        self._uchar_stride = array._stride * sizeof(float)
        _BaseArray.__init__(self, data_owner=array)
        self._is_assignable = True

    cdef void _sync_data_ptr(self):
        if not self._is_data_owner:
            self._count = self.data_owner._count
            self._data = self.data_owner._data + self._offset
            self._uchar_data = (<unsigned char*>self._data) + self._uchar_offset

    cdef float _getitem(self, int index):
        return (<float>(self._uchar_data[index*self._uchar_stride]))/255

    cdef void _setitem(self, int index, float value):
        if value > 1:
            value = 1
        if value < 0:
            value = 0
        self._uchar_data[index*self._uchar_stride] = \
                <unsigned char>(value*255)


cdef class _RepeatedArray1d(_BaseArray1d):
    cdef int _times
    def __init__(self, data_owner, int times):
        self._times = times
        _BaseArray1d.__init__(self, data_owner=data_owner)
        self._is_assignable = self.data_owner._is_assignable

    cdef void _sync_data_ptr(self):
       if not self._is_data_owner:
           self.data_owner._sync_data_ptr()
           self._data = self.data_owner._data
           self._count = self.data_owner._count*self._times

    cdef int _convert_index(self, int raw):
        return raw%self.data_owner._count

cdef class _StretchedArray1d(_BaseArray1d):
    cdef int _times
    def __init__(self, data_owner, int times):
        self._times = times
        _BaseArray1d.__init__(self, data_owner=data_owner)
        self._is_assignable = self.data_owner._is_assignable

    cdef void _sync_data_ptr(self):
       if not self._is_data_owner:
           self.data_owner._sync_data_ptr()
           self._data = self.data_owner._data
           self._count = self.data_owner._count*self._times

    cdef int _convert_index(self, int raw):
        return raw/self._times


#FIXME This class needs to work with OffsetUByteArray!
cdef class ItemInfo:
    """
    Handles accessing data for a single item in an array.
    """

    cdef Array2d array
    cdef int index

    def __init__(self, Array2d array not None, int index):
        self.array = array
        self.index = index

    def __setattr__(self, name, float value):
        if name not in self.array._attribute_arrays:
            raise AttributeError
        self.array._attribute_arrays[name][self.index] = value

    def __getattr__(self, name):
        if name not in self.array._attribute_arrays:
            raise AttributeError
        return self.array._attribute_arrays[name][self.index]

    def __getitem__(self, int index):
        # This could be optimized...
        return self.array._column_arrays[index][self.index]

    def __setitem__(self, int index, float value):
        self.array._column_arrays[index][self.index] = value


    def _update(self, new_data):
        cdef int i, length, start_offset
        length = len(new_data)
        if self.index >= len(self.array):
            raise IndexError
        if length > len(self.array._column_arrays):
            raise ValueError
        for i from 0 <= i < length:
            self.array._column_arrays[i][self.index] = new_data[i]

    def __len__(self):
        return len(self.array._column_arrays)


ctypedef float (array_op2_f)(float arg1, float arg2)


cdef class _ArrayOp2:
    cdef array_op2_f * operation
    cdef object arg1, arg2
    def __init__(self, arg1, arg2):
        if isinstance(arg1, _ArrayOp2):
            self.arg1 = arg1.copy()
        else:
            self.arg1 = arg1
        if isinstance(arg2, _ArrayOp2):
            self.arg2 = arg2.copy()
        else:
            self.arg2 = arg2
    def assign_to(self, _BaseArray target):
        if isinstance(self.arg1, _BaseArray) and \
                isinstance(self.arg2, _BaseArray):
            _do_op2_a_a(self.operation, 0, len(target), target,
                    self.arg1, self.arg2)
        elif isinstance(self.arg1, _BaseArray):
            _do_op2_a_f(self.operation, 0, len(target), target,
                    self.arg1, float(self.arg2))
        elif isinstance(self.arg2, _BaseArray):
            _do_op2_f_a(self.operation, 0, len(target), target,
                    float(self.arg1), self.arg2)
        else:
            raise RuntimeError

    def __len__(self):
        try:
            len1 = len(self.arg1)
        except TypeError:
            len1 = None
        try:
            len2 = len(self.arg2)
        except TypeError:
            len2 = None
        if len1 is not None and len2 is not None and len1 != len2:
            raise RuntimeError
        return max(len1, len2)

    def copy(self):
        s = Array1d(size=len(self))
        self.assign_to(s)
        return s

    def __iter__(self):
        return iter(self.copy()) # FIXME actually iterate!

cdef class ArrayOpAdd(_ArrayOp2):
    def __init__(self, arg1, arg2):
        self.operation = op2_add
        _ArrayOp2.__init__(self, arg1, arg2)

cdef class ArrayOpSub(_ArrayOp2):
    def __init__(self, arg1, arg2):
        self.operation = op2_sub
        _ArrayOp2.__init__(self, arg1, arg2)

cdef class ArrayOpMul(_ArrayOp2):
    def __init__(self, arg1, arg2):
        self.operation = op2_mul
        _ArrayOp2.__init__(self, arg1, arg2)

cdef class ArrayOpDiv(_ArrayOp2):
    def __init__(self, arg1, arg2):
        self.operation = op2_div
        _ArrayOp2.__init__(self, arg1, arg2)

cdef class ArrayOpMod(_ArrayOp2):
    def __init__(self, arg1, arg2):
        self.operation = op2_mod
        _ArrayOp2.__init__(self, arg1, arg2)

cdef class ArrayOpMin(_ArrayOp2):
    def __init__(self, arg1, arg2):
        self.operation = op2_min
        _ArrayOp2.__init__(self, arg1, arg2)

cdef class ArrayOpMax(_ArrayOp2):
    def __init__(self, arg1, arg2):
        self.operation = op2_max
        _ArrayOp2.__init__(self, arg1, arg2)

def array_max(a, b):
    return ArrayOpMax(a, b)


cdef _do_op2_a_a(array_op2_f * operation, int start, int end,
        _BaseArray result,
        _BaseArray arg1, _BaseArray arg2):
    cdef int i
    arg1._sync_data_ptr()
    arg2._sync_data_ptr()
    for i from start <= i < end:
        result._data[i*result._stride] = operation(
                arg1._getitem(i),
                arg2._getitem(i))

cdef _do_op2_a_f(array_op2_f * operation, int start, int end,
        _BaseArray result,
        _BaseArray arg1, float arg2):
    cdef int i
    arg1._sync_data_ptr()
    for i from start <= i < end:
        result._data[i*result._stride] = operation(
                arg1._getitem(i),
                arg2)

cdef _do_op2_f_a(array_op2_f * operation, int start, int end,
        _BaseArray result,
        float arg1, _BaseArray arg2):
    cdef int i
    arg2._sync_data_ptr()
    for i from start <= i < end:
        result._data[i*result._stride] = operation(
                arg1,
                arg2._getitem(i))

cdef float op2_add(float arg1, float arg2):
        return arg1 + arg2

cdef float op2_sub(float arg1, float arg2):
        return arg1 - arg2

cdef float op2_mul(float arg1, float arg2):
        return arg1 * arg2

cdef float op2_div(float arg1, float arg2):
        return arg1 / arg2

cdef float op2_mod(float arg1, float arg2):
        return fmodf(arg1, arg2)

cdef float op2_min(float arg1, float arg2):
        if arg1 < arg2:
            return arg1
        else:
            return arg2

cdef float op2_max(float arg1, float arg2):
        if arg1 > arg2:
            return arg1
        else:
            return arg2

