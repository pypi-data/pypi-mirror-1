#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup


__version__ = "0.6.0"
__license__ = "GPL 3"
__author__ = "Dinu Gherman"
__date__ = "2008-09-26"


# description for Distutils to do its business

long_description = """\
`Svglib` is an experimental library for reading `SVG 
<http://www.w3.org/Graphics/SVG/>`_ files and converting them (to a 
reasonable degree) to other formats using the Open Source `ReportLab 
Toolkit <http://see www.reportlab.org>`_. As a package it reads existing 
SVG files and returns them converted to ReportLab Drawing objects that can 
be used in a variety of ReportLab-related contexts, e.g. as Platypus Flowable  objects or in RML2PDF. As a command-line tool it converts SVG files into PDF  ones. Tests include a vast amount of tests from the `W3C SVG test suite 
<http://www.w3.org/Graphics/SVG/WG/wiki/Test_Suite_Overview>`_.


Features
++++++++

- convert SVG files into ReportLab Graphics Drawing objects
- handle plain or compressed SVG files (.svg and .svgz)
- allow patterns for output files on command-line
- install a Python package named ``svglib``
- install a Python command-line script named ``svg2pdf``
- provide a Unittest test suite
- access some standard W3C SVG tests available online
- access some Wikipedia SVG samples available online


Examples
++++++++

You can use `svglib` as a Python package e.g. like in the following
interactive Python session::

    >>> from svglib.svglib import svg2rlg
    >>> from reportlab.graphics import renderPDF
    >>>
    >>> drawing = svg2rlg("file.svg")
    >>> renderPDF.drawToFile(drawing, "file.pdf")

In addition a script named ``svg2pdf`` can be used more easily from 
the system command-line like this (you can see more examples when 
typing ``svg2pdf -h``)::

    $ svg2pdf file1.svg file2.svgz
    $ svg2pdf -o "%(basename)s.pdf" /path/file[12].svgz?
"""


# see http://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX",
    "Operating System :: Microsoft :: Windows",
    "Natural Language :: English",
    "Programming Language :: Python",
    "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    "Topic :: Documentation",
    "Topic :: Utilities",
    "Topic :: Printing",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Text Processing :: Markup :: XML",
]

baseURL = "http://www.dinu-gherman.net/"

setup(
    name = "svglib",
    version = __version__,
    description = "An experimental library for reading and converting SVG.",
    long_description = long_description,
    date = __date__,
    author = __author__,
    author_email = "@".join(["gherman", "darwin.in-berlin.de"]),
    maintainer = __author__,
    maintainer_email = "@".join(["gherman", "darwin.in-berlin.de"]),
    license = __license__,
    platforms = ["Posix", "Windows"],
    keywords = ["svg", "reportlab", "PDF"],
    url = baseURL,
    download_url = baseURL + "tmp/svglib-%s.tar.gz" % __version__,
    package_dir = {'svglib': 'src/svglib'},
    packages = ['svglib'],
    scripts = ["src/scripts/svg2pdf"], 
    classifiers = classifiers,

    # for setuptools, only
    # install_requires = ["reportlab>2.0"],
)
