#!/usr/bin/env python
from distutils.core import Extension, setup

__revision__ = "$Id: setup.py 11 2005-07-05 18:33:59Z const $"

NAME = "LSystem2"
VERSION = "1.1"
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

define_macros = [
    ("VERSION", '"%s"' % VERSION),
    ("AUTHOR", '"%s"' % AUTHOR),
    ]

_LSystem = Extension(
    name = "%s._LSystem" % NAME,
    sources = ["_LSystem.c"],
    define_macros = define_macros,
    )

_GL = Extension(
    name = "%s._GL" % NAME,
    sources = ["_GL.c"],
    libraries = ["GL", "GLU", "glut", "X11", "Xi", "Xmu"],
    library_dirs = ["/usr/X11R6/lib"],
    )

setup(
    name = NAME,
    version = VERSION,
    author = AUTHOR,
    author_email = "const@tltsu.ru",
    url = "http://home.tltsu.ru/~const",
    download_url ="http://home.tltsu.ru/svn/%s/" % NAME,
    license = "PSF",
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = classifiers,
    packages = [NAME],
    ext_modules = [_LSystem, _GL],
    )
