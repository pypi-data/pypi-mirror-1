from setuptools import setup, find_packages
from setuptools.extension import Extension

import sys

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

if sys.platform == "win32":
    GL = "opengl32"
    GLU = "glu32"
    compile_args = []
    link_args = []
elif sys.platform == "darwin":
    compile_args=['-O3', '-framework','OpenGL','-I',
            '/System/Library/Frameworks/OpenGL.framework/Headers']
    link_args=['-dynamic','-framework','OpenGL',
            '-L/System/Library/Frameworks/OpenGL.framework/Libraries']
    GL = "GL"
    GLU = "GLU"
else:
    compile_args=['-O3']
    link_args=[]
    GL = "GL"
    GLU = "GLU"

setup(
    name = 'Rabbyt',
    version = "0.0.5",
    author = "Matthew Marshall",
    author_email = "matthew@matthewmarshall.org",
    description = "A fast 2D sprite engine using OpenGL",
    license = "LGPL",
    url="http://matthewmarshall.org/projects/rabbyt/",
    long_description=open("README").read(),

    packages = find_packages(),
    include_package_data = True,
    exclude_package_data = {'':['README', 'examples']},

    ext_modules=[
        Extension("rabbyt._rabbyt", ["rabbyt/rabbyt._rabbyt.pyx"],
            libraries=[GL, GLU, 'm'],
            extra_compile_args=compile_args,
            extra_link_args=link_args),
        Extension("rabbyt.anims", ["rabbyt/rabbyt.anims.pyx"],
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
    ]
)
