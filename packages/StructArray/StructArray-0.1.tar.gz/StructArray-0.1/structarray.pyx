"""
StructArray allows you to perform fast arithmetic operations on
arrays of structured (or unstructured) data.

There are two classes you need to worry about:  ``Array`` and ``StructArray``.

``Array`` does most of the work.  It provides a simple array of numbers.  Any
operation performed on the array will be done on each item in it, blazing
fast.  Multiple arrays of the same length can be
added/subtracted/multiplied/divided together, with the result stored in another
array.

``StructArray`` provides an almost object-oriented approach.  You pass a list
of attribute names and ``StructArray`` creates an ``Array`` for each one.
However, getting an item from the ``StructArray`` returns an object mapping
each array's value to it's attributes, making it easier to work with a single
item.  The data is also interleaved together, making it suitable for use as an
OpenGL vertex array.


Notes on multidimensional arrays:

Multidimensional arrays are mostly just a painsaver for item indexes.
``array[x, y]`` is identical to ``array[x+y*width]``.  If fact, both forms of
are valid for a multidimensional array.  ``len(array)`` always returns the
number of items in the array, not the length in any particular direction.

There is an additional restriction on multidimensional arrays: they cannot be
resized.  (This restriction could be lifted if there is demand.)

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

__version__ = "0.1"

cdef extern from "stdlib.h":
    ctypedef unsigned int size_t
    cdef void *malloc(size_t size)
    cdef void free(void *ptr)
    cdef void *realloc(void *ptr, size_t size)


cdef extern from "Python.h":
    object PyObject_GenericGetAttr(object o, object name)
    int PyObject_GenericSetAttr(object o, object name, object value)


cdef extern from "op_loops.h":
    ctypedef int Operation
    cdef int run_float_float(int length, Operation op,
        float * out,  int stride_o,
        float * in_a, int stride_a,
        float * in_b, int stride_b,)
    cdef int Add, Sub, Mul, Div, Mod, Max, Min


cdef class _BaseArray:

    cdef void _sync_data_ptr(self):
       if not self._is_data_owner:
           self.data_owner._sync_data_ptr()
           self._data = self.data_owner._data
           self._count = self.data_owner._count
           self._dimensions = self.data_owner._dimensions

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

    def __len__(self):
        self._sync_data_ptr()
        return self._count

    def _grow(self, int additional_size, exact):
        cdef int new_size, i
        cdef void * ptr
        self._count = self._count + additional_size
        if exact:
            new_size = self._count
        else:
            new_size = self._allocated_size/sizeof(float) + 1
            while self._count > new_size:
                new_size = new_size * 2
        if new_size*sizeof(float) > self._allocated_size:
            ptr = realloc(self._data,
                    sizeof(float)*self._stride*new_size)
            if ptr == NULL:
                raise RuntimeError("Unable to allocate memory for array!")
            self._data = <float*>ptr
            self._allocated_size = self._stride*new_size

    def set_length(self, length):
        """
        ``set_length(length)``

        Sets the length explicitly.

        This is an alternative to using ``append`` and ``extend``.  (It should
        be a little faster.)
        """
        cdef void * ptr
        if self.data_owner is not self:
            raise RuntimeError("Not data owner")
        if len(self._dimensions) > 1:
            raise ValueError("Cannot resize a multidimensional array")
        if not self._is_resizeable():
            raise ValueError("Cannot resize this array")
        if length > self._count:
            self._grow(length-self._count, True)
            # TODO Give the data some defaults
        elif length < self._count:
            self._count = length
            self._allocated_size = self._stride*length
            ptr = realloc(self._data,
                    sizeof(float)*self._allocated_size)
            if ptr == NULL:
                raise RuntimeError("Error in realloc!")
            self._data = <float*>ptr
        self._dimensions = (self._count,)

    def get_dimensions(self):
        """
        ``get_size()``

        Returns a tuple of this array's dimensional size.

        If it is a single dimension array, a tuple containing the length will
        be returned.
        """
        return self._dimensions

    def _is_resizeable(self):
        return (self is self.data_owner) and (len(self._dimensions) == 1)

    def append(self, item):
        """
        ``append(item)``

        Appends an item to the array.
        """
        if self is not self.data_owner:
            raise RuntimeError("Not data owner")
        if not self._is_resizeable():
            raise ValueError("Cannot resize this array.")
        self._grow(1, False)
        self._dimensions = (self._count,)
        try:
            self[self._count - 1] = item
        except:
            # If there was an error assigning the item, we don't want to leave
            # dead item behind.
            self._count = self._count - 1
            self._dimensions = (self._count,)
            raise

    def extend(self, items):
        """
        ``extend(items)``

        Iterates over ``items``, calling ``append()`` on each one.
        """
        for i in items:
            self.append(i)

    def sanitize_index(self, index):
        """
        ``sanitize_index(index)`` -> sanitized index

        This method takes an index, such as passed to __getitem__, and  returns
        an index that is between 0 and len(self).  (So that it can be used with
        the underlying C array.)  This includes handling negitive and/or
        multidimensional indexes.

        Slices are currently not supported.
        """
        if isinstance(index, (int, long)):
            if index < 0:
                index = index + len(self)
            if index < 0 or index >= len(self):
                raise IndexError("array index out of range")
            else:
                return index
        elif isinstance(index, slice):
            raise NotImplementedError("slicing arrays isn't implemented yet.")
        elif hasattr(index, "__len__") and isinstance(self._dimensions, tuple):
            if len(index) != len(self._dimensions):
                raise IndexError("multidimensional index should have a length "
                        "of %d" % len(self._dimensions))
            else:
                converted_index = 0
                for dim, i in enumerate(index):
                    if i < 0:
                        i = i + self._dimensions[dim]
                    if i < 0 or i >= self._dimensions[dim]:
                        raise IndexError("array index out of range")
                    for j in range(0,dim):
                        i = i * self._dimensions[j]
                    converted_index = converted_index + i
                assert converted_index < len(self)
                return converted_index

    def get_data_addr(self):
        """
        ``get_data_addr()``

        Gets the memory address of the data.

        This, together with ``get_data_stride()``, can be used with PyOpenGL
        or Pyglet for OpenGL vertex arrays.  For example:

        >>> array = StructArray(("x", "y"), size=100, defaults=(0,0))
        >>> glVertexPointer(2, GL_FLOAT,
        ...     array.get_data_stride(),
        ...     array.get_data_addr())
        """
        self._sync_data_ptr()
        return <unsigned long>self._data

    def get_data_stride(self):
        """
        ``get_data_stride()``

        Gets the number of bytes between the begining of each array element.
        """
        self._sync_data_ptr()
        return self._stride*sizeof(float)

cdef class _ItemInfo # Forward declaration

cdef class StructArray(_BaseArray):
    """
    ``StructArray(attributes, [initial_data, swizzles, size, defaults])``

    StructArray provides an array of structred data.

    ``attributes`` the list of attribute names.
    e.g., ``('x', 'y', 'dx', 'dy')``  An ``Array`` will be created for each of
    these.

    ``initial_data`` is a list of tuples to fill the array with.

    ``swizzles`` provides shortcuts for accessing multiple attributes at a
    time.  (This is currently not implemented.)

    ``size`` is the initial length of the array.  If ``size`` is longer than
    ``initial_data``, the remaining items will be filled in by ``defaults``.
    If if ``initial_data`` is longer than ``size``, it's length will be used
    instead.

    If ``size`` is a tuple with more than one item, the array will be
    multidimensional.  See the documentation for the ``structarray`` module
    for more on multidimensional arrays.

    ``defaults`` is a tuple of default values for the items.  (One value
    corresponding to each attribute.)  This is used both for initially creating
    the array, and when ``set_length()`` is called.

    Item access on a ``StructArray`` returns an ``item`` object, which
    has attributes corresponding to the attributes of the ``StructArray``.

    This might make it clearer:

        >>> particles = StructArray(('x', 'y', 'dx', 'dy'), size=10)
        >>> p = particles[1]
        >>> print p
        <item at index 1 (0.0, 0.0, 0.0, 0.0)>
        >>> p.x, p.y = 0, 100
        >>> p.dx, p.dy = 0, 5
        >>> print particles[0]
        <item at index 1 (0.0, 100.0, 0.0, 5.0)>

    Additionally, an array is created for each attribute, allowing you to work
    with the value of that attribute for all of the items:

        >>> print particles.y
        <OffsetArray [0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]>

    (``OffsetArray`` is simply a subclass of ``Array`` that stores it's data
    at an offset inside of another array.  It works just like ``Array``, only
    you can't change the length.)

    Assigning to an attribute will do the 'right thing':

        >>> particles.dx = 6.5
        >>> particles.x += particles.dx*2
        >>> print particles[1]
        <item at index 1 (13.0, 100.0, 6.5, 5.0)>

    You can also assign a tuple to an item:

        >>> particles[2] = (15, 20, 0, 100)
        >>> print particles[2]
        <item at index 2 (15.0, 20.0, 0.0, 100.0)>

    When assigning a tuple, you can ommit some values, leaving them as they are:

        >>> particles[2] = (100, 200)
        >>> print particles[2]
        <item at index 2 (100.0, 200.0, 0.0, 100.0)>
    """
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

        self._dimensions = (0,) # So that set_length works.

        if isinstance(size, (int, long)):
            size = max(len(initial_data), size)
            self.set_length(size)
        elif len(size) == 1:
            size = max(len(initial_data), size[0])
            self.set_length(size)
        else:
            size = tuple(size)
            length = 1
            for i in size:
                length = length * i
            self._grow(length, True)
            self._dimensions = size

        self._attribute_arrays = {}
        self._column_arrays = []
        for i, name in enumerate(self._attributes):
            array = OffsetArray(self, i)
            self._attribute_arrays[name] = array
            self._column_arrays.append(array)

        # TODO swizzles

        cdef initial_len
        initial_len = min(len(initial_data), self._count)
        for i from 0 <= i < initial_len:
            self[i] = initial_data[i]
        for i from initial_len <= i < self._count:
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

    def __getitem__(self, index):
        index = self.sanitize_index(index)
        return _ItemInfo(self, index)

    def __setitem__(self, index, value):
        index = self.sanitize_index(index)
        _ItemInfo(self, index)._update(value)

    def __iter__(self):
        return _StructArrayIter(self)

cdef class _StructArrayIter:
    cdef int index
    cdef StructArray array
    def __init__(self, StructArray array not None):
        self.array = array
    def __iter__(self):
        return self
    def __next__(self):
        if self.index >= self.array._count:
            raise StopIteration
        else:
            self.index = self.index + 1
            return _ItemInfo(self.array, self.index-1)


cdef class Array(_BaseArray):
    """
    ``Array(initial_data=[], size=0, default=0)``

    This is a single dimensional array.

    ``initial_data`` can be used to populate the array.  ``Array(range(10))``
    works as you would expect :)

    ``size`` is the initial size of the array.  (Unless the length of
    ``initial_data`` is bigger, in which case it is used.)  If ``size`` is a
    tuple with more than one item, the array will be multidimensional.  See the
    ``structarray`` module documentation form more on multidimensional arrays.

    ``default`` is the default value for the array items.

    Note that you can use both ``initial_data`` and ``size`` at the same time.
    If ``size`` larger than the length of ``initial_data``, the rest of the
    array will be filled with ``default``.
    ``Array(range(3), size=8, default=6)`` would result in
    ``[0, 1, 2, 6, 6, 6, 6, 6]``.

    (The exception to this is if you are a multidimensional array, in which
    case ``initial_data`` will be truncated to fit, as multidimensional arrays
    cannot currently be resized.)

    ``Array`` supports basic arithmetic operations: addition, subtraction,
    multiplication, division, and modulus.  Each of these operations can be
    performed against a single number or another ``Array`` of the same length.

    Arithmetic operations don't return an ``Array``.  Instead they return an
    array operation object.  The operation will be carried out when you
    assign this object to another array.  (You can also call it's ``copy()``
    method to create a new array.)

    For example::

        >>> arg1 = Array(range(10))
        >>> arg2 = Array(range(10,20))
        >>> arg1 + arg2
        <structarray.ArrayOpAdd object at 0xb7d4d66c>
        >>> (arg1 + arg2).copy()
        <Array [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0]>
        >>> arg1.assign_from(arg1 + arg2)
        >>> print arg1
        <Array [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0]>
    """
    cdef float _default
    def __init__(self, initial_data=[], size=0, default=None):
        _BaseArray.__init__(self, data_owner=self)
        cdef int i, initial_len

        self._stride = 1
        self._is_assignable = True

        self._default = default or 0

        self._dimensions = (0,) # so set_length() works

        if isinstance(size, (int, long)):
            size = max(len(initial_data), size)
            self.set_length(size)
        elif len(size) == 1:
            size = max(len(initial_data), size[0])
            self.set_length(size)
        else:
            size = tuple(size)
            length = 1
            for d in size:
                length = length * d
            self._grow(length, True)
            self._dimensions = size

        initial_len = min(len(initial_data), self._count)
        for i from 0 <= i < initial_len:
            self._data[i] = initial_data[i]
        if default is not None:
            for i from initial_len <= i < self._count:
                self._data[i] = self._default

    cdef void _setitem(self, int index, float value):
        self._data[index*self._stride] = value

    cdef float _getitem(self, int index):
        return self._data[index*self._stride]

    def __setitem__(self, index, float value):
        self._sync_data_ptr()
        if not self._is_assignable:
            raise ValueError("This array is not assignable.")
        index = self.sanitize_index(index)
        self._setitem(index, value)

    def __getitem__(self, index):
        self._sync_data_ptr()
        index = self.sanitize_index(index)
        return self._getitem(index)

    def __add__(self, other):
        return ArrayOpAdd(self, other)

    def __sub__(self, other):
        return ArrayOpSub(self, other)

    def __mul__(self, other):
        return ArrayOpMul(self, other)

    def __div__(self, other):
        return ArrayOpDiv(self, other)

    def __truediv__(self, other):
        return ArrayOpDiv(self, other)

    def __mod__(self, other):
        return ArrayOpMod(self, other)

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

    def __imod__(self, other):
        ArrayOpMod(self, other).assign_to(self)
        return self


    def assign_from(self, source):
        """
        ``assign_from(source)``

        Reassigns our value from another array.

        ``source`` can be another ``Array`` instance, or any iterable of the
        correct length.  It can also me a single number, in which case it will
        be assigned to each item.
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
                self._setitem(i, float(source[i]))

    def assign_to(self, Array target not None):
        """
        ``assign_to(target)``

        Assigns our value *to* another array.

        ``target`` must be another ``Array`` instance.  (Not a ``StructArray``,
        but a ``StructArray`` attribute works fine.)
        """
        self._sync_data_ptr()
        target._sync_data_ptr()
        if not len(target) == len(self):
            raise ValueError("Mismatched lengths")
        if not target._is_assignable:
            raise ValueError("Array is not assignable")
        cdef int i
        cdef float * from_, *to_
        cdef int from_stride, to_stride, count
        from_ = self._data
        from_stride = self._stride
        to_ = target._data
        to_stride = target._stride
        count = target._count
        for i from 0 <= i < count:
            to_[i*to_stride] = from_[i*from_stride]

    def __repr__(self):
        items = []
        for f in self:
            items.append(str(f))
        return "<%s [%s]>" % (self.__class__.__name__, ', '.join(items))

    def stretch(self, int times):
        """
        ``stretch(times)``

        Returns a stretched copy this array.  Each item is
        duplicated ``times`` times.

        For example, ``Array([1,2,3]).stretch(3)`` will return
        ``Array([1,1,1,2,2,2,3,3,3])``.

        This operation is not lazy.
        """
        cdef Array new
        new = Array(size=len(self)*times)
        cdef int i, j, length, stride
        cdef float temp
        cdef float * new_data, *_data
        length = len(self)
        new_data = new._data
        _data = self._data
        stride = self._stride
        
        for i from 0 <= i < length:
            temp = _data[i*stride]
            for j from 0 <= j < times:
                new_data[i*times+j] = temp # _stride will be 1.
        return new

    def repeat(self, int times):
        """
        ``repeat(times)``

        Returns a repeated copy of this array.

        For example, ``Array([1,2,3]).repeat(3)`` will return
        ``Array([1,2,3,1,2,3,1,2,3])``.

        This operation is not lazy.
        """
        cdef int stride, i, j, length
        length = len(self)
        stride = self._stride
        cdef Array new
        new = Array(size=len(self)*times)

        cdef float * new_data, *_data
        new_data = new._data
        _data = self._data

        j = 0
        for i from 0 <= i < length*times:
            new_data[i] = _data[j*stride]
            j = j + 1
            if j == length:
                j = 0
        return new

    def copy(self):
        """
        ``copy()``

        Returns a new ``Array`` with a copy of our data.  (The data is
        copied immediately; there's nothing lazy here.)
        """
        s = Array(size=len(self))
        self.assign_to(s)
        return s

    def __iter__(self):
        return _ArrayIter(self)

