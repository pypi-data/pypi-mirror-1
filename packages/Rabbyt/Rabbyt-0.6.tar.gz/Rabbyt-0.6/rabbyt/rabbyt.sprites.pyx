"""
The most interesting part of this module is probably the ``Sprite`` class.

If you need more specialized rendering, try subclassing from ``BaseSprite``.
"""

__credits__ = (
"""
Copyright (C) 2007  Matthew Marshall

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.

You should have received a copy of the GNU Library General Public
License along with this library; if not, write to the Free
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
""")

__author__ = "Matthew Marshall <matthew@matthewmarshall.org>"

cdef extern from "math.h":
    cdef float fmodf(float x, float y)
    cdef float cosf(float x)
    cdef float sinf(float x)
    cdef float sqrtf(float x)

cdef extern from "GL/gl.h":
    ctypedef float GLfloat
    ctypedef float GLclampf
    ctypedef unsigned int GLenum
    ctypedef unsigned int GLbitfield
    ctypedef int GLint
    ctypedef unsigned int GLuint
    ctypedef int GLsizei
    ctypedef double GLdouble
    ctypedef double GLclampd
    ctypedef void GLvoid

    cdef int GL_SMOOTH
    cdef int GL_COLOR_BUFFER_BIT
    cdef int GL_BLEND
    cdef int GL_SRC_ALPHA
    cdef int GL_ONE_MINUS_SRC_ALPHA
    cdef int GL_TEXTURE_2D
    cdef int GL_QUADS
    cdef int GL_MODELVIEW
    cdef int GL_RGBA
    cdef int GL_RGB
    cdef int GL_NEAREST
    cdef int GL_LINEAR
    cdef int GL_TEXTURE_MAG_FILTER
    cdef int GL_TEXTURE_MIN_FILTER
    cdef int GL_TEXTURE_ENV
    cdef int GL_TEXTURE_ENV_MODE
    cdef int GL_MODULATE
    cdef int GL_LINEAR_MIPMAP_NEAREST
    cdef int GL_UNSIGNED_BYTE
    cdef int GL_PROJECTION
    cdef int GL_FLAT
    cdef int GL_FLOAT
    cdef int GL_POLYGON_SMOOTH

    cdef void glTranslatef(GLfloat x, GLfloat y, GLfloat z)
    cdef void glRotatef(GLfloat angle, GLfloat x, GLfloat y, GLfloat z)
    cdef void glScalef(GLfloat x, GLfloat y, GLfloat z)
    cdef void glEnable(GLenum cap)
    cdef void glDisable(GLenum cap)
    cdef void glClear(GLbitfield mask)
    cdef void glShadeModel(GLenum mode)
    cdef void glClearColor(GLclampf red, GLclampf green, GLclampf blue, GLclampf alpha)
    cdef void glBlendFunc(GLenum sfactor, GLenum dfactor)
    cdef void glBindTexture(GLenum target, GLuint texture)
    cdef void glColor4f(GLfloat red, GLfloat green, GLfloat blue, GLfloat alpha)
    cdef void glBegin(GLenum mode)
    cdef void glTexCoord2f(GLfloat s, GLfloat t)
    cdef void glVertex2f(GLfloat x, GLfloat y)
    cdef void glEnd()
    cdef void glViewport(GLint x, GLint y, GLsizei width, GLsizei height)
    cdef void glOrtho(GLint bottom, GLint left, GLint top, GLint bottom, GLint front, GLint back)
    cdef void glMatrixMode(GLenum mode)
    cdef void glLoadIdentity()
    cdef void glTexParameteri(GLenum target, GLenum pname, GLint param)
    cdef void glTexImage2D(GLenum target, GLint level, GLint internalformat, GLsizei width, GLsizei height, GLint border, GLenum format, GLenum type, GLvoid *pixels)
    cdef void glGenTextures(GLsizei n, GLuint *textures)
    cdef void glDeleteTextures(GLsizei n, GLuint *textures)
    cdef void glTexEnvf(GLenum target, GLenum pname, GLfloat param)
    cdef void glPushMatrix()
    cdef void glPopMatrix()


