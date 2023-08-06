# Copyright (C) 2004-2008 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
#       $Id: TrustedPythonScriptMixin.py,v 1.1.1.1 2008/05/18 14:00:04 dieter Exp $
'''Auxiliary mixin class to implement trusted PythonScripts.'''
import __builtin__
from operator import getitem

from ExtensionClass import Base
from RestrictedPython.RestrictionMutator import \
     RestrictionMutator as RM, FuncInfo, _print_target_name
from RestrictedPython.RCompile import RFunction, compileAndTuplize
from RestrictedPython import PrintCollector

from Products.PythonScripts.PythonScript import PythonScript

from dm.reuse import rebindFunction

_Globals = {
  '__builtins__':__builtin__.__dict__,
  '_apply_':      apply,
  '_getitem_':    getitem,
  '_getiter_':    iter,
   '_print_':     PrintCollector,
  '_write_':      lambda ob:ob,
  }
  

class TrustedPythonScriptMixin(Base):
  _newfun = rebindFunction(PythonScript._newfun.im_func,
                           safe_builtins=__builtin__.__dict__,
                           _getattr_=getattr,
                           _getitem_=getitem,
                           _write_=lambda ob:ob,
                           # for Zope 2.7.1 and up
                           get_safe_globals = _Globals.copy,
                           guarded_getattr = getattr,
                           )

  def _compiler(self, *args, **kw):
    # Bah: apparently someone renamed 'globalize' to 'globals' in 'Rfunction.__init__' near Zope 2.7.1
    try:
      gen = RFunction(*args, **kw)
    except TypeError:
      #work around the incompatible change
      if 'globalize' not in kw: raise
      kw['globals'] = kw['globalize']
      del kw['globalize']
      gen = RFunction(*args, **kw)
    gen.rm = RestrictionMutator()
    return compileAndTuplize(gen)


class RestrictionMutator:
  '''a 'RestrictionMutator' without restrictions.'''

  def __init__(self):
    self.warnings = []
    self.errors = []
    self.used_names = {}
    self.funcinfo = FuncInfo()

  def checkName(self, node, name):
    if name == "printed":
      self.error(node, '"printed" is a reserved name.')
    
  
  visitName = RM.visitName.im_func
  visitAssName = RM.visitAssName.im_func
  visitFunction = RM.visitFunction.im_func
  visitModule = RM.visitModule.im_func
  visitClass = RM.visitClass.im_func
  visitImport = RM.visitImport.im_func

  prepBody = RM.prepBody.im_func

  def visitPrint(self, node, walker):
    """we add the current print target if no target is specified."""
    node = walker.defaultVisitNode(node)
    self.funcinfo.print_used = 1
    self.funcinfo._print_used = 1 # compatibility?
    if node.dest is None: node.dest = _print_target_name
    return node

  visitPrintnl = visitPrint 
