#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"Project meta information"


__version__ = "0.2.0"
__license__ = "GPL 3"
__author__ = "Dinu Gherman"
__date__ = "2009-06-07"


name = "pdfgrid"
version = __version__
date = __date__
description = "Add a grid on top of all pages of a PDF document."
long_description = """\
`Pdfgrid` is a Python command-line tool and module for adding a regular 
grid on top of all pages of an existing PDF document. It will mostly be 
used for measuring individual parts of PDF pages like graphics or paragraph 
widths. For the time being, only a rectangular grid with major and minor 
lines is supported, and their colour and line widths can be set individually.

NOTE: This is an initial release. The API is likely to change and for the 
time being the grid size is limited to A4, but this will change in future 
releases.

`Pdfgrid` depends on two Open Source libraries, namely 
`pyPdf <http://pypi.python.org/pypi/pyPdf>`_, a package written by 
Mathieu Fenniak and `reportlab <http://www.reportlab.org/downloads.html>`_ 
by ReportLab, Ltd.

This version fixes an issue with the manual installation.


Features
++++++++

- add regular rectangular grid over all pages of a PDF document
- define grid origin on all PDF pages
- define grid styles containing grid step, line width and colour
- use multiple grids at once with different styling
- install a Python module named ``pdfgrid.py``
- install a Python command-line script named ``pdfgrid``
- provide a Unittest test suite


Examples
++++++++

You can use *pdfgrid* as a Python module e.g. like in the following
interactive Python session::

    >>> from reportlab.lib.colors import red
    >>> from reportlab.lib.units import cm
    >>> from pdfgrid import grid
    >>> grid("foo.pdf", origin=(0, 0), styles=[(1*cm, 0.1, red)])
    written: foo-grid.pdf
    
In addition there is a script named ``pdfscript``, which can be used 
from the system command-line e.g. like this::

    $ pdfgrid -h
    $ pdfgrid -v
    $ pdfgrid --origin "0,0" --styles "1*cm,0.1,colors.red" foo.pdf
    written: foo-grid.pdf
"""
author = 'Dinu Gherman'
author_email = '@'.join(['gherman', 'darwin.in-berlin.de'])
maintainer = author
maintainer_email = author_email
license_short = 'GNU GPL'
license = __license__
platforms = ["Posix", "Windows"]
keywords = ["overlay", "grid", "PDF"]
_baseURL = "http://www.dinu-gherman.net/"
url = _baseURL
download_url = _baseURL + "tmp/%s-%s.tar.gz" % (name, __version__)

scripts = ["pdfgrid"]
py_modules = ["pdfgrid"]

classifiers = [
    # see http://pypi.python.org/pypi?%3Aaction=list_classifiers
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
    "Topic :: Utilities",
    "Topic :: Printing",
    # "Topic :: Documentation",
    # "Topic :: Software Development :: Libraries :: Python Modules",
]

# for setuptools, only:
# install_requires = ["reportlab>2.0"],
