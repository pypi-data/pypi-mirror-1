from setuptools import setup, find_packages
from setuptools.extension import Extension as BaseExtension
import re

import sys, os

def replace_suffix(path, new_suffix):
    return os.path.splitext(path)[0] + new_suffix

# If we are going to use pyrex, we need to use at least 0.9.6.3.
have_sufficient_pyrex = False
try:
    import Pyrex.Compiler.Version
    if Pyrex.Compiler.Version.version.split('.') >= ['0','9','6','3']:
        have_sufficient_pyrex = True
    else:
        print "*"*80
        print "Pyrex is older that 0.9.6.3.  C files will not be updated."
        print "*"*80
except ImportError:
    print "Could not import Pyrex.  C files will not be updated."

# <hack type="ugly">
if have_sufficient_pyrex:
    # Setuptools doesn't pass the extension to swig_sources, so until it is
    # fixed we need to do a little hack.
    import Pyrex.Distutils.build_ext
    _old_swig_sources = Pyrex.Distutils.build_ext.swig_sources
    def swig_sources(self, sources, extension=None):
        # swig_sources only uses the extension for looking up the swig_options,
        # so we're fine with passing it a dummy.
        if extension is None:  extension = Extension("dummy", [])
        return _old_swig_sources(self, sources, extension)
    Pyrex.Distutils.build_ext.swig_sources = swig_sources
# </hack>

class Extension(BaseExtension):
    def __init__(self, name, sources, libraries=()):
        if not have_sufficient_pyrex:
            sources = [re.sub("\.pyx$", ".c", s) for s in sources]

        transform = {}
        exclude = []
        compile_args = ["-O3"]
        link_args = []
        if sys.platform == "win32":
            transform = {'GL':'opengl32', 'GLU':'glu32'}
            exclude = ['m']
	    # Bugs tend to show up when using mingw32 with optimizing more
            # than -O1.
	    compile_args = ["-O3", "-fno-strict-aliasing"]

        libraries = [transform.get(l,l) for l in libraries if l not in exclude]


        if sys.platform == "darwin" and "GL" in libraries:
            compile_args.extend(['-fno-common', '-I',
                    '/System/Library/Frameworks/OpenGL.framework/Headers'])
            link_args.extend(['-dynamic',
            '-L/System/Library/Frameworks/OpenGL.framework/Libraries'])

        BaseExtension.__init__(self, name, sources, libraries=libraries,
                extra_compile_args=compile_args, extra_link_args=link_args)


long_description = open("README").read() + """

Changelog
=========

""" + open("CHANGELOG").read()

version = re.search('__version__ = "([0-9\.a-z]+)"',
        open("rabbyt/__init__.py").read()).groups()[0]

setup(
    name = 'Rabbyt',
    version = version,
    author = "Matthew Marshall",
    author_email = "matthew@matthewmarshall.org",
    description = "A fast 2D sprite engine using OpenGL",
    license = "MIT",
    url="http://matthewmarshall.org/projects/rabbyt/",
    long_description=long_description,

    packages = find_packages(),
    include_package_data = True,
    exclude_package_data = {'':['README', 'examples', 'docs'],
            'rabbyt':['*.c', '*.h',  '*.pyx', '*.pxd']},

    ext_modules=[
        Extension("rabbyt._rabbyt", ["rabbyt/rabbyt._rabbyt.pyx"],
            libraries=['GL', 'GLU', 'm']),
        Extension("rabbyt._anims", ["rabbyt/rabbyt._anims.pyx",
                "rabbyt/anim_sys.c"],
            libraries=['GL', 'GLU', 'm']),
        Extension("rabbyt._sprites", ["rabbyt/rabbyt._sprites.pyx"],
            libraries=['GL', 'm']),
        Extension("rabbyt.vertexarrays", ["rabbyt/rabbyt.vertexarrays.pyx"],
            libraries=['GL']),
        Extension("rabbyt.collisions", ["rabbyt/rabbyt.collisions.pyx"],
            libraries=['m']),
        Extension("rabbyt.primitives", ["rabbyt/rabbyt.primitives.pyx"],
            libraries=['GL', 'm']),
    ],
)