from anims cimport Anim, AnimConst

from rabbyt.anims import to_Anim

cdef float pi, pi_over_180
pi = 3.1415926535897931
pi_over_180 = pi / 180.0

cdef struct Point2d:
    float x,y

cdef struct float2:
    float a, b

cdef class BaseSprite:
    """
    ``BaseSprite(...)``

    This class provides some basic functionality for sprites:

    * transformations (x, y, rot, scale)
    * color (red, green, blue, alpha)
    * bounding_radius (for collision detection)

    ``BaseSprite`` doesn't render anything itself  You'll want to subclass it
    and override either ``render()`` or ``render_after_transform()``.

    You can pass any of the ``BaseSprite`` properties as keyword arguments.
    (``x``, ``y``, ``xy``, etc.)
    """
    cdef object __weakref__

    cdef Anim _r, _g, _b, _a
    cdef Anim _x, _y
    cdef Anim _rot

    # If _scale_y is None, _scale will be used for both x and y scaling.
    cdef Anim _scale, _scale_y

    cdef float _bounding_radius

    def __new__(self, *args, **kwargs):
        # We assign these in __new__ to avoid segfaults from the properties
        # being read before assigned for the first time.
        self._r = AnimConst(1)
        self._g = AnimConst(1)
        self._b = AnimConst(1)
        self._a = AnimConst(1)

        self._x = AnimConst(0)
        self._y = AnimConst(0)

        self._rot = AnimConst(0)
        self._scale = AnimConst(1)
        self._scale_y = None

    def __init__(self, **kwargs):
        names = "xy x y rgba red green blue alpha scale rot".split()
        for name, value in kwargs.items():
            if name not in names:
                raise TypeError("unexpected keyword argument %r" % name)
            setattr(self, name, value)

    property xy:
        """
        A tuple of the x and y coordinates
        """
        def __get__(self):
            return (self._x.g(), self._y.g())
        def __set__(self, p):
            self._x = to_Anim(p[0])
            self._y = to_Anim(p[1])

    property x:
        """ x coordinate """
        def __get__(self):
            return self._x.g()
        def __set__(self, x):
            self._x = to_Anim(x)

    property y:
        """ y coordinate """
        def __get__(self):
            return self._y.g()
        def __set__(self, y):
            self._y = to_Anim(y)

    property rgb:
        """ red, green, and blue color components """
        def __get__(self):
            return (self.red, self.green, self.blue)
        def __set__(self, c):
            self.red, self.green, self.blue = c

    property rgba:
        """ red, green, blue, and alpha color components """
        def __get__(self):
            return (self.red, self.green, self.blue, self.alpha)
        def __set__(self, c):
            self.red, self.green, self.blue, self.alpha = c

    property red:
        """ red color component """
        def __get__(self):
            return self._r.g()
        def __set__(self, r):
            self._r = to_Anim(r)
    property green:
        """ green color component """
        def __get__(self):
            return self._g.g()
        def __set__(self, g):
            self._g = to_Anim(g)
    property blue:
        """ blue color component """
        def __get__(self):
            return self._b.g()
        def __set__(self, b):
            self._b = to_Anim(b)
    property alpha:
        """ alpha color component """
        def __get__(self):
            return self._a.g()
        def __set__(self, a):
            self._a = to_Anim(a)

    property scale:
        """
        scale

        ``1.0`` is normal size; ``0.5`` is half size, ``2.0`` is double
        size... you get the point.

        You can scale the x and y axises independently by assigning a tuple of
        length two.
        """
        def __get__(self):
            if self._scale_y is not None:
                return (self._scale.g(), self._scale_y.g())
            else:
                return self._scale.g()
        def __set__(self, s):
            try:
                iter(s)
            except:
                self._scale = to_Anim(s)
                self._scale_y = None
            else:
                self._scale = to_Anim(s[0])
                self._scale_y = to_Anim(s[1])

    property rot:
        """ rotation """
        def __get__(self):
            return self._rot.g()
        def __set__(self, r):
            self._rot = to_Anim(r)

    property bounding_radius:
        """
        bounding_radius

        This should be the distance of the farthest point from the center.  It
        can be used for collision detection.
        """
        def __get__(self):
            return self._bounding_radius
        def __set__(self, float r):
            self._bounding_radius = r

    property bounding_radius_squared:
        """
        bounding_radius_squared

        This is just like ``bounding_radius``, only it's squared.  (duh)

        ``bounding_radius`` and ``bounding_radius_squared`` are automatically
        kept in sync with each other.
        """
        def __get__(self):
            return self._bounding_radius * self._bounding_radius
        def __set__(self, float r2):
            self._bounding_radius = sqrtf(r2)


    cdef Point2d _convert_offset(self, float ox, float oy):
        cdef float x, y, sx, sy, r, co, si
        cdef Point2d out
        x = self._x.g()
        y = self._y.g()
        sx = self._scale.g()
        if self._scale_y is None:
            sy = sx
        else:
            sy = self._scale_y.g()
        r = self._rot.g()

        co = cosf(r*pi_over_180)
        si = sinf(r*pi_over_180)
        out.x = (ox*sx*co - oy*sy*si) + x
        out.y = (ox*sx*si + oy*sy*co) + y
        return out

    def convert_offset(self, offset):
        """
        ``convert_offset((x, y)) -> (x, y)``

        Converts coordinates relative to this sprite to global coordinates,
        including rotation and scaling.
        """
        cdef Point2d c_offset, out_offset
        c_offset = self._convert_offset(offset[0], offset[1])
        return (c_offset.x, c_offset.y)

    def attrgetter(self, name):
        """
        ``attrgetter(name)``

        Returns an anim that returns the value of the given attribute name.

        Perhaps this is easiest to see with an example.  The following two lines
        will do the same thing, only the second is much, much faster:

            .. sourcecode:: python

                sprite.x = lambda: other_sprite.x

                sprite.x = other_sprite.attrgetter("x")

        The anim returned by attrgetter is implemented in Pyrex (C) and
        will retrieve the value without doing a python attribute lookup.

        This doesn't work for all attributes -- only ``x``, ``y``, ``scale``,
        ``rot``, ``red``, ``green``, ``blue``, and ``alpha``.  (Subclasses
        might add others.)
        """
        return _base_sprite_attr_getters[name](self)

    def render(self):
        """
        ``render()``

        Renders the sprite.

        By default, this method will transform the OpenGL modelview matrix
        according to ``x``, ``y``, ``scale``, and ``rot``, and call
        ``render_after_transform()``.

        If you want transformations to be handled for you, leave this method and
        override ``render_after_transform()``.  Otherwise, override
        ``render()``.
        """
        cdef float x, y, sx, sy, r

        x = self._x.g()
        y = self._y.g()
        sx = self._scale.g()
        if self._scale_y is None:
            sy = sx
        else:
            sy = self._scale_y.g()
        r = self._rot.g()

        if x != 0 or y != 0 or sx != 1 or sy != 1 or r != 0:
            glPushMatrix()
            try:
                glTranslatef(x, y, 0)
                glRotatef(r,0,0,1)
                glScalef(sx, sy, 1)
                self.render_after_transform()
            finally:
                glPopMatrix()
        else:
            self.render_after_transform()

    def render_after_transform(self):
        """
        ``render_after_transform()``

        This method is called by ``BaseSprite.render()`` after transformations
        have been applied.

        If you don't want to mess with doing transformations yourself, you can
        override this method instead of ``render()``.
        """
        pass



