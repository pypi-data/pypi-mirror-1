
from rabbyt._anims cimport Anim, AnimConst

from rabbyt.anims import to_Anim

cdef float pi, pi_over_180, oneeighty_over_pi
pi = 3.1415926535897931
pi_over_180 = pi / 180.0
oneeighty_over_pi = 180.0 / pi

ctypedef struct cpVect:
    float x,y

ctypedef struct cpBody:
    float m, m_inv
    float i, i_inv

    cpVect p, v, f, v_bias
    float a, w, t, w_bias
    cpVect rot

cdef class _ChipmunkBodyX(Anim):
    cdef cpBody * body

    cdef float g(self):
        return self.body[0].p.x

cdef class _ChipmunkBodyY(Anim):
    cdef cpBody * body

    cdef float g(self):
        return self.body[0].p.y

cdef class _ChipmunkBodyA(Anim):
    cdef cpBody * body

    cdef float g(self):
        return self.body[0].a*oneeighty_over_pi


def chipmunk_body_anims(long body_addr):
    """
    ``chipmunk_body_anims(body_addr)``

    Provides fast integration with the chipmunk physics library.  Returns
    three anims for x, y, and rotation.

    ``body_addr`` Should be the address of a cpBody structure.  For example,
    if you are using the pymonk wrapper, you can do this:

        .. sourcecode:: python

            anims = chipmunk_body_anims(ctypes.addressof(body.contents))
            sprite.x, sprite.y, sprite.rot = anims

    Note that the anims store an internal pointer to the cpBody structure,
    but not a python reference.  This means that if you read the anims value
    after calling cpBodyDestroy on the body, you will get a segfault.
    """
    cdef _ChipmunkBodyX x
    x = _ChipmunkBodyX()
    x.body = <cpBody*>body_addr
    cdef _ChipmunkBodyY y
    y = _ChipmunkBodyY()
    y.body = <cpBody*>body_addr
    cdef _ChipmunkBodyA a
    a = _ChipmunkBodyA()
    a.body = <cpBody*>body_addr

    return (x,y,a)

__docs_all__ = ['chipmunk_body_anims']
