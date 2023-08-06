# Copyright (C) 2004 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
# see "LICENSE.txt" for details
#       $Id: TestBase.py,v 1.1.1.1 2008/05/18 14:00:04 dieter Exp $
'''Test base class.

The 'TrustedExecutables' tests use 'ZopeTestCase'.
You must install this package separately (under 'lib/python/Testing').
You can get 'ZopeTestCase' from Zope.org.
'''

from os.path import join
from unittest import TestSuite, makeSuite


from Globals import package_home
from Testing.ZopeTestCase import ZopeTestCase, installProduct

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import getContainingPackage

prefix = getContainingPackage(__name__)

installProduct('CMFCore', 1)
installProduct('Five', 1)
registerDirectory('Files', globals())


class TestCase(ZopeTestCase):
  def afterSetUp(self):
    folder = self.folder
    folder.manage_addProduct['CMFCore'].manage_addDirectoryView(
      prefix + ':Files', 'Files'
      )


def getSuite(*testClasses, **kw):
  prefix= kw.get('prefix','test')
  return TestSuite([makeSuite(cl,prefix) for cl in testClasses])
  
