from setuptools import setup, find_packages
from setuptools.extension import Extension


import sys

# If we are going to use pyrex, we need to use at least 0.9.5.  Older versions
# cause segfaults with weakrefs!
have_sufficient_pyrex = False
try:
    import Pyrex.Compiler.Version
    if Pyrex.Compiler.Version.version.split('.') >= ['0','9','5']:
        have_sufficient_pyrex = True
except ImportError:
    pass
if not have_sufficient_pyrex:
    # How many hacks would a hack saw hack if a hack saw could saw hacks?
    original__init__ = Extension.__init__
    def __init__(self, *args, **kwargs):
        original__init__(self, *args, **kwargs)
        # If either there is no Pyrex or the Pyrex version is too old, we
        # want to make SURE that the pyrex version isn't used!
        sources = []
        for s in self.sources:
            if s.endswith('.pyx'):
                sources.append(s[:-3]+'c')
            else:
                sources.append(s)
        self.sources = sources
    Extension.__init__ = __init__

if sys.platform == "darwin":
    # On MacOS we need to include from gl.h instead of GL/gl.h, but pyrex
    # doesn't have anything along the lines of conditional compiling.  So,
    # this hack fixes up the c file after it is created.
    from Pyrex.Compiler.Main import CompilationOptions, default_options, compile
    from Pyrex.Distutils import build_ext
    def pyrex_compile(self, source):
        options = CompilationOptions(default_options,
            include_path = self.include_dirs)
        result = compile(source, options)
        if result.num_errors <> 0:
            sys.exit(1)

        if result.c_file:
            source = open(result.c_file).read()
            source = source.replace('#include "GL/gl.h"', '#include "gl.h"')
            source = source.replace('#include "GL/glu.h"', '#include "glu.h"')
            open(result.c_file, "wt").write(source)
    build_ext.pyrex_compile = pyrex_compile
    # This is identical to the original swig_sources, except for that the c
    # file is *not* checked to be newer than the pyx file.  (We need to make
    # sure that the c file is regenerated.)
    def swig_sources (self, sources, extension = None):
        if not self.extensions:
            return

        pyx_sources = []
        pyx_sources = [source for source in sources if source.endswith('.pyx')]
        other_sources = [source for source in sources if not source.endswith('.pyx')]

        suffix = '.c'
        for pyx in pyx_sources:
            if os.path.exists(pyx):
                source = pyx
                target = replace_suffix(source, suffix)
                self.pyrex_compile(source)

        return [replace_suffix(src, suffix) for src in pyx_sources] + other_sources
    build_ext.swig_sources = swig_sources

if sys.platform == "win32":
    GL = "opengl32"
    GLU = "glu32"
    compile_args = []
    link_args = []
elif sys.platform == "darwin":
    compile_args=['-O3', '-fno-common', '-I',
             '/System/Library/Frameworks/OpenGL.framework/Headers']
    link_args=['-dynamic',
            '-L/System/Library/Frameworks/ OpenGL.framework/Libraries']

    GL = "GL"
    GLU = "GLU"
else:
    compile_args=['-O3']
    link_args=[]
    GL = "GL"
    GLU = "GLU"

long_description = open("README").read() + """

Changelog
=========

""" + open("CHANGELOG").read()

setup(
    name = 'Rabbyt',
    version = "0.7",
    author = "Matthew Marshall",
    author_email = "matthew@matthewmarshall.org",
    description = "A fast 2D sprite engine using OpenGL",
    license = "MIT",
    url="http://matthewmarshall.org/projects/rabbyt/",
    long_description=long_description,

    packages = find_packages(),
    include_package_data = True,
    exclude_package_data = {'':['README', 'examples', 'docs'],
            'rabbyt':['*.c', '*.pyx', '*.pxd']},

    ext_modules=[
        Extension("rabbyt._rabbyt", ["rabbyt/rabbyt._rabbyt.pyx"],
            libraries=[GL, GLU, 'm'],
            extra_compile_args=compile_args,
            extra_link_args=link_args),
        Extension("rabbyt._anims", ["rabbyt/rabbyt._anims.pyx"],
            libraries=['m'],
            extra_compile_args=compile_args,
            extra_link_args=link_args),
        Extension("rabbyt.sprites", ["rabbyt/rabbyt.sprites.pyx"],
            libraries=[GL, 'm'],
            extra_compile_args=compile_args,
            extra_link_args=link_args),
        Extension("rabbyt.vertexarrays", ["rabbyt/rabbyt.vertexarrays.pyx"],
            libraries=[GL],
            extra_compile_args=compile_args,
            extra_link_args=link_args),
        Extension("rabbyt.collisions", ["rabbyt/rabbyt.collisions.pyx"],
            libraries=['m'],
            extra_compile_args=compile_args,
            extra_link_args=link_args),
        Extension("rabbyt.physics", ["rabbyt/rabbyt.physics.pyx"],
            libraries=['m'],
            extra_compile_args=compile_args,
            extra_link_args=link_args),
    ],
)
