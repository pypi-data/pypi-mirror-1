# Copyright (C) 2004 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
# see "LICENSE.txt" for details
#       $Id: testTrustedPageTemplateFile.py,v 1.2 2008/06/15 07:00:04 dieter Exp $

from TestBase import TestCase, getSuite

from Products.TrustedExecutables.TrustedPageTemplateFile import \
     TrustedPageTemplateFile

class TestTrustedPageTemplateFile(TestCase):
  def testNoUnauthorized(self):
    f = self.folder
    fi = TrustedPageTemplateFile('Files/pt.xpt', globals()).__of__(f)
    fi() # we succeed unless we get an exception

  def testCallPy(self):
    # test that calling a python script from a trusted page template succeeds
    # (this broke in version 1.0.0)
    fi = self.folder.Files
    self.assertEqual(fi.pt_call_py().rstrip(), 'test')
    


def test_suite(): return getSuite(TestTrustedPageTemplateFile,
                                  )
