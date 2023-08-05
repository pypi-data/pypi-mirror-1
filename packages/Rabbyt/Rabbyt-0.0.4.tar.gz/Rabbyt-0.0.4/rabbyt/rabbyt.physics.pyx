
from dynamicvalues cimport DV, DVConst

from rabbyt.dynamicvalues import to_DV

import weakref

cdef class Basic1(DV):
    """
    Basic1

    Provides basic physics (position, velocity, and acceleration,) in a single
    dimention.

    Basic1 instances can be used as dynamic values, so you can do this for
    example:

    sprite.y = Basic1(10, a=-9.81)

    (The sprite will start at a height of ten, then fall with an acceleration
    of -9.81 world units per second.)
    """
    cdef object __weakref__

    cdef float _p, _v
    cdef DV _a

    def __new__(self, *args, **kwargs):
        self._a = DVConst(0.0)

    def __init__(self, p=0, v=0, a=0):
        """
        Basic1(p=0, v=0, a=0)

        Uppon creation, a Basic1 instance will automatically add itself to the
        global update manager.  This frees you from having to keep track of
        it yourself.  Just use rabbyt.physics.update(dt) to update everything.
        """
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

        This property accepts dynamic values.  For example, if you want to ramp
        up acceleration:

        basic_physics.a = rabbyt.lerp(0,100, dt=1000)
        """
        def __get__(self):
            return self._a
        def __set__(self, a):
            self._a = to_DV(a)

    def update(self, dt):
        """
        Update the state by timestep dt.

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
    Basic2

    This is a convenience class for using to Basic1 instances to simulate
    physics in two dimentions.

    Using item access will return the individual Basic1 instances, so this would
    work fine:

    sprite.xy = Basic2((0,10), axy=(0,-9.81))

    You can set the positions, velocities, and accelerations for x and y with
    the properties x, y, vx, vy, ax, and ay.

    You can also assign/retrieve two value at once with xy, vxy, or axy.

    Any of these properties can be passed to __init__() as keyword arguments.
    """
    cdef object __weakref__

    cdef Basic1 _x, _y

    def __new__(self, *args, **kwargs):
        self._x = Basic1()
        self._y = Basic1()

    def __init__(self, xy=(0,0), vxy=(0,0), axy=(0,0), **kwargs):
        """
        Basic2(xy=(0,0), vxy=(0,0), axy=(0,0), ...)

        (You can also use the single value properties as keyword arguments, if
        you prefer.)

        Basic2 instances are not automatically added to
        rabbyt.physics.default_update_manager, but the individual Basic1
        instances used for each dimention are.  (Added the Basic2 instance too
        would result in the Basic1 instances being updated twice!)
        """
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


class UpdateManager:
    """
    UpdateManager

    This is a small helper class for keeping track of physics drivers that need
    updated.

    All physics drivers are stored as weakrefs, so you don't need to worry about
    removing them.

    There is a global update manager at rabbyt.physics.default_update_manager.
    All physics drivers are automatically added to it.
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
        update(dt)

        Update the physics drivers by timestep dt.
        """
        for u in self.updateables:
            u().update(dt)

default_update_manager = UpdateManager()
update = default_update_manager.update
