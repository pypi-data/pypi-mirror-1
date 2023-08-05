from setuptools import setup, find_packages
from setuptools.extension import Extension
import re

import sys, os

def replace_suffix(path, new_suffix):
    return os.path.splitext(path)[0] + new_suffix


have_pyrex = False
try:
    import Pyrex.Compiler.Version
    have_pyrex = True
except ImportError:
    print "Could not import Pyrex.  C files will not be updated."

# <hack type="ugly">
if have_pyrex:
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



long_description = open("README").read()
#+ """

#Changelog
#=========

#""" + open("CHANGELOG").read()

if sys.platform == "win32":
    libraries = []
else:
    libraries = ['m']

setup(
    name = 'StructArray',
    version = "0.1",
    author = "Matthew Marshall",
    author_email = "matthew@matthewmarshall.org",
    description = "Fast operations on arrays of structured data.",
    license = "MIT",
    url="http://matthewmarshall.org/projects/structarray/",
    long_description=long_description,

    packages = find_packages(),
    include_package_data = True,
    exclude_package_data = {'':['README', 'examples', 'docs', '*.c', '*.h',
            '*.pyx', '*.pxd']},

    ext_modules=[
        Extension("structarray", ["structarray.pyx"],
            libraries=libraries),
    ],
)