cdef class _AnimBaseSpriteAttr_(Anim):
    cdef BaseSprite sprite
    def __init__(self, BaseSprite sprite not None):
        self.sprite = sprite

cdef class _AnimBaseSpriteAttr_x(_AnimBaseSpriteAttr_):
    cdef float g(self):
        return self.sprite._x.g()

cdef class _AnimBaseSpriteAttr_y(_AnimBaseSpriteAttr_):
    cdef float g(self):
        return self.sprite._y.g()

cdef class _AnimBaseSpriteAttr_rot(_AnimBaseSpriteAttr_):
    cdef float g(self):
        return self.sprite._rot.g()

cdef class _AnimBaseSpriteAttr_scale(_AnimBaseSpriteAttr_):
    cdef float g(self):
        return self.sprite._scale.g()

cdef class _AnimBaseSpriteAttr_red(_AnimBaseSpriteAttr_):
    cdef float g(self):
        return self.sprite._red.g()

cdef class _AnimBaseSpriteAttr_green(_AnimBaseSpriteAttr_):
    cdef float g(self):
        return self.sprite._green.g()

cdef class _AnimBaseSpriteAttr_blue(_AnimBaseSpriteAttr_):
    cdef float g(self):
        return self.sprite._blue.g()

cdef class _AnimBaseSpriteAttr_alpha(_AnimBaseSpriteAttr_):
    cdef float g(self):
        return self.sprite._alpha.g()