cdef class _ArrayIter:
    cdef int index
    cdef Array array
    def __init__(self, Array array not None):
        self.array = array
    def __iter__(self):
        return self
    def __next__(self):
        if self.index >= self.array._count:
            raise StopIteration
        else:
            self.index = self.index + 1
            return self.array._getitem(self.index-1)

cdef class OffsetArray(Array):
    """
    ``OffsetArray(array, offset)``

    An array that accesses it's data from an offset inside of another array.

    This class is used by StructArray for providing arrays of individual
    attributes.  You probably don't want to create instances of it yourself.
    """
    cdef int _offset
    def __init__(self, _BaseArray array not None, int offset):
        self._offset = offset
        _BaseArray.__init__(self, data_owner=array)
        self._is_assignable = True

    cdef void _sync_data_ptr(self):
        Array._sync_data_ptr(self)
        if not self._is_data_owner:
            self._data = self.data_owner._data + self._offset



cdef class _ItemInfo:
    """
    Handles accessing data for a single item in an array.
    """

    cdef StructArray array
    cdef int index

    def __init__(self, StructArray array not None, int index):
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

    def __getitem__(self, index):
        return self.array._column_arrays[index][self.index]

    def __setitem__(self, index, float value):
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

    def __repr__(self):
        return "<item at index %d %r>" % (self.index, tuple(self))

