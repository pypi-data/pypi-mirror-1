# Copyright (C) 2008 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
#       $Id: PythonExpr.py,v 1.1.1.1 2008/05/18 14:00:04 dieter Exp $
'''Trusted equivalent of 'ZRPythonExpr'.'''

from dm.reuse import rebindFunction

from zope.tales.pythonexpr import PythonExpr
from DocumentTemplate.DT_Util import TemplateDict

from Products.PageTemplates.ZRPythonExpr import call_with_ns

call_with_ns = rebindFunction(call_with_ns,
                              Rtd = TemplateDict,
                              )



