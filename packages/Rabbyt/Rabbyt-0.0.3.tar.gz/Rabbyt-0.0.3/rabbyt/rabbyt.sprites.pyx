
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


from dynamicvalues cimport DV, DVConst

from rabbyt.dynamicvalues import to_DV

cdef float pi, pi_over_180
pi = 3.1415926535897931
pi_over_180 = pi / 180.0

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

    cdef DV _r
    cdef DV _g
    cdef DV _b
    cdef DV _a

    cdef DV _x
    cdef DV _y

    cdef DV _u
    cdef DV _v

    cdef DV _rot
    cdef DV _scale

    cdef int _tex_id

    cdef float _bounding_radius

    def __new__(self, *args, **kwargs):
        # We assign these in __new__ to avoid segfaults from the properties
        # being read before assigned for the first time.
        self._r = DVConst(1)
        self._g = DVConst(1)
        self._b = DVConst(1)
        self._a = DVConst(1)

        self._x = DVConst(0)
        self._y = DVConst(0)
        self._u = DVConst(0)
        self._v = DVConst(0)

        self._rot = DVConst(0)
        self._scale = DVConst(1)

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
            self._x = to_DV(p[0])
            self._y = to_DV(p[1])

    property x:
        def __get__(self):
            return self._x.g()
        def __set__(self, x):
            self._x = to_DV(x)

    property y:
        def __get__(self):
            return self._y.g()
        def __set__(self, y):
            self._y = to_DV(y)

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
            self._u = to_DV(p[0])
            self._v = to_DV(p[1])

    property u:
        def __get__(self):
            return self._u.g()
        def __set__(self, u):
            self._u = to_DV(u)

    property v:
        def __get__(self):
            return self._v.g()
        def __set__(self, v):
            self._v = to_DV(v)

    property rgb:
        def __get__(self):
            return (self._r.g(), self._g.g(), self._b.g())
        def __set__(self, c):
            cdef int i
            self._r = to_DV(c[0])
            self._g = to_DV(c[1])
            self._b = to_DV(c[2])

    property rgba:
        def __get__(self):
            return (self._r.g(), self._g.g(), self._b.g(), self._a.g())
        def __set__(self, c):
            cdef int i
            self._r = to_DV(c[0])
            self._g = to_DV(c[1])
            self._b = to_DV(c[2])
            self._a = to_DV(c[3])

    property red:
        def __get__(self):
            return self._r.g()
        def __set__(self, r):
            self._r = to_DV(r)
    property green:
        def __get__(self):
            return self._g.g()
        def __set__(self, g):
            self._g = to_DV(g)
    property blue:
        def __get__(self):
            return self._b.g()
        def __set__(self, b):
            self._b = to_DV(b)
    property alpha:
        def __get__(self):
            return self._a.g()
        def __set__(self, a):
            self._a = to_DV(a)

    property texture_id:
        def __get__(self):
            return self._tex_id
        def __set__(self, int t):
            self._tex_id = t

    property scale:
        def __get__(self):
            return self._scale.g()
        def __set__(self, s):
            self._scale = to_DV(s)

    property rot:
        def __get__(self):
            return self._rot.g()
        def __set__(self, r):
            self._rot = to_DV(r)

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
                        (self.vertexes[i].x*si - self.vertexes[i].y*co)*s+y)
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
        out.x = (ox*co + oy*si)*s + x
        out.y = (ox*si - oy*co)*s + y
        return out

    def convert_offset(self, offset):
        """
        Converts coordinates relative to this sprite to global coordinates,
        including rotation and scaling.
        """
        cdef Point2d c_offset, out_offset
        c_offset = self._convert_offset(offset[0], offset[1])
        return (c_offset.x, c_offset.y)

    def attrgetter(self, name):
        return _sprite_attr_getters[name](self)



cdef class _DVSpriteAttr_(DV):
    cdef Sprite sprite
    def __init__(self, Sprite sprite not None):
        self.sprite = sprite

cdef class _DVSpriteAttr_x(_DVSpriteAttr_):
    cdef float g(self):
        return self.sprite._x.g()

cdef class _DVSpriteAttr_y(_DVSpriteAttr_):
    cdef float g(self):
        return self.sprite._y.g()

cdef class _DVSpriteAttr_u(_DVSpriteAttr_):
    cdef float g(self):
        return self.sprite._u.g()

cdef class _DVSpriteAttr_v(_DVSpriteAttr_):
    cdef float g(self):
        return self.sprite._v.g()

cdef class _DVSpriteAttr_rot(_DVSpriteAttr_):
    cdef float g(self):
        return self.sprite._rot.g()

cdef class _DVSpriteAttr_scale(_DVSpriteAttr_):
    cdef float g(self):
        return self.sprite._scale.g()

cdef class _DVSpriteAttr_red(_DVSpriteAttr_):
    cdef float g(self):
        return self.sprite._red.g()

cdef class _DVSpriteAttr_green(_DVSpriteAttr_):
    cdef float g(self):
        return self.sprite._green.g()

cdef class _DVSpriteAttr_blue(_DVSpriteAttr_):
    cdef float g(self):
        return self.sprite._blue.g()

cdef class _DVSpriteAttr_alpha(_DVSpriteAttr_):
    cdef float g(self):
        return self.sprite._alpha.g()

_sprite_attr_getters = dict(
    x=_DVSpriteAttr_x,
    y=_DVSpriteAttr_y,
    u=_DVSpriteAttr_u,
    v=_DVSpriteAttr_v,
    rot=_DVSpriteAttr_rot,
    scale=_DVSpriteAttr_scale,
    red=_DVSpriteAttr_red,
    green=_DVSpriteAttr_green,
    blue=_DVSpriteAttr_blue,
    alpha=_DVSpriteAttr_alpha)

