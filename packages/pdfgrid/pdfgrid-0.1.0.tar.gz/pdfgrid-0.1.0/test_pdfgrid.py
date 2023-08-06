#!/usr/bin/env python

"Testsuite for pdfgrid module."


import os
import sys
import unittest

try:
    from pyPdf import PdfFileReader
except ImportError:
    _MSG = "Please install pyPdf first, see http://pybrary.net/pyPdf"
    raise RuntimeError(_MSG)

from reportlab.lib.units import mm, cm, inch
from reportlab.lib import colors

from pdfgrid import grid


class GridTests(unittest.TestCase):
    "Test overlaying a grid on all pages of a PDF document."

    def test0(self):
        "Test overlaying a default grid on all pages of a PDF document."

        path = "samples/test-a4-p.pdf"
        outPath = os.path.splitext(path)[0] + "-grid-default.pdf"
        grid(path, origin=None, styles=None, outputPat=outPath)

    def test1(self):
        "Test overlaying a grid with a changed origin on the pages."

        path = "samples/test-a4-p.pdf"
        outPath = os.path.splitext(path)[0] + "-grid-origin.pdf"
        grid(path, origin=(2*cm, 3*cm), styles=None, outputPat=outPath)

    def test2(self):
        "Test overlaying a grid with changed origin and line style on the pages."

        path = "samples/test-a4-p.pdf"
        outPath = os.path.splitext(path)[0] + "-grid-style.pdf"
        styles = [(5*cm, 0.1, colors.red)]
        grid(path, origin=(2*cm, 3*cm), styles=styles, outputPat=outPath)

    def test3(self):
        "Test two grids with changed origin and multiple styles on the pages."

        path = "samples/test-a4-p.pdf"
        outPath = os.path.splitext(path)[0] + "-grid-styles.pdf"
        styles = [(1*cm, 0.1, colors.blue), (5*cm, 2, colors.red)]
        grid(path, origin=(2*cm, 3*cm), styles=styles, outputPat=outPath)


if __name__ == "__main__":
    unittest.main()
