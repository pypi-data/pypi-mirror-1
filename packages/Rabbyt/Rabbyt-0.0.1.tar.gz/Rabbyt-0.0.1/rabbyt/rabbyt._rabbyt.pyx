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

cdef extern from "GL/glu.h":
    cdef GLint gluBuild2DMipmaps( GLenum target, GLint internalFormat, GLsizei width, GLsizei height, GLenum format, GLenum type, void *data)


cdef int time

cdef float pi, pi_over_180
pi = 3.1415926535897931
pi_over_180 = pi / 180.0

def set_time(int t):
    """
    Sets the time that rabbyt.get_time() should return.

    If you are using any time based animations, (such as rabbyt.lerp or
    rabbyt.bezier3,) you should call this function every frame.

    For example, if you are using pygame you can do this::

        rabbyt.set_time(pygame.time.get_ticks())

    Using this function should make it easier to implement a pause feature.
    """
    global time
    time = t

def get_time():
    """
    Gets the time that was last set by rabbyt.set_time()
    """
    global time
    return time


load_texture_file_hook = None
def set_load_texture_file_hook(callback):
    """
    This sets the callback that is used to load a texture from a file.  (It is
    called when you give a string for the first argument of Sprite.)

    The default is rabbyt.pygame_load_texture, which will use pygame to load the
    file.  You may write your own callback if you don't want to use pygame.

    The callback should take the filename as a single argument, and return a
    tuple of the form (texture_id, (width, height)).
    """
    global load_texture_file_hook
    load_texture_file_hook = callback

cdef class Anim:
    cdef float g(self):
        return 0.0

    def get(self):
        return self.g()

cdef class AnimConst(Anim):
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
    cdef int startt
    cdef int endt
    cdef int extend
    cdef float one_over_dt

    def __init__(self, float start, float end, int startt, int endt,
            int extend):
        self.start = start
        self.end = end
        self.startt = startt
        self.endt = endt
        self.extend = extend
        self.one_over_dt = 1/<float>(self.endt-self.startt)

    cdef float g(self):
        cdef float t
        t = extend_t((time-self.startt)*self.one_over_dt, self.extend)

        return (self.end-self.start) * t + self.start

cdef class AnimStaticCubicBezier(Anim):
    cdef float p0
    cdef int startt, endt
    cdef int extend
    cdef float one_over_dt
    cdef float a, b, c

    def __init__(self, float p0, float p1, float p2, float p3, int startt,
            int endt, int extend):
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
        t = extend_t((time-self.startt)*self.one_over_dt, self.extend)
        t2 = t * t
        t3 = t2 * t
        return self.a*t3 + self.b*t2 + self.c*t + self.p0

cdef class AnimWrap(Anim):
    cdef Anim parent
    cdef object bounds
    cdef unsigned char is_static
    cdef float s_bounds[2]

    def __init__(self, bounds, parent, static):
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


cdef Anim to_Anim(v):
    cdef Anim mp
    if isinstance(v, Anim):
        mp = v
    else:
        mp = AnimConst(v)
    return mp

cdef struct Point2d:
    float x,y

