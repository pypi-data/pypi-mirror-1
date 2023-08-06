.. -*- mode: rst -*-

========
Pdfgrid
========

---------------------------------------------------------------------
Add a grid on top of all pages of a PDF document.
---------------------------------------------------------------------

:Author:     Dinu Gherman <gherman@darwin.in-berlin.de>
:Homepage:   http://www.dinu-gherman.net/
:Version:    Version 0.2.0
:Date:       2009-06-07
:Copyright:  GNU Public Licence v3 (GPLv3)


About
-----

`Pdfgrid` is a Python command-line tool and module for adding a regular 
grid on top of all pages of an exiwsting PDF document. It will mostly be 
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
--------

- add regular rectangular grid over all pages of a PDF document
- define grid origin on all PDF pages
- define grid styles containing grid step, line width and colour
- use multiple grids at once with different styling
- install a Python module named ``pdfgrid.py``
- install a Python command-line script named ``pdfgrid``
- provide a Unittest test suite


Examples
--------

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


Installation
------------

There are two ways to install `pdfgrid`, either as a so-called Python *egg* 
via the ``easy_install`` command, if available on your system, or from 
a source tarball. Please see the seperate file ``INSTALL.txt`` for more 
detailed instructions! 


Dependencies
------------

`Pdfgrid` depends on `pyPdf` which, if missing, will miraculously be 
installed together with `pdfgrid` if you have a working internet 
connection during the installation procedure. If for whatever reason 
`pyPdf` cannot be installed, `pdfgrid` should still install fine. 
In this case you'll get a warning when trying to run `pdfgrid`.

`PyPdf` also needs the `ReportLab toolkit 
<http://www.reportlab.org/downloads.html>`_ to be installed, 
which unfortunately cannot be installed yet as a Python **egg**.


Testing
-------

The `pdfgrid` tarball distribution contains a Unittest test suite 
in the folder ``src/test`` which can be run like shown in the 
following lines on the system command-line::
 
  $ tar xfz pdfgrid-0.2.0.tar.gz
  $ python test_pdfgrid.py
  written: samples/test-a4-p-grid-default.pdf
  .written: samples/test-a4-p-grid-origin.pdf
  .written: samples/test-a4-p-grid-style.pdf
  .written: samples/test-a4-p-grid-styles.pdf
  .
  ----------------------------------------------------------------------
  Ran 4 tests in 0.806s

  OK
  
  $ python test_pdfgridscript.py
  running: pdfgrid --styles '10*mm,0,colors.green;50*mm,2,colors.red' 'samples/test-a4-l.pdf'
  written: samples/test-a4-l-grid.pdf
  .
  ----------------------------------------------------------------------
  Ran 1 test in 0.482s

  OK


Bug reports
-----------

Please report bugs and patches to Dinu Gherman 
<gherman@darwin.in-berlin.de>. Don't forget to include information 
about the version of your hardware platform, operating system, Python 
interpreter and, of course, *pdfgrid* itself.