cdef class _ArrayOp2:
    cdef int operation
    cdef object arg1, arg2
    def __init__(self, arg1, arg2):
        assert isinstance(arg1, (_ArrayOp2, _BaseArray, float, long, int))
        assert isinstance(arg2, (_ArrayOp2, _BaseArray, float, long, int))
        self.arg1 = arg1
        self.arg2 = arg2
    def assign_to(self, _BaseArray target):
        """
        ``assign_to(target)``

        Performs the operation, saving the result in ``target``.
        """
        if isinstance(self.arg1, _ArrayOp2):
            arg1 = self.arg1.copy()
        else:
            arg1 = self.arg1
        if isinstance(self.arg2, _ArrayOp2):
            arg2 = self.arg2.copy()
        else:
            arg2 = self.arg2

        if isinstance(arg1, _BaseArray) and \
                isinstance(arg2, _BaseArray):
            _do_op2_a_a(self.operation, 0, len(target), target,
                    arg1, arg2)
        elif isinstance(arg1, _BaseArray):
            _do_op2_a_f(self.operation, 0, len(target), target,
                    arg1, float(arg2))
        elif isinstance(arg2, _BaseArray):
            _do_op2_f_a(self.operation, 0, len(target), target,
                    float(arg1), arg2)
        else:
            raise RuntimeError


    def __len__(self):
        if hasattr(self.arg1, "__len__"):
            len1 = len(self.arg1)
        else:
            len1 = None
        if hasattr(self.arg2, "__len__"):
            len2 = len(self.arg2)
        else:
            len2 = None
        if len1 is not None and len2 is not None and len1 != len2:
            raise RuntimeError
        return max(len1, len2)

    def copy(self):
        """
        ``copy()``

        Creates a new array and saves the result of the operation into it.
        """
        s = Array(size=len(self))
        self.assign_to(s)
        return s

    def __iter__(self):
        return iter(self.copy()) # FIXME actually iterate!

    def __add__(self, other):
        return ArrayOpAdd(self, other)

    def __sub__(self, other):
        return ArrayOpSub(self, other)

    def __mul__(self, other):
        return ArrayOpMul(self, other)

    def __div__(self, other):
        return ArrayOpDiv(self, other)

    def __truediv__(self, other):
        return ArrayOpDiv(self, other)

    def __mod__(self, other):
        return ArrayOpMod(self, other)

