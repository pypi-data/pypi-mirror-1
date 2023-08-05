#!/usr/bin/env python

"""Setup script for the PyAnnodex module distribution."""

import os
import re
import sys
import string

from distutils.core import setup
from distutils.extension import Extension

VERSION_MAJOR = 0
VERSION_MINOR = 7
VERSION_PATCH = 2
pyannodex_version = str(VERSION_MAJOR) + "." + str(VERSION_MINOR) + "." + str(VERSION_PATCH)

def get_setup():
    data = {}
    r = re.compile(r'(\S+)\s*?=\s*(.+)')
    
    if not os.path.isfile('Setup'):
        print "No 'Setup' file. Perhaps you need to run the configure script."
        sys.exit(1)

    f = open('Setup', 'r')
    
    for line in f.readlines():
        m = r.search(line)
        if not m:
            print "Error in setup file:", line
            sys.exit(1)
        key = m.group(1)
        val = m.group(2)
        data[key] = val
        
    return data

data = get_setup()
annodex_include_dir = data['annodex_include_dir']
annodex_lib_dir = data['annodex_lib_dir']
annodex_libs = string.split(data['annodex_libs'])


defines = [('VERSION_MAJOR', VERSION_MAJOR),
           ('VERSION_MINOR', VERSION_MINOR),
           ('VERSION', '"%s"' % pyannodex_version)]

_annodexmodule = Extension(
    name='_annodex',
    sources=['src/annodexmodule.c', 'src/py_anx.c'],
    define_macros = defines,
    include_dirs=[annodex_include_dir, 'include'],
    library_dirs=[annodex_lib_dir],
    libraries=annodex_libs)

setup (
    name = "pyannodex",
    version = pyannodex_version,
    description = "Python bindings for annodex libraries",
    long_description = """pyannodex provides low-level bindings for the annodex libraries, as well as providing a high-level object oriented interface""",
    author = "Ben Leslie",
    author_email = "benno@benno.id.au",
    platforms = ["POSIX", "MacOS", "Windows"],
    url = "http://www.benno.id.au/code/pyannodex/",
    license = "BSD",
    packages = ["annodex"],
    scripts = ["tools/anxrip.py",
               "tools/anxenc.py",
               "tools/anxinfo.py"],
    package_dir = {"annodex" : "pysrc"},
    ext_package = "annodex",
    ext_modules = [_annodexmodule],
    classifiers = ["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "Operating System :: OS Independent",
                   "Programming Language :: C",
                   "Programming Language :: Python",
                   "Topic :: Multimedia :: Video",
                   "Topic :: Software Development :: Libraries :: Python Modules"]
    )
