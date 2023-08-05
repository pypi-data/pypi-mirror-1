#!/usr/bin/env python
from distutils.core import Extension, setup

__revision__ = "$Id: setup.py 6 2005-07-01 18:53:15Z const $"

NAME = "LSystem2"
VERSION = "1.0"
AUTHOR = "Constantin Baranov"

DESCRIPTION = "LSystem for Python"
LONG_DESCRIPTION = """\
LSystem2 is a new version of LSystem package, which includes
a fast C implementation of basic processing of vector LSystem
(Lindenmayer's System), and several extra Python modules."""

classifiers = [
    "Development Status :: 2 - Pre-Alpha",
    "Intended Audience :: Education",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: Python Software Foundation License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: C",
    "Programming Language :: Python",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Scientific/Engineering :: Visualization",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ],

define_macros = [
    ("VERSION", '"%s"' % VERSION),
    ("AUTHOR", '"%s"' % AUTHOR),
    ]

_LSystem = Extension(
    name = "LSystem2._LSystem",
    sources = ["_LSystem.c"],
    define_macros = define_macros,
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
    ext_modules = [_LSystem],
    )