cdef class ArrayOpAdd(_ArrayOp2):
    def __init__(self, arg1, arg2):
        self.operation = Add
        _ArrayOp2.__init__(self, arg1, arg2)

cdef class ArrayOpSub(_ArrayOp2):
    def __init__(self, arg1, arg2):
        self.operation = Sub
        _ArrayOp2.__init__(self, arg1, arg2)

cdef class ArrayOpMul(_ArrayOp2):
    def __init__(self, arg1, arg2):
        self.operation = Mul
        _ArrayOp2.__init__(self, arg1, arg2)

cdef class ArrayOpDiv(_ArrayOp2):
    def __init__(self, arg1, arg2):
        self.operation = Div
        _ArrayOp2.__init__(self, arg1, arg2)

cdef class ArrayOpMod(_ArrayOp2):
    def __init__(self, arg1, arg2):
        self.operation = Mod
        _ArrayOp2.__init__(self, arg1, arg2)

cdef class ArrayOpMin(_ArrayOp2):
    def __init__(self, arg1, arg2):
        self.operation = Min
        _ArrayOp2.__init__(self, arg1, arg2)

cdef class ArrayOpMax(_ArrayOp2):
    def __init__(self, arg1, arg2):
        self.operation = Max
        _ArrayOp2.__init__(self, arg1, arg2)

