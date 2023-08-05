#!/usr/bin/env python
from distutils.core import Extension, setup
import sys

__revision__ = "$Id: setup.py 12 2005-07-10 18:43:27Z const $"

NAME = "LSystem2"
VERSION = "1.2"
AUTHOR = "Constantin Baranov"

DESCRIPTION = "LSystem for Python"
LONG_DESCRIPTION = """\
LSystem2 is a new version of LSystem package, which includes
a fast C implementation of basic processing of vector LSystem
(Lindenmayer's System), and several extra Python modules:
EPS, Tk, GL (visualization support)."""

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Education",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: Python Software Foundation License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: C",
    "Programming Language :: Python",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Scientific/Engineering :: Visualization",
    ]

warn = lambda s: sys.stderr.write("Warning! %s\n" % s)
if sys.version < "2.3":
    warn("Python 2.3 or newer is recommended!")
try:
    import Tkinter
except ImportError:
    warn("Tkinter not found!")
try:
    import OpenGL
    if OpenGL.__version__ < "2":
        warn("OpenGL 2.0 or newer is recommended!")
except ImportError:
    warn("OpenGL not found!")

Complex = Extension(
    name = "Complex",
    sources = ["Complex.c"],
    )

setup(
    name = NAME,
    version = VERSION,
    author = AUTHOR,
    author_email = "const@tltsu.ru",
    url = "http://home.tltsu.ru/~const",
    download_url ="http://home.tltsu.ru/svn/%s/" % NAME,
    license = "PSF",
    platforms = "*",
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = classifiers,
    packages = [NAME],
    ext_package = NAME,
    ext_modules = [Complex],
    )
