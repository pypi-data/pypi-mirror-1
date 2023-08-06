# Copyright (C) 2004 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
# see "LICENSE.txt" for details
#       $Id: testTrustedPageTemplateFile.py,v 1.1.1.1 2008/05/18 14:00:04 dieter Exp $

from TestBase import TestCase, getSuite

from Products.TrustedExecutables.TrustedPageTemplateFile import \
     TrustedPageTemplateFile

class TestTrustedPageTemplateFile(TestCase):
  def testNoUnauthorized(self):
    f = self.folder
    fi = TrustedPageTemplateFile('Files/pt.xpt', globals()).__of__(f)
    fi() # we succeed unless we get an exception


def test_suite(): return getSuite(TestTrustedPageTemplateFile,
                                  )
