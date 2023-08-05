#!/usr/bin/env python
from distutils.core import Extension, setup

__revision__ = "$Id: setup.py 71 2005-12-04 20:08:21Z const $"

NAME = "LSystem2"
VERSION = "1.5"
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

Quaternion = Extension(
    name = "Quaternion",
    sources = ["Quaternion.c"],
    )

setup(
    name = NAME,
    version = VERSION,
    author = AUTHOR,
    author_email = "const@tltsu.ru",
    url = "http://home.tltsu.ru/~const/",
    download_url ="http://home.tltsu.ru/svn/const/pub/%s/" % NAME,
    license = "PSF",
    platforms = "posix",
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = classifiers,
    packages = [NAME],
    ext_package = NAME,
    ext_modules = [Quaternion],
    )
