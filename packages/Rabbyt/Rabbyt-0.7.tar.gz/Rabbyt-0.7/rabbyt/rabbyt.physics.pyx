
from _anims cimport Anim, AnimConst

from rabbyt.anims import to_Anim

import weakref

cdef extern from "math.h":
    cdef float fmodf(float x, float y)
    cdef float cosf(float x)
    cdef float sinf(float x)
    cdef float sqrtf(float x)
    cdef float atan2f(float, float)

cdef float pi, pi_over_180, oneeighty_over_pi
pi = 3.1415926535897931
pi_over_180 = pi / 180.0
oneeighty_over_pi = 180.0 / pi

import warnings

_warning_message = ("The Basic1 and Basic2 classes are deprecated.  If you "
                    "find them useful, drop me an email and we can talk "
                    "about it.")

cdef class Basic1(Anim):
    """
    ``Basic1(p=0, v=0, a=0)``

    Provides basic physics (position, velocity, and acceleration,) in a single
    dimension.

    **I am planning on taking this class out in the next version of rabbyt.  If
    you want it to stay, drop me an email explaining why and I might change my
    mind.**

    Basic1 instances can be used as anims, so you can do this for
    example:

        .. sourcecode:: python

            sprite.y = Basic1(10, a=-9.81)

    (The sprite will start at a height of ten, then fall with an acceleration
    of -9.81 world units per second.)

    Uppon creation, a ``Basic1`` instance will automatically add itself to the
    global update manager.  This frees you from having to keep track of
    it yourself.  Just use ``rabbyt.physics.update(dt)`` to update everything.
    """
    cdef object __weakref__

    cdef float _p, _v
    cdef Anim _a

    def __new__(self, *args, **kwargs):
        self._a = AnimConst(0.0)

    def __init__(self, p=0, v=0, a=0):
        """
        """
        warnings.warn(_warning_message)
        self.p = p
        self.v = v
        self.a = a
        default_update_manager.append(self)

    property p:
        """
        position
        """
        def __get__(self):
            return self._p
        def __set__(self, float p):
            self._p = p

    property v:
        """
        velocity
        """
        def __get__(self):
            return self._v
        def __set__(self, v):
            self._v = v

    property a:
        """
        acceleration

        This property accepts anims.  For example, if you want to ramp
        up acceleration:

            .. sourcecode:: python

                basic_physics.a = rabbyt.lerp(0,100, dt=1000)
        """
        def __get__(self):
            return self._a
        def __set__(self, a):
            self._a = to_Anim(a)

    def update(self, dt):
        """
        ``update(dt)``

        Update the state by timestep ``dt``.

        By convention, I recommend using a timestep measured in seconds, rather
        than in milliseconds.
        """
        self._update(dt)

    cdef void _update(self, float dt):
        # TODO this needs a *real* integrator
        cdef float a, v, f

        v = self._v
        a = self._a.g()
        self._v = v + a * dt
        self._p = self._p + v*dt + .5*a*dt*dt

    cdef float g(self):
        return self._p

cdef class Basic2:
    """
    ``Basic2(xy=(0,0), vxy=(0,0), axy=(0,0), ...)``

    **I am planning on taking this class out in the next version of rabbyt.  If
    you want it to stay, drop me an email explaining why and I might change my
    mind.**

    (You can also use the single value properties as keyword arguments, if
    you prefer.)

    This is a convenience class for using two Basic1 instances to simulate
    physics in two dimensions.

    Using item access will return the individual Basic1 instances, so this would
    work fine:

        .. sourcecode:: python

            sprite.xy = Basic2((0,10), axy=(0,-9.81))

    You can set the positions, velocities, and accelerations for x and y with
    the properties ``x``, ``y``, ``vx``, ``vy``, ``ax``, and ``ay``.

    You can also assign/retrieve two value at once with ``xy``, ``vxy``, or
    ``axy``.

    Any of these properties can be passed to ``__init__()`` as keyword
    arguments.

    ``Basic2`` instances are not automatically added to
    ``rabbyt.physics.default_update_manager``, but the individual ``Basic1``
    instances used for each dimension are.  (Adding the ``Basic2`` instance as
    well would result in the ``Basic1`` instances being updated twice!)
    """
    cdef object __weakref__

    cdef Basic1 _x, _y

    def __new__(self, *args, **kwargs):
        self._x = Basic1()
        self._y = Basic1()

    def __init__(self, xy=(0,0), vxy=(0,0), axy=(0,0), **kwargs):
        warnings.warn(_warning_message)
        self.xy = xy
        self.vxy = vxy
        self.axy = axy
        valid_keys = "x y vx vy ax ay".split()
        for key, value in kwargs.items():
            if key not in valid_keys:
                raise TypeError("Unexpected keyword argument %r" % key)
            setattr(self, key, value)

    property x:
        """x position"""
        def __get__(self):
            return self._x.p
        def __set__(self, x):
            self._x.p = x
    property y:
        """y position"""
        def __get__(self):
            return self._y.p
        def __set__(self, y):
            self._y.p = y
    property vx:
        """x velocity"""
        def __get__(self):
            return self._x.v
        def __set__(self, x):
            self._x.v = x
    property vy:
        """y velocity"""
        def __get__(self):
            return self._y.v
        def __set__(self, y):
            self._y.v = y
    property ax:
        """x acceleration"""
        def __get__(self):
            return self._x.a
        def __set__(self, x):
            self._x.a = x
    property ay:
        """y acceleration"""
        def __get__(self):
            return self._y.a
        def __set__(self, y):
            self._y.a = y

    property xy:
        """x and y positions"""
        def __get__(self):
            return self.x, self.y
        def __set__(self, xy):
            self.x, self.y = xy
    property vxy:
        """x and y velocities"""
        def __get__(self):
            return self.vx, self.vy
        def __set__(self, vxy):
            self.vx, self.vy = vxy
    property axy:
        """x and y accelerations"""
        def __get__(self):
            return self.ax, self.ay
        def __set__(self, axy):
            self.ax, self.ay = axy

    def __len__(self):
        return 2

    def __getitem__(self, i):
        if i == 0:
            return self._x
        else:
            return self._y

    def update(self, dt):
        self._x.update(dt)
        self._y.update(dt)


class UpdateManager(object):
    """
    ``UpdateManager()``

    **I am planning on taking this class out in the next version of rabbyt.  If
    you want it to stay, drop me an email explaining why and I might change my
    mind.**

    This is a small helper class for keeping track of physics drivers that need
    updated.

    All physics drivers are stored as weakrefs, so you don't need to worry about
    removing them.

    There is a global update manager at
    ``rabbyt.physics.default_update_manager``. All physics drivers are
    automatically added to it.
    """
    def __init__(self):
        self.updateables = []

    def append(self, updateable):
        self.updateables.append(weakref.ref(updateable, self.remove_ref))

    def remove_ref(self, reference):
        try:
            self.updateables.remove(reference)
        except ValueError:
            pass

    def update(self, float dt):
        """
        ``update(dt)``

        Update the physics drivers by timestep ``dt``.
        """
        for u in self.updateables:
            u().update(dt)

default_update_manager = UpdateManager()
update = default_update_manager.update

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

chipmonk_body_anims = chipmunk_body_anims

__docs_all__ = ('Basic1 Basic2 UpdateManager update '
                'chipmunk_body_anims').split()
