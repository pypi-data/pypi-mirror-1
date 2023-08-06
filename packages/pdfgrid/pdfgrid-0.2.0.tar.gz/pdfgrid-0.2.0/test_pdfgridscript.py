#!/usr/bin/env python

"Testsuite for nop."


import os
import sys
import unittest

# filter command-line argument paths, so unittest's main will not see them
PATHS = [p for p in sys.argv[1:] if os.path.exists(p)]
NONPATHS = [p for p in sys.argv[1:] if not os.path.exists(p)]
sys.argv[1:] = NONPATHS


class PdfgridScriptTestCase(unittest.TestCase):
    "Testing pdfgrid script."

    def test0(self):
        "Test nop script."

        # skip test, if nopscript not found
        if not os.popen("which nopscript").read().strip():
            print "nopscript not found, test skipped."
            return
            
        for path in PATHS:
            cmd = "pdfgrid --styles '10*mm,0,colors.green;50*mm,2,colors.red' '%s'" % path
            print "running:", cmd
            os.system(cmd)


if __name__ == "__main__":
    unittest.main()
