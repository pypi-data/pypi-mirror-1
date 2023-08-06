# Copyright (C) 2004 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
# see "LICENSE.txt" for details
#       $Id: testTrustedFSObjects.py,v 1.1.1.1 2008/05/18 14:00:04 dieter Exp $
from TestBase import TestCase, getSuite

class TestTrustedFSObjects(TestCase):
  def testPageTemplate(self):
    fi = self.folder.Files
    fi.pt() # we succeed unless we get an exception

  def testPythonScript(self):
    fi = self.folder.Files
    self.assertEqual(fi.py().rstrip(), 'test')


def test_suite(): return getSuite(TestTrustedFSObjects,
                                  )
