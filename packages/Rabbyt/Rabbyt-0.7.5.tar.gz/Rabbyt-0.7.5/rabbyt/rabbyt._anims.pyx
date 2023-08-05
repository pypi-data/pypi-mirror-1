"""

This module provides the compiled Anim classes.  Everything is imported into
the rabbyt.anims module, and should be accessed from there.

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

__author__ = "Matthew Marshall <matthew@matthewmarshall.org>"


cdef extern from "math.h":
    cdef float fmodf(float x, float y)
    cdef float cosf(float x)
    cdef float sinf(float x)
    cdef float sqrtf(float x)
    cdef float expf(float x)
    cdef float fabsf(float x)
    cdef float M_PI

cdef float time

def set_time(float t):
    """
    ``set_time(t)``

    Sets the time that ``get_time()`` should return.

    If you are using any time based animations, (such as ``lerp()``,)
    you should call this function every frame.

    For example, if you are using pygame you can do this::

        rabbyt.set_time(pygame.time.get_ticks())

    Using this function should make it easier to implement a pause feature.

    Note that rabbyt makes no assumption about the unit that the time is in.
    You can use milliseconds or seconds or even something else.  It's up to
    you.
    """
    global time
    time = t

def get_time():
    """
    ``get_time()``

    Gets the time that was last set by ``set_time()``
    """
    global time
    return time

def add_time(float t):
    """
    ``add_time(t)``

    Adds ``t`` to the ... time ... (Is it just me or does that sound dorky?)

    This is really just a short cut that does this:

        .. sourcecode:: python

            set_time(get_time() + t)

    The new time is returned.
    """
    global time
    time = time + t
    return time

cdef float _get_time():
    return time


cdef class Anim:
    """
    ``Anim()``

    This is the base class for anims.  It shouldn't be instanced directly.

    Performing arithmatic operations on an anim will result in a new anim that
    will allways be up to date.
    """
    cdef float g(self):
        return 0.0

    def get(self):
        """
        ``get() -> float``

        Gets the value.
        """
        return self.g()

    def __add__(self, other):
        if not isinstance(self, Anim):
            self, other = other, self
        if isinstance(other, (int, long, float)):
            return AnimAddStatic(self, other)
        else:
            return AnimAdd(self, other)

    def __sub__(self, other):
        if isinstance(self, Anim) and isinstance(other, (int, long, float)):
            return AnimAddStatic(self, -other)
        else:
            return AnimSub(self, other)

    def __mul__(self, other):
        return AnimMul(self, other)

    def __div__(self, other):
        return AnimDiv(self, other)


cdef class AnimConst(Anim):
    """
    ``AnimConst(value)``

    An anim that isn't animated.

    This is mostly here so that constant values can be used with the same
    interface as Anim.
    """
    cdef float v

    def __init__(self, float v):
        self.v = v

    cdef float g(self):
        return self.v

cdef float extend_t(float t, int mode):
    if mode == 1: # constant
        if t < 0:
            t = 0
        elif t > 1:
            t = 1
    elif mode == 2: # extrapolate
        pass
    elif mode == 3: # repeat
        if t >= 1:
            t = t - (<int>t)
        elif t < 0:
            t = 1 + t - (<int>t)
    elif mode == 4: # reverse
        if t < 0:
            t = -t
        if (<int>t) % 2 == 1:
            t = 1 - (t - (<int>t))
        else:
            t = t - (<int>t)
    return t

cdef class AnimLerp(Anim):
    cdef float start
    cdef float end
    cdef float startt
    cdef float endt
    cdef int extend
    cdef float one_over_dt

    def __init__(self, float start, float end, float startt, float endt,
            int extend):
        self.start = start
        self.end = end
        self.startt = startt
        self.endt = endt
        self.extend = extend
        self.one_over_dt = 1/<float>(self.endt-self.startt)

    cdef float _interpolate(self, float t):
        return t

    cdef float g(self):
        cdef float t
        t = extend_t((_get_time()-self.startt)*self.one_over_dt, self.extend)
        return (self.end-self.start) * self._interpolate(t) + self.start


cdef class AnimCosine(AnimLerp):
    cdef float _interpolate(self, float t):
        return 1-cosf(t * M_PI/2)

cdef class AnimSine(AnimLerp):
    cdef float _interpolate(self, float t):
        return sinf(t * M_PI/2)

cdef class AnimExponential(AnimLerp):
    cdef float _interpolate(self, float t):
        return (expf(t)-1) / (expf(1)-1)


cdef class AnimStaticCubicBezier(Anim):
    cdef float p0
    cdef float startt, endt
    cdef int extend
    cdef float one_over_dt
    cdef float a, b, c

    def __init__(self, float p0, float p1, float p2, float p3, float startt,
            float endt, int extend):
        self.p0 = p0
        self.startt = startt
        self.endt = endt
        self.extend = extend
        self.one_over_dt = 1/<float>(endt-startt)
        self.c = 3.0 * (p1 - p0)
        self.b = 3.0 * (p2 - p1) - self.c
        self.a = p3 - p0 - self.c - self.b

    cdef float g(self):
        cdef float t, t2, t3
        t = extend_t((_get_time()-self.startt)*self.one_over_dt, self.extend)
        t2 = t * t
        t3 = t2 * t
        return self.a*t3 + self.b*t2 + self.c*t + self.p0

cdef class AnimWrap(Anim):
    """
    ``AnimWrap(bounds, parent, static=True)``

    An anim that returns another anim wrapped within two bounds.

    You might want to use ``rabbyt.wrap()`` instead.

   ``bounds`` is the bounds that the value should be wrapped within.  It can
    be anything supporting item access with a length of at least two.

    ``parent`` is the ``Anim`` that is being wrapped.

    If static is ``True``, ``bounds[0]`` and ``bounds[1]`` are read only once
    and stored as variables in c.  This is much faster, but doesn't work if
    ``bounds`` is an object you wish to mutate.
    """
    cdef Anim parent
    cdef object bounds
    cdef unsigned char is_static
    cdef float s_bounds[2]

    def __init__(self, bounds, parent, static=True):
        if static:
            self.is_static = 1
            self.s_bounds[0] = bounds[0]
            self.s_bounds[1] = bounds[1]
            self.bounds = None
        else:
            self.is_static = 0
            self.bounds = bounds

        self.parent = to_Anim(parent)

    cdef float g(self):
        cdef float p, b1, b2, d
        if self.is_static == 1:
            b1 = self.s_bounds[0]
            b2 = self.s_bounds[1]
        else:
            b1 = self.bounds[0]
            b2 = self.bounds[1]

        p = self.parent.g()

        d = b2 - b1

        p = fmodf(p-fmodf(b1,d), d)
        if p < 0:
            p = p + d

        return p + b1

cdef class AnimAddStatic(Anim):
    cdef float s
    cdef Anim a

    def __init__(self, Anim a not None, float s):
        self.a = a
        self.s = s

    cdef float g(self):
        return self.a.g() + self.s


cdef class _AnimArithmatic(Anim):
    cdef Anim a1, a2

    def __init__(self, a1, a2):
        self.a1 = to_Anim(a1)
        self.a2 = to_Anim(a2)

cdef class AnimAdd(_AnimArithmatic):
    cdef float g(self):
        return self.a1.g() + self.a2.g()

cdef class AnimSub(_AnimArithmatic):
    cdef float g(self):
        return self.a1.g() - self.a2.g()

cdef class AnimMul(_AnimArithmatic):
    cdef float g(self):
        return self.a1.g() * self.a2.g()

cdef class AnimDiv(_AnimArithmatic):
    cdef float g(self):
        return self.a1.g() / self.a2.g()

cdef class AnimPyFunc(Anim):
    """
    ``AnimPyFunc(function, cache=False)``

    An anim that calls a python function, using the returned value.

    function is the callback called to retrieve the value.  It should
    return a float.

    If ``cache`` is ``True``, the result returned by function will be
    cached for as long as the time (as set by ``rabbyt.set_time()``) doesn't
    change. This could provide good speedup if the value is read multiple
    times per frame.
    """
    cdef object function
    cdef int cache_output # would be bool if pyrex allowed it.
    cdef float cache
    cdef float cache_time
    def __init__(self, function, cache=False):
        self.function = function
        self.cache_output = cache

    cdef float g(self):
        if self.cache_output:
            if _get_time() != self.cache_time:
                self.cache = self.function()
                self.cache_time = _get_time()
            return self.cache
        else:
            return self.function()

cdef class AnimProxy(Anim):
    """
    ``AnimProxy(value, cache=False)``

    An anim that simply returns the value of another anim.

    ``value`` is the value that can be returned.  It can be a number, a
    function, or another anim.

    If ``cache`` is True, a cached value will be called when the anim is
    accessed a second time without the global time changing.
    """
    cdef int cache_output
    cdef float cache
    cdef float cache_time
    cdef Anim _value
    def __init__(self, value, cache=False):
        self.cache_output = cache
        self.value = value

    property value:
        """
        The value that this anim will return.

        You can assign another anim here, and it's value will be returned.
        """
        def __get__(self):
            return self._value.g()
        def __set__(self, v):
            self._value = to_Anim(v)
            self.cache_time = 0

    cdef float g(self):
        if not self.cache_output or _get_time() != self.cache_time:
            self.cache = self._value.g()
            self.cache_time = _get_time()
        return self.cache

def to_Anim(v):
    """
    ``to_Anim(value) -> Anim subclass instance``

    This is a convenience function to get ``Anim`` for a value.

    If ``value`` is already an ``Anim``, it is returned directly.

    If ``value`` is callable, it is wrapped in an ``AnimPyFunc``.

    Otherwise, ``value`` is wrapped in an ``AnimConst``.
    """
    cdef Anim dv
    if isinstance(v, Anim):
        dv = v
    elif callable(v):
        dv = AnimPyFunc(v)
    else:
        dv = AnimConst(v)
    return dv

