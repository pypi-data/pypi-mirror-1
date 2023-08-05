cdef class _BaseArray:
    # Should be called at the start of any operation that accesses _data
    cdef void _sync_data_ptr(self)

    cdef float _getitem(self, int index)
    cdef void _setitem(self, int index, float value)
    # The length of _data sould always be _allocated_size*sizeof(float) bytes.
    cdef float * _data
    cdef int _allocated_size # In bytes
    cdef int _count
    cdef int _stride   # Note that stride is in sizeof(float), not bytes!
    cdef int _is_data_owner # If we need to clean up the data.
    cdef _BaseArray data_owner  # Reference to the owner of the data.
    cdef int _is_assignable
    cdef object _dimensions  # a tuple of dimensions