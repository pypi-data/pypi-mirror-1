# Copyright (C) 2004-2008 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
#       $Id: TrustedPageTemplateFile.py,v 1.1.1.1 2008/05/18 14:00:04 dieter Exp $
'''A 'PageTemplateFile' without security restrictions.'''

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from dm.reuse import rebindFunction
from TrustedExpression import getEngine, ModuleImporter


class TrustedPageTemplateFile(PageTemplateFile):
  pt_getEngine = rebindFunction(PageTemplateFile.pt_getEngine.im_func,
                                  getEngine = getEngine
                                  )

  pt_getContext = rebindFunction(PageTemplateFile.pt_getContext.im_func,
                                 SecureModuleImporter=ModuleImporter,
                                 )

