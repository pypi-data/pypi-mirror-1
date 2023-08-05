
cdef class Anim:
    cdef float g(self)

cdef class AnimConst(Anim):
    cdef float v
