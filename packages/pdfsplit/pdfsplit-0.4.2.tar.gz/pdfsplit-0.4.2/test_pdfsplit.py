#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"Tests for pdfsplit module."

import os
import sys
import unittest

try:
    from pyPdf import PdfFileReader
except ImportError:
    _MSG = "Please install pyPdf first, see http://pybrary.net/pyPdf"
    raise RuntimeError(_MSG)

import pdfsplit


class SliceStr2SliceObjTests(unittest.TestCase):
    "Test converting slice strings to Python slice objects."

    def test0(self):
        "Test converting slice strings to Python slice objects."

        mapping = (
            ("0",     slice(0, 1, None)),
            ("0:5",   slice(0, 5, None)),
            ("-1",    slice(-1, None, None)),
            ("0::2",  slice(0, None, 2)),
            ("-3:-1", slice(-3, -1, None)),
            ("::-1",  slice(None, None, -1)),
        )
        for sstr, exp in mapping:
            res = pdfsplit.sliceStr2sliceObj(sstr)
            self.assertEqual(res, exp)


class RangeStr2SliceObjTests(unittest.TestCase):
    "Test converting range strings to Python slice objects."

    def test0(self):
        "Test converting range strings to Python slice objects."

        mapping = (
            ("1",     slice(0, 1, None)),
            ("1-5",   slice(0, 5, None)),
        )
        for rstr, exp in mapping:
            res = pdfsplit.rangeStr2sliceObj(rstr)
            self.assertEqual(res, exp)


    def test1(self):
        "Test converting invalid range string."

        rangeStrs = [
            "5-1",
        ]
        for rstr in rangeStrs:
            self.assertRaises(
                ValueError, pdfsplit.rangeStr2sliceObj, rstr
            )


class ModuleUsageTests(unittest.TestCase):
    "Test pdfsplit used as a module."

    def test0(self):
        "Test slicing page 0."

        tag = "-split-0"
        pdfsplit.DEFAULT_BASENAME_POSTFIX_TAG = tag
        path0 = "samples/test.pdf"
        path1 = os.path.splitext(path0)[0] + tag +".pdf"
        pdfsplit.splitPages(path0, ["0"])
        self.assert_(os.path.exists(path1))
        
        # assert output has correct number of pages
        input = PdfFileReader(file(path1, "rb"))
        self.assertEqual(input.getNumPages(), 1)
        
        # assert output page(s) has/have correct text content
        page = input.getPage(0)
        text = page.extractText().strip()
        self.assertEqual(text, "0")


    def test1(self):
        "Test slicing pages 0:5."

        tag = "-split-0..5"
        pdfsplit.DEFAULT_BASENAME_POSTFIX_TAG = tag
        path0 = "samples/test.pdf"
        path1 = os.path.splitext(path0)[0] + tag +".pdf"
        pdfsplit.splitPages(path0, ["0:5"])
        self.assert_(os.path.exists(path1))

        # assert output has correct number of pages
        input = PdfFileReader(file(path1, "rb"))
        self.assertEqual(input.getNumPages(), 5)
        
        # assert output page(s) has/have correct text content
        for i in range(5):
            page = input.getPage(i)
            text = page.extractText().strip()
            self.assertEqual(text, str(i))


    def test2(self):
        "Test slicing pages with odd numbers."

        tag = "-odd"
        pdfsplit.DEFAULT_BASENAME_POSTFIX_TAG = tag
        path0 = "samples/test.pdf"
        path1 = os.path.splitext(path0)[0] + tag +".pdf"
        pdfsplit.splitPages(path0, ["1::2"])
        self.assert_(os.path.exists(path1))

        # assert output has correct number of pages
        input = PdfFileReader(file(path1, "rb"))
        self.assertEqual(input.getNumPages(), 25)
        
        # assert output page(s) has/have correct text content
        for i in range(25):
            page = input.getPage(i)
            text = page.extractText().strip()
            self.assertEqual(text, str(2*i + 1))


    def test3(self):
        "Test slicing all pages in reversed order."

        tag = "-reversed"
        pdfsplit.DEFAULT_BASENAME_POSTFIX_TAG = tag
        path0 = "samples/test.pdf"
        path1 = os.path.splitext(path0)[0] + tag +".pdf"
        pdfsplit.splitPages(path0, ["::-1"])
        self.assert_(os.path.exists(path1))

        # assert output has correct number of pages
        input = PdfFileReader(file(path1, "rb"))
        self.assertEqual(input.getNumPages(), 50)
        
        # assert output page(s) has/have correct text content
        for i in range(50):
            page = input.getPage(i)
            text = page.extractText().strip()
            self.assertEqual(text, str(50-i-1))


class CommandLineUsageTests(unittest.TestCase):
    "Test pdfsplit used as a command-line tool."

    def test0(self):
        "Test slicing page 10."

        tag = "-split"
        path0 = "samples/test.pdf"
        path1 = os.path.splitext(path0)[0] + tag +".pdf"
        cmd = "%s ./pdfsplit 10 '%s'" % (sys.executable, path0)
        os.system(cmd)
        self.assert_(os.path.exists(path1))
        
        # assert output has correct number of pages
        input = PdfFileReader(file(path1, "rb"))
        self.assertEqual(input.getNumPages(), 1)
        
        # assert output page(s) has/have correct text content
        page = input.getPage(0)
        text = page.extractText().strip()
        self.assertEqual(text, "10")


if __name__=='__main__':
    unittest.main()