_base_sprite_attr_getters = dict(
    x=_AnimBaseSpriteAttr_x,
    y=_AnimBaseSpriteAttr_y,
    rot=_AnimBaseSpriteAttr_rot,
    scale=_AnimBaseSpriteAttr_scale,
    red=_AnimBaseSpriteAttr_red,
    green=_AnimBaseSpriteAttr_green,
    blue=_AnimBaseSpriteAttr_blue,
    alpha=_AnimBaseSpriteAttr_alpha)


cdef class Sprite(BaseSprite):
    """
    ``Sprite(texture=None, shape=None, tex_shape=(0,1,1,0), ...)``

    This class provides a basic, four point, textured sprite.

    All arguments are optional.

    ``texture`` should be either the filename of an image or an OpenGL
    texture id.  If ``shape`` is not given it will default to the
    dimensions of the texture if they are available.  For more information
    on ``shape`` and ``tex_shape`` read the docstrings for ``Sprite.shape``
    and ``Sprite.tex_shape``

    Additionally, you can pass values for most of the properties as keyword
    arguments.  (``x``, ``y``, ``xy``, ``u``, ``v``, ``uv``, etc...)
    """

    cdef Point2d vertexes[4]
    cdef Point2d texcoords[4]

    cdef Anim _u, _v

    cdef int _tex_id

    def __new__(self, *args, **kwargs):
        self._u = AnimConst(0)
        self._v = AnimConst(0)

    def __init__(self, texture=None, shape=None, tex_shape=(0,1,1,0),
            **kwargs):
        from rabbyt._rabbyt import load_texture_file_hook
        if isinstance(texture, basestring):
            self.texture_id, tex_size = load_texture_file_hook(texture)
        elif isinstance(texture, (int, long)):
            self.texture_id = texture
            tex_size = None
        elif texture != None:
            raise ValueError("texture should be either an int or str.")

        if not shape:
            if tex_size:
                w, h = tex_size
                shape = [-w/2, h/2, w/2, -h/2]
            else:
                s = 10.
                shape = [s, s, -s, -s]
        self.shape = shape

        self.tex_shape = tex_shape

        for key in list(kwargs):
            if key in "uv u v left right top bottom".split():
                setattr(self, key, kwargs.pop(key))
        BaseSprite.__init__(self, **kwargs)



    property shape:
        """
        The shape of the sprite.

        This must either be of the form ``[left, top, right, bottom]``, or a
        list of four coordinates, eg. ``[(0,0), (20,0), (20,20), (0,20)]``

        ``[-10, -10, 10, 10]`` is the default.

        When you assign to ``shape``, ``bounding_radius`` is automatically set
        to the distance of the farthest coordinate.
        """
        def __get__(self):
            return ((self.vertexes[0].x, self.vertexes[0].y),
                    (self.vertexes[1].x, self.vertexes[1].y),
                    (self.vertexes[2].x, self.vertexes[2].y),
                    (self.vertexes[3].x, self.vertexes[3].y))
        def __set__(self, s):
            try:
                s[0][0]
            except TypeError:
                l, t, r, b = s
                s = [(l, t), (r, t), (r, b), (l, b)]
            assert len(s) == 4 # Only quads supported now.
            cdef int i
            cdef float d
            for i, v in enumerate(s):
                self.vertexes[i].x = v[0]
                self.vertexes[i].y = v[1]
            self.bounding_radius = 0
            for i from 0 <= i < 4:
                d = self.vertexes[i].x**2 + self.vertexes[i].y**2
                if d > self.bounding_radius_squared:
                    self.bounding_radius_squared = d

    property tex_shape:
        """
        This defines how a texture is mapped onto the sprite.

        Like ``Sprite.shape``, you can give either
        ``[left, top, right, bottom]`` or a list of coordinates.

        The default is ``[0, 1, 1, 0]``, which uses the entire texture.
        """
        def __get__(self):
            return ((self.texcoords[0].x, self.texcoords[0].y),
                    (self.texcoords[1].x, self.texcoords[1].y),
                    (self.texcoords[2].x, self.texcoords[2].y),
                    (self.texcoords[3].x, self.texcoords[3].y))
        def __set__(self, s):
            try:
                s[0][0]
            except TypeError:
                l, t, r, b = s
                s = [(l, t), (r, t), (r, b), (l, b)]
            assert len(s) == 4 # Only quads supported now.
            for i, coord in enumerate(s):
                self.texcoords[i].x = coord[0]
                self.texcoords[i].y = coord[1]


    property u:
        """ u texture offset """
        def __get__(self):
            return self._u.g()
        def __set__(self, u):
            self._u = to_Anim(u)

    property v:
        """ v texture offset """
        def __get__(self):
            return self._v.g()
        def __set__(self, v):
            self._v = to_Anim(v)

    property uv:
        """
        The values of ``u`` and ``v`` are added to ``tex_shape``.  This could
        be useful if you have multiple frames of an animation on a single
        texture.  Set ``tex_shape`` to the shape of a single frame and set
        ``uv``, to select each frame.
        """
        def __get__(self):
            return (self._u.g(), self._v.g())
        def __set__(self, p):
            self._u = to_Anim(p[0])
            self._v = to_Anim(p[1])

    property texture_id:
        """
        ``texture_id`` is a number as returned by ``rabbyt.load_texture()``.
        (But you can use any loaded OpenGL texture.)

        If ``texture_id`` is ``0``, texturing will be disabled for this sprite.
        """
        def __get__(self):
            return self._tex_id
        def __set__(self, int t):
            self._tex_id = t

    def render(self):
        """
        ``render()``

        Renders the sprite onto the screen.

        This method depends on the global OpenGL state.  Keep that in mind if
        things seem to go crazy.
        """
        if self._tex_id != 0:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self._tex_id)
        else:
            glDisable(GL_TEXTURE_2D)
        glColor4f(self._r.g(), self._g.g(), self._b.g(), self._a.g())

        cdef float x, y, u, v, sx, sy, r
        x = self._x.g()
        y = self._y.g()
        u = self._u.g()
        v = self._v.g()
        sx = self._scale.g()
        if self._scale_y is None:
            sy = sx
        else:
            sy = self._scale_y.g()
        r = self._rot.g()

        cdef int i
        cdef float vx, vy, co, si

        glBegin(GL_QUADS)
        if r == 0:
            glTexCoord2f(self.texcoords[0].x+u,self.texcoords[0].y+v)
            glVertex2f(self.vertexes[0].x*sx+x,self.vertexes[0].y*sy+y)
            glTexCoord2f(self.texcoords[1].x+u,self.texcoords[1].y+v)
            glVertex2f(self.vertexes[1].x*sx+x,self.vertexes[1].y*sy+y)
            glTexCoord2f(self.texcoords[2].x+u,self.texcoords[2].y+v)
            glVertex2f(self.vertexes[2].x*sx+x,self.vertexes[2].y*sy+y)
            glTexCoord2f(self.texcoords[3].x+u,self.texcoords[3].y+v)
            glVertex2f(self.vertexes[3].x*sx+x,self.vertexes[3].y*sy+y)
        else:
            r = r * pi_over_180
            co = cosf(r)
            si = sinf(r)
            for i from 0 <= i < 4:
                glTexCoord2f(self.texcoords[i].x+u,self.texcoords[i].y+v)
                vx = self.vertexes[i].x*sx
                vy = self.vertexes[i].y*sy
                glVertex2f((vx*co - vy*si)+x, (vx*si + vy*co)+y)
        glEnd()

    def attrgetter(self, name):
        """
        ``attrgetter(name)``

        Returns an anim that returns the value of the given attribute name.

        (See the docs for ``BaseSprite.attrgetter()`` for more information.)

        Sprite adds support for ``u`` and ``v``, in addition to the attributes
        supported by ``BaseSprite``.
        """
        if name == "u":
            return _AnimSpriteAttr_u(self)
        elif name == "v":
            return _AnimSpriteAttr_v(self)
        else:
            return BaseSprite.attrgetter(self, name)


    cdef float2 _bounds_x(self):
            cdef float2 bounds
            cdef float r, co, si, x, s
            cdef int i
            s = self._scale.g()
            r = self._rot.g() * pi_over_180
            co = cosf(r)
            si = sinf(r)

            for i from 0 <= i < 4:
                x = (self.vertexes[i].x*co - self.vertexes[i].y*si)*s
                if i == 0:
                    bounds.a = x
                    bounds.b = x
                else:
                    if bounds.a > x:
                        bounds.a = x
                    if bounds.b < x:
                        bounds.b = x
            return bounds

    cdef float2 _bounds_y(self):
            cdef float2 bounds
            cdef float r, co, si, y, s
            cdef int i
            if self._scale_y is None:
                s = self._scale.g()
            else:
                s = self._scale_y.g()
            r = self._rot.g() * pi_over_180
            co = cosf(r)
            si = sinf(r)

            for i from 0 <= i < 4:
                y = (self.vertexes[i].x*si + self.vertexes[i].y*co)*s
                if i == 0:
                    bounds.a = y
                    bounds.b = y
                else:
                    if bounds.a > y:
                        bounds.a = y
                    if bounds.b < y:
                        bounds.b = y
            return bounds

    property left:
        """ x coordinate of the left side of the sprite """
        def __get__(self):
            return self._bounds_x().a + self._x.g()
        def __set__(self, x):
            self.x = x - self._bounds_x().a

    property right:
        """ x coordinate of the right side of the sprite """
        def __get__(self):
            return self._bounds_x().b + self._x.g()
        def __set__(self, x):
            self.x = x - self._bounds_x().b

    property bottom:
        """ y coordinate of the bottom of the sprite """
        def __get__(self):
            return self._bounds_y().a + self._y.g()
        def __set__(self, y):
            self.y = y - self._bounds_y().a

    property top:
        """ y coordinate of the top of the sprite """
        def __get__(self):
            return self._bounds_y().b + self._y.g()
        def __set__(self, y):
            self.y = y - self._bounds_y().b


cdef class _AnimSpriteAttr_(Anim):
    cdef BaseSprite sprite
    def __init__(self, Sprite sprite not None):
        self.sprite = sprite

cdef class _AnimSpriteAttr_u(_AnimSpriteAttr_):
    cdef float g(self):
        return self.sprite._u.g()

cdef class _AnimSpriteAttr_v(_AnimSpriteAttr_):
    cdef float g(self):
        return self.sprite._v.g()

__docs_all__ = ('BaseSprite Sprite').split()