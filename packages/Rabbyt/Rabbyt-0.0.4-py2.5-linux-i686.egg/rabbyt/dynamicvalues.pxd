
cdef class DV:
    cdef float g(self)

cdef class DVConst(DV):
    cdef float v