cdef class Sprite:
    """
    Sprite is the class the does the exciting drawing stuff.

    Sprites have a number of properties to control their appearance.  These are:
    x, y, rot, scale, u, v, red, green, blue, and alpha.  Most of them should
    be pretty obvious.  The only exception would be 'u' and 'v', which are
    simply added to tex_shape.  There are also some shortcut properties to get
    or set multiple values at a time.  These are: xy, uv, rgb, and rgba.  All of
    these properties can be given to Sprite.__init__ as additional keyword
    arguments.
    """

    cdef Point2d vertexes[4]
    cdef Point2d texcoords[4]

    cdef Anim _r
    cdef Anim _g
    cdef Anim _b
    cdef Anim _a

    cdef Anim _x
    cdef Anim _y

    cdef Anim _u
    cdef Anim _v

    cdef Anim _rot
    cdef Anim _scale

    cdef int _tex_id

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
        self._u = AnimConst(0)
        self._v = AnimConst(0)

        self._rot = AnimConst(0)
        self._scale = AnimConst(1)

    def __init__(self, texture=None, shape=None, tex_shape=(0,1,1,0), **kwargs):
        """
        rabbyt.Sprite(texture=None, shape=None, tex_shape=(0,1,1,0), ...)

        All arguments are optional.

        ``texture`` should be either the filename of an image or an OpenGL
        texture id.  If ``shape`` is not given it will default to the
        dimensions of the texture if they are available.  For more information
        on ``shape`` and ``tex_shape`` read the docstrings for ``Sprite.shape``
        and ``Sprite.tex_shape``

        Additionally, you can pass values for most of the properties as keyword
        arguments.  (x, y, xy, u, v, uv, etc...)
        """
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

        names = "xy x y uv u v rgba red green blue alpha scale rot".split()
        for name, value in kwargs.items():
            if name not in names:
                raise TypeError("unexpected keyword argument %r" % name)
            setattr(self, name, value)

    def __hash__(self):
        return id(self)

    property shape:
        """
        The shape of the sprite.

        This must either be of the form [left, top, right, bottom], or a list
        of four coordinates, eg. [(0,0), (20,0), (20,20), (0,20)]

        [-10, -10, 10, 10] is the default.
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

        Like Sprite.shape, you can give either [left, top, right, bottom] or
        a list of coordinates.

        The default is [0, 1, 1, 0], which uses the entire texture.
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

    property xy:
        """
        This is the x and y coordinates of the sprite.

        You can also access the components individually with Sprite.x and
        Sprite.y.
        """
        def __get__(self):
            return (self._x.g(), self._y.g())
        def __set__(self, p):
            self._x = to_Anim(p[0])
            self._y = to_Anim(p[1])

    property x:
        def __get__(self):
            return self._x.g()
        def __set__(self, x):
            self._x = to_Anim(x)

    property y:
        def __get__(self):
            return self._y.g()
        def __set__(self, y):
            self._y = to_Anim(y)

    property uv:
        """
        The values of u and v are added to tex_shape.  This could be useful if
        you have multiple frames of an animation on a single texture.  Set
        tex_shape to the shape of a single frame and set uv, to select each
        frame.
        """
        def __get__(self):
            return (self._u.g(), self._v.g())
        def __set__(self, p):
            self._u = to_Anim(p[0])
            self._v = to_Anim(p[1])

    property u:
        def __get__(self):
            return self._u.g()
        def __set__(self, u):
            self._u = to_Anim(u)

    property v:
        def __get__(self):
            return self._v.g()
        def __set__(self, v):
            self._v = to_Anim(v)

    property rgb:
        def __get__(self):
            return (self._r.g(), self._g.g(), self._b.g())
        def __set__(self, c):
            cdef int i
            self._r = to_Anim(c[0])
            self._g = to_Anim(c[1])
            self._b = to_Anim(c[2])

    property rgba:
        def __get__(self):
            return (self._r.g(), self._g.g(), self._b.g(), self._a.g())
        def __set__(self, c):
            cdef int i
            self._r = to_Anim(c[0])
            self._g = to_Anim(c[1])
            self._b = to_Anim(c[2])
            self._a = to_Anim(c[3])

    property red:
        def __get__(self):
            return self._r.g()
        def __set__(self, r):
            self._r = to_Anim(r)
    property green:
        def __get__(self):
            return self._g.g()
        def __set__(self, g):
            self._g = to_Anim(g)
    property blue:
        def __get__(self):
            return self._b.g()
        def __set__(self, b):
            self._b = to_Anim(b)
    property alpha:
        def __get__(self):
            return self._a.g()
        def __set__(self, a):
            self._a = to_Anim(a)

    property texture_id:
        def __get__(self):
            return self._tex_id
        def __set__(self, int t):
            self._tex_id = t

    property scale:
        def __get__(self):
            return self._scale.g()
        def __set__(self, s):
            self._scale = to_Anim(s)

    property rot:
        def __get__(self):
            return self._rot.g()
        def __set__(self, r):
            self._rot = to_Anim(r)

    property bounding_radius:
        """
        bounding_radius

        This should be the distance of the farthest point from the center.  It
        can be used for collision detection.

        This is set whenever you assign to ``shape``, but you change it later.
        """
        def __get__(self):
            return self._bounding_radius
        def __set__(self, float r):
            self._bounding_radius = r

    property bounding_radius_squared:
        """
        bounding_radius_squared

        This is just like bounding_radius, only it's squared.  (duh)

        bounding_radius and bounding_radius_squared are automatically kept in
        sync with each other.
        """
        def __get__(self):
            return self._bounding_radius * self._bounding_radius
        def __set__(self, float r2):
            self._bounding_radius = sqrtf(r2)

    cdef _update(self, int time, int dt):
        pass

    def render(self):
        """
        Renders the sprite onto the screen.

        This method depends on the global OpenGL state.
        """
        self._render()

    cdef _render(self):
        if self._tex_id != 0:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self._tex_id)
        else:
            glDisable(GL_TEXTURE_2D)
        glColor4f(self._r.g(), self._g.g(), self._b.g(), self._a.g())

        cdef float x, y, u, v, s, r
        x = self._x.g()
        y = self._y.g()
        u = self._u.g()
        v = self._v.g()
        s = self._scale.g()
        r = self._rot.g()

        cdef int i
        cdef float vx, vy, co, si

        glBegin(GL_QUADS)
        if r == 0:
            glTexCoord2f(self.texcoords[0].x+u,self.texcoords[0].y+v)
            glVertex2f(self.vertexes[0].x*s+x,self.vertexes[0].y*s+y)
            glTexCoord2f(self.texcoords[1].x+u,self.texcoords[1].y+v)
            glVertex2f(self.vertexes[1].x*s+x,self.vertexes[1].y*s+y)
            glTexCoord2f(self.texcoords[2].x+u,self.texcoords[2].y+v)
            glVertex2f(self.vertexes[2].x*s+x,self.vertexes[2].y*s+y)
            glTexCoord2f(self.texcoords[3].x+u,self.texcoords[3].y+v)
            glVertex2f(self.vertexes[3].x*s+x,self.vertexes[3].y*s+y)
        else:
            r = r * pi_over_180
            co = cosf(r)
            si = sinf(r)
            for i from 0 <= i < 4:
                glTexCoord2f(self.texcoords[i].x+u,self.texcoords[i].y+v)
                glVertex2f((self.vertexes[i].x*co + self.vertexes[i].y*si)*s+x,
                        (-self.vertexes[i].x*si + self.vertexes[i].y*co)*s+y)
        glEnd()

    def __cmp__(Sprite self, Sprite other):
        cdef float s, o
        s = self._y.g()
        o = other._y.g()
        if s == o:
            return 0
        elif s > o:
            return 1
        else:
            return -1


    cdef Point2d _convert_offset(self, float ox, float oy):
        cdef float x, y, s, r, co, si
        cdef Point2d out
        x = self._x.g()
        y = self._y.g()
        s = self._scale.g()
        r = self._rot.g()

        co = cosf(r*pi_over_180)
        si = sinf(r*pi_over_180)
        out.x = ( ox*co + oy*si)*s + x
        out.y = (-ox*si + oy*co)*s + y
        return out

    def convert_offset(self, offset):
        """
        Converts coordinates relative to this sprite to global coordinates,
        including rotation and scaling.
        """
        cdef Point2d c_offset, out_offset
        c_offset = self._convert_offset(offset[0], offset[1])
        return (c_offset.x, c_offset.y)


def render_unsorted(sprites):
    """
    render_unsorted(sprites)

    Renders a list of sprites.

    Since this function is implemented in Pyrex, it should be a little faster
    than looping through the sprites in Python.
    """
    for s in sprites:
        s.render()


def render_sorted(sprites):
    ss = list(sprites)
    ss.sort()
    render_unsorted(ss)


def set_viewport(viewport, projection=None):
    """
    set_viewport(viewport, [projection])

    Sets how coordinates map to the screen.

    viewport gives the screen coordinates that will be drawn to.  It should
    be in either the form (width, height) or (left, top, right, bottom)

    projection gives the sprite coordinates that will be mapped to the screen
    coordinates given by viewport.  It too should be in one of the two forms
    accepted by viewport.  If projection is not given, it will default to the
    width and height of viewport.  If only the width and height are given,
    (0, 0) will be the center point.
    """
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if len(viewport) == 4:
        l, t, r, b = viewport
    else:
        l, t = 0, 0
        r, b = viewport
    glViewport(l, t, r-l, b-t)

    if projection is not None:
        if len(projection) == 4:
            l, t, r, b = projection
        else:
            w,h = projection
            l, r, t, b = -w/2, w/2, -h/2, h/2
    else:
        w,h = r-l, b-t
        l, r, b, t = -w/2, w/2, -h/2, h/2
    glOrtho(l, r, b, t, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def set_default_attribs():
    """
    set_default_attribs()

    Sets a few of the OpenGL attributes that sprites expect.

    Unless you know what you are doing, you should call this at least once
    before rendering any sprites.  (It is called automatically in
    rabbyt.init_display())
    """
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glEnable(GL_BLEND)
    #glEnable(GL_POLYGON_SMOOTH)


# The following functions were ripped from Simmon Wittber's GFX library:

def load_texture(byte_string, size, type='RGBA', filter=True, mipmap=True):
    """
    Load a texture and return it.
    """
    cdef GLuint textures[1]
    cdef GLuint id
    glGenTextures(1, textures)
    id = textures[0]
    update_texture(id, byte_string, size, type, filter, mipmap)
    return id

def update_texture(texture_id, byte_string, size, type='RGBA', filter=True, mipmap=True):
    """
    Update a texture with a different byte_string.
    """
    cdef char *data
    data = byte_string
    if type == 'RGBA':
        ptype = GL_RGBA
        channels = 4
    elif type == 'RGB':
        ptype = GL_RGB
        channels = 3
    else:
        raise ValueError('type must be "RGBA" or "RGB"')

    if size[0]*size[1]*channels != len(byte_string):
        raise ValueError('byte_string is an unexpected size.')

    filter_type = GL_NEAREST
    if filter: filter_type = GL_LINEAR
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter_type)
    if mipmap:
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST)
        gluBuild2DMipmaps(GL_TEXTURE_2D, channels, size[0], size[1], ptype, GL_UNSIGNED_BYTE, data)
    else:
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter_type)
        glTexImage2D(GL_TEXTURE_2D, 0, ptype, size[0], size[1], 0, ptype, GL_UNSIGNED_BYTE, data)

def unload_texture(texture_id):
    """
    Unload a texture from memory.
    """
    cdef GLuint textures[1]
    textures[0] = texture_id
    glDeleteTextures(1, textures)

def clear(rgba=(0.0,0.0,0.0,1.0)):
    """
    Clear the screen to a background color.
    """
    glClearColor(rgba[0], rgba[1], rgba[2], rgba[3])
    glClear(GL_COLOR_BUFFER_BIT)
