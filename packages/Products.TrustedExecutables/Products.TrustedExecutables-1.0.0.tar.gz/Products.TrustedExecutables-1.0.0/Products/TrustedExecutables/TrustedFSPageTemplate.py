# Copyright (C) 2004-2008 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
#       $Id: TrustedFSPageTemplate.py,v 1.1.1.1 2008/05/18 14:00:04 dieter Exp $
'''FSPageTemplate unrestricted by Zopes security'''

import sys

import Globals
from zLOG import LOG, ERROR

from Products.CMFCore.FSPageTemplate import \
     FSPageTemplate, \
     PageTemplate, \
     registerFileExtension, Cacheable, _setCacheHeaders

from dm.reuse import rebindFunction
from Utils import _UnCustomizable
from TrustedExpression import getEngine, ModuleImporter

class TrustedFSPageTemplate(_UnCustomizable, FSPageTemplate):
  
  meta_type = 'Trusted Filesystem Page Template'

  pt_getEngine = staticmethod(getEngine)

  pt_getContext = rebindFunction(FSPageTemplate.pt_getContext.im_func,
                                 SecureModuleImporter=ModuleImporter,
                                 )


registerFileExtension('xpt', TrustedFSPageTemplate)
