# Copyright (C) 2004-2008 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
#       $Id: TrustedExpression.py,v 1.1.1.1 2008/05/18 14:00:04 dieter Exp $

from sys import modules

from dm.reuse import rebindFunction

import OFS
from Products.PageTemplates.Expressions import \
     ZopePathExpr, PathIterator, \
     getEngine, createZopeEngine, \
     render
from zope.tales.expressions import SimpleModuleImporter
from zope.traversing.adapters import traversePathElement

import PythonExpr


ModuleImporter = SimpleModuleImporter()


# sad that we must duplicate this code here.
def boboAwareZopeTraverse(object, path_items, econtext):
    """Traverses a sequence of names, first trying attributes then items.

    This uses Zope 3 path traversal where possible and interacts
    correctly with objects providing OFS.interface.ITraversable when
    necessary (bobo-awareness).
    """
    request = getattr(econtext, 'request', None)
    path_items = list(path_items)
    path_items.reverse()

    while path_items:
        name = path_items.pop()
        if OFS.interfaces.ITraversable.providedBy(object):
          if name.startswith('_'):
            # We know that even 'unrestrictedTraverse' will reject it.
            # We do not want to reimplement 'unrestrictedTraverse' (without
            # the stupid restriction) but still support at least
            # attribute access (maybe, we do more later)
            object = getattr(object, name)
          else:
            object = object.unrestrictedTraverse(name)
        else:
          object = traversePathElement(object, name, path_items,
                                         request=request)
    return object

render = rebindFunction(render,
                        ZRPythonExpr = PythonExpr,
                        )


class ZopePathExpr(ZopePathExpr):
  __init__ = rebindFunction(ZopePathExpr.__init__,
                            boboAwareZopeTraverse = boboAwareZopeTraverse,
                            )
  _eval = rebindFunction(ZopePathExpr._eval,
                         render = render,
                         )

class PathIterator(PathIterator):
  same_part = rebindFunction(PathIterator.same_part,
                             boboAwareZopeTraverse = boboAwareZopeTraverse,
                             )

createZopeEngine = rebindFunction(createZopeEngine,
                                  ZopePathExpr = ZopePathExpr,
                                  PathIterator = PathIterator,
                                  ZRPythonExpr = PythonExpr,
                                  SecureModuleImporter = ModuleImporter,
                                  )

_engine = createZopeEngine()
def getEngine(): return _engine


