from setuptools import setup, find_packages
from setuptools.extension import Extension
from Pyrex.Distutils import build_ext
import sys

if sys.platform == "win32":
    GL = "opengl32"
    GLU = "glu32"
    compile_args = []
    link_args = []
elif sys.platform == "darwin":
    compile_args=['-O3', '-framework','OpenGL','-I','/System/Library/Frameworks/OpenGL.framework/Headers']
    link_args=['-dynamic','-framework','OpenGL', '-L/System/Library/Frameworks/OpenGL.framework/Libraries']
    GL = "GL"
    GLU = "GLU"
else:
    compile_args=['-O3']
    link_args=[]
    GL = "GL"
    GLU = "GLU"
    

setup(
    name = 'Rabbyt',
    version = "0.0.4",
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
        Extension("rabbyt.dynamicvalues", ["rabbyt/rabbyt.dynamicvalues.pyx"],
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
    cmdclass = {'build_ext': build_ext}
)
