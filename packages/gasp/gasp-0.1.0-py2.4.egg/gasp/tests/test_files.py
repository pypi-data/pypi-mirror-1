
##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTLAR PURPOSE.
#
##############################################################################
"""Testing all XML Locale functionality.

$Id$
"""
import os
import PIL.Image
import popen2
import unittest
import sys
import gasp.tests
import gasp.testing

class GraphicsTest(unittest.TestCase):
    def __init__(self, moduleFileName, basePath, testPath):
        self.moduleFileName = moduleFileName
        self.basePath = basePath
        self.testPath = testPath
	unittest.TestCase.__init__(self)

    def setUp(self):
	self.counter = 0
	self.basename = self.moduleFileName.split('.')[0]
	gasp.testing.TEST_CASE = self

    def tearDown(self):
        gasp.testing.TEST_CASE = None

    def runTest(self):
        name = self.basename
        __import__('gasp.tests.input.' + name)
	if self.counter == 0:
	    return
	for i in xrange(self.counter):
            self.assertSameImage(
                os.path.join(self.basePath, name + '.%i.png' %i),
                os.path.join(self.testPath, name + '.%i.png' %i),
                )
        
    def assertSameImage(self, baseImage, testImage):
        base = PIL.Image.open(baseImage).getdata()
        test = PIL.Image.open(testImage).getdata()
        for i in range(len(base), 2):
            if (sum(base[i]) - sum(test[i])) != 0:
                self.fail('Image is not the same.')


def test_suite():
   suite = unittest.TestSuite()
   inputDir = os.path.join(os.path.dirname(gasp.tests.__file__), 'input')
   outputDir = os.path.join(os.path.dirname(gasp.tests.__file__), 'output')
   expectDir = os.path.join(os.path.dirname(gasp.tests.__file__), 'expected')
   for filename in os.listdir(inputDir):
       if not filename.endswith(".py") or filename.startswith("__init__"):
           continue
       
       TestCase = type(filename[:-3], (GraphicsTest,), {})
       case = TestCase(filename, outputDir, expectDir)
       suite.addTest(case)


   return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
