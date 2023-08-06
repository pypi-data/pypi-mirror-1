# Copyright (C) 2008 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
#       $Id: PythonExpr.py,v 1.2 2008/06/15 07:00:04 dieter Exp $
'''Trusted equivalent of 'ZRPythonExpr'.'''

from dm.reuse import rebindFunction

from zope.tales.pythonexpr import PythonExpr
from DocumentTemplate.DT_Util import TemplateDict

from Products.PageTemplates.ZRPythonExpr import call_with_ns

class Utd(TemplateDict):
  # required by "InstanceDict"
  guarded_getattr = getattr

call_with_ns = rebindFunction(call_with_ns,
                              Rtd = Utd,
                              )



