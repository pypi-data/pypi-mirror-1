#!/usr/bin/env python
from distutils.core import Extension, setup
import os

__revision__ = "$Id: setup.py 87 2006-03-12 20:00:13Z const $"

NAME = "LSystem2"
DESCRIPTION = """\
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
    sources = [os.path.join(NAME, "Quaternion.c")],
    )

setup(
    name = NAME,
    version = "1.6",
    author = "Constantin Baranov",
    author_email = "const@tltsu.ru",
    url = "http://home.tltsu.ru/~const/",
    download_url ="http://home.tltsu.ru/svn/const/pub/%s/" % NAME,
    license = "PSF",
    platforms = "posix",
    description = "LSystem for Python",
    long_description = DESCRIPTION,
    classifiers = classifiers,
    packages = [NAME],
    ext_package = NAME,
    ext_modules = [Quaternion],
    )
