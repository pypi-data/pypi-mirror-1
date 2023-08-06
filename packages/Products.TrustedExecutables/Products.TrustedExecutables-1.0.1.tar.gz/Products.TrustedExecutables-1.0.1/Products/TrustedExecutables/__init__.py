# Copyright (C) 2004 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
# see "LICENSE.txt" for details
#       $Id: __init__.py,v 1.1.1.1 2008/05/18 14:00:04 dieter Exp $
'''TrustedExecutables

this product defines a set of executable objects not restricted
by Zopes security checks.

The security checks are expensive. Thus avoiding them can
drastically speed things up.

You should use these features only for file system based objects
which are considered safe according to the Zope security philosophie.

CAUTION: These objects must make their own security checks when
  they access untrusted objects.
'''

import TrustedPageTemplateFile

try: import Products.CMFCore
except ImportError: pass
else:
  import TrustedFSPageTemplate, TrustedFSPythonScript

# add utilities to "__builtin__"
import __builtin__; _bd = __builtin__.__dict__
from DocumentTemplate.DT_Util import TemplateDict
for _k,_v in TemplateDict.__dict__.items():
  if not _k.startswith('_') and _k not in _bd: _bd[_k] = _v
del _k; del _v; del _bd