def array_max(a, b):
    """
    ``array_max(a, b)``

    Finds the maximum of each item in ``a`` and ``b``.

    Like the aritmetic operators, this doesn't return a new array, but an
    operation object that you can assign to an array.  (Or call ``.copy()``
    to create a new array)
    """
    return ArrayOpMax(a, b)

def array_min(a, b):
    """
    ``array_max(a, b)``

    Finds the minimum of each item in ``a`` and ``b``.

    Like the aritmetic operators, this doesn't return a new array, but an
    operation object that you can assign to an array.  (Or call ``.copy()``
    to create a new array)
    """
    return ArrayOpMin(a,b)


cdef _do_op2_a_a(int operation, int start, int end,
        _BaseArray result,
        _BaseArray arg1, _BaseArray arg2):
    arg1._sync_data_ptr()
    arg2._sync_data_ptr()
    length = end-start
    run_float_float(length, operation,
        result._data+start*result._stride, result._stride,
        arg1._data+start*result._stride, arg1._stride,
        arg2._data+start*result._stride, arg2._stride,)


cdef _do_op2_a_f(int operation, int start, int end,
        _BaseArray result,
        _BaseArray arg1, float arg2):
    arg1._sync_data_ptr()
    length = end-start
    run_float_float(length, operation,
        result._data+start*result._stride, result._stride,
        arg1._data+start*arg1._stride, arg1._stride,
        &arg2, 0)


cdef _do_op2_f_a(int operation, int start, int end,
        _BaseArray result,
        float arg1, _BaseArray arg2):
    arg2._sync_data_ptr()
    length = end-start
    run_float_float(length, operation,
        result._data+start*result._stride, result._stride,
        &arg1, 0,
        arg2._data+start*arg2._stride, arg2._stride,)


__all__ = ['Array', 'StructArray', 'array_max', 'array_min']
__docs_all__ = __all__
