from setuptools import setup, find_packages
from setuptools.extension import Extension
from Pyrex.Distutils import build_ext

setup(
    name = 'Rabbyt',
    version = "0.0.2",
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
            libraries=['GL', 'GLU', 'm'],
            extra_compile_args=['-O3']),
        Extension("rabbyt.vertexarrays", ["rabbyt/rabbyt.vertexarrays.pyx"],
            libraries=['GL'], extra_compile_args=['-O3']),
        Extension("rabbyt.collisions", ["rabbyt/rabbyt.collisions.pyx"],
            libraries=['m'], extra_compile_args=['-O3']),
    ],
    cmdclass = {'build_ext': build_ext}
)
