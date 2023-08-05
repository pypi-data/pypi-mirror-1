##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

"""
Tests, tests, tests.........
"""

import os
import unittest

from zope.interface.verify import verifyClass
from zopyx.convert.interfaces import IFOConverter, IHTML2FOConverter

from zopyx.convert.html2fo import HTML2FOConverter
from zopyx.convert.fo2xfc import RTFConverter, WMLConverter, DOCXConverter, ODTConverter
from zopyx.convert.fo2pdf import PDFConverter


test_html = os.path.join(os.path.dirname(__file__), 'data', 'test.html')

class ConverterTests(unittest.TestCase):

    def testInterfaces(self):
        verifyClass(IHTML2FOConverter, HTML2FOConverter)
        verifyClass(IFOConverter, RTFConverter)
        verifyClass(IFOConverter, ODTConverter)
        verifyClass(IFOConverter, DOCXConverter)
        verifyClass(IFOConverter, WMLConverter)

    def testPDF(self):
        fo_filename = HTML2FOConverter().convert(test_html)
        output_filename = PDFConverter().convert(fo_filename)

    def testRTF(self):
        fo_filename = HTML2FOConverter().convert(test_html)
        output_filename = RTFConverter().convert(fo_filename)

    def testODT(self):
        fo_filename = HTML2FOConverter().convert(test_html)
        output_filename = ODTConverter().convert(fo_filename)

    def testWML(self):
        fo_filename = HTML2FOConverter().convert(test_html)
        output_filename = WMLConverter().convert(fo_filename)

    def testDOCX(self):
        fo_filename = HTML2FOConverter().convert(test_html)
        output_filename = DOCXConverter().convert(fo_filename)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ConverterTests))
    return suite

