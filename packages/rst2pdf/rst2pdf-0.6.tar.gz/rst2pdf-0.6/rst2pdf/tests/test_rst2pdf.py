# -*- coding: utf-8 -*-
#$HeadURL: https://rst2pdf.googlecode.com/svn/tags/0.6/rst2pdf/tests/test_rst2pdf.py $
#$LastChangedDate: 2008-08-29 13:47:05 -0300 (Fri, 29 Aug 2008) $
#$LastChangedRevision: 165 $
from unittest import TestCase, makeSuite
from pyPdf import PdfFileReader
import cStringIO

import docutils.core

import rst2pdf
from utils import *

import pdb
#import pdb; pdb.set_trace()

def input_file_path(file):
    return join(PREFIX, 'input', file)

class FullGenerationTests(TestCase):
    """ broken since createPdf is no longer a function
    """
    def test_bullet_chars_full(self):
        self.output=cStringIO.StringIO()
        input_file = input_file_path('test_bullet_chars.txt')
        input=open(input_file,'r').read()
        createPdf(text=input, output=self.output, styleSheet=None)
        self.output.seek(0)
        result = PdfFileReader(self.output)
        text_result = result.getPage(0).extractText()
        self.assertEqual(text_result, u'\nTest\nItem 1\nItem 2\n')

    
class GenerationTests(rst2pdfTests):

    def test_bullet_chars(self):
        input_file = input_file_path('test_bullet_chars.txt')
        input=open(input_file,'r').read()
        doctree=docutils.core.publish_doctree(input)
        elements=self.converter.gen_elements(doctree,0)
        self.assertEqual(len(elements), 4)
        self.assertEqual(elements[1].text, 'Test')
        self.assertEqual(elements[2]._cellvalues[0][0][0].text, 'Item 1')
        self.assertEqual(elements[2]._cellvalues[0][0][0].bulletText, u'\u2022')
        self.assertEqual(elements[3]._cellvalues[0][0][0].text, 'Item 2')
        self.assertEqual(elements[3]._cellvalues[0][0][0].bulletText, u'\u2022')
        #pdb.set_trace()
        
def test_suite():
    suite = makeSuite(GenerationTests)
    return suite
    
if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')