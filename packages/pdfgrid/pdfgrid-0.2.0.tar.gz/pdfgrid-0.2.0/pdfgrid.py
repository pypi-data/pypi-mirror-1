#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Add a grid on top of all pages of a PDF document."""

import os
import sys
from cStringIO import StringIO

try:
    from pyPdf import PdfFileWriter, PdfFileReader
    from pyPdf.pdf import PageObject, ImmutableSet, ContentStream
    from pyPdf.generic import \
        NameObject, DictionaryObject, ArrayObject, FloatObject
except ImportError:
    _MSG = "Please install pyPdf first, see http://pybrary.net/pyPdf"
    raise RuntimeError(_MSG)

from reportlab.lib.pagesizes import A3, A4, A5
from reportlab.lib.units import mm, cm, inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas


__version__ = "0.2.0"
__license__ = "GPL 3"
__author__ = "Dinu Gherman"
__date__ = "2009-06-07"


def makeGridPage(pageSize, typ="rect", origin=None, styles=None):
    "Create an empty PDF page with a grid on it."
    
    # set some default values if not provided as arguments
    if origin is None:
        origin = (0, 0)
    if styles is None:
        styles = [(1*cm, 0, colors.black)]
    
    buffer = StringIO()
    canv = canvas.Canvas(None)
    canv.setPageSize(pageSize)
    canv.showOutline()

    x0, y0 = origin
    w, h = pageSize

    # tmporary hack
    w = max([w, h])
    h = max([w, h])

    for style in styles:
        # apply styling
        step, lw, col = style
        canv.setStrokeColor(col)
        canv.setLineWidth(lw)
        
        # draw grid (right now only regular rectangular)
        if typ == "rect":
            # draw vertical lines
            x = x0
            while 0 < x:
                canv.line(x, 0, x, h)
                x -= step
            x = x0
            while x < w:
                canv.line(x, 0, x, h)
                x += step
                
            # draw horizontal lines
            y = y0
            while 0 < y:
                canv.line(0, y, w, y)
                y -= step
            y = y0
            while y < h:
                canv.line(0, y, w, y)
                y += step

        # draw origin circle
        canv.circle(x0, y0, step/2.0)
    
    # finish
    canv.showPage()
    buffer.write(canv.getpdfdata())
    buffer.seek(0)

    return buffer


def grid(inPath, origin, styles, outputPat=None):
    "Overlay a grid on all pages of some document."

    # derive the ouput path from the output pattern, if given
    if not outputPat:
        outputPat = "%(dirname)s/%(base)s-grid%(ext)s"
    dirname = os.path.dirname(inPath)
    basename = os.path.basename(inPath)
    base = os.path.basename(os.path.splitext(inPath)[0])
    ext = os.path.splitext(inPath)[1]    
    aDict = {
        "dirname":dirname or ".", "basename":basename, 
        "base":base, "ext":ext
    }
    outPath = outputPat % aDict
    outPath = os.path.normpath(outPath)

    output = PdfFileWriter()
    input = PdfFileReader(open(inPath, "rb"))
    nPages = input.getNumPages()
    pageSize = A4
    grid = PdfFileReader(makeGridPage(pageSize, origin=origin, styles=styles))
    gridPage = grid.getPage(0)
    
    IS = ImmutableSet
    PO, AO, DO, NO = PageObject, ArrayObject, DictionaryObject, NameObject

    for i in range(nPages):
        docPage = input.getPage(i)
    
        newResources = DO()
        rename = {}
        orgResources = docPage["/Resources"].getObject()
        page2Resources = gridPage["/Resources"].getObject()
    
        for res in "ExtGState Font XObject ColorSpace Pattern Shading".split():
            res = "/" + res
            new, newrename = PO._mergeResources(orgResources, page2Resources, res)
            if new:
                newResources[NO(res)] = new
                rename.update(newrename)
    
        newResources[NO("/ProcSet")] = AO(
            IS(orgResources.get("/ProcSet", AO()).getObject()).union(
                IS(page2Resources.get("/ProcSet", AO()).getObject())
            )
        )
    
        newContentArray = AO()
        
        orgContent = docPage["/Contents"].getObject()
        newContentArray.append(PO._pushPopGS(orgContent, docPage.pdf))
        
        page2Content = gridPage['/Contents'].getObject()
        page2Content = PO._contentStreamRename(page2Content, rename, docPage.pdf)
        newContentArray.append(page2Content)
        
        docPage[NO('/Contents')] = ContentStream(newContentArray, docPage.pdf)
        docPage[NO('/Resources')] = newResources

        output.addPage(docPage)
        
    outputStream = open(outPath, "wb")
    output.write(outputStream)
    print "written:", outPath
