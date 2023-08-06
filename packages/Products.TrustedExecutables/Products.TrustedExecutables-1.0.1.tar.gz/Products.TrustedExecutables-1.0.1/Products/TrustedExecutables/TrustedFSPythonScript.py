# Copyright (C) 2004-2008 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
#       $Id: TrustedFSPythonScript.py,v 1.1.1.1 2008/05/18 14:00:04 dieter Exp $
'''FSPythonScript unrestricted by Zopes security.'''
import linecache, os

from Products.CMFCore.FSPythonScript import \
     FSPythonScript, \
     registerFileExtension, Cacheable

from dm.reuse import rebindFunction
from Utils import _UnCustomizable
from TrustedPythonScriptMixin import TrustedPythonScriptMixin
from TrustedPythonScript import TrustedPythonScript


# ATT: in case Chris Wither's "zdb" is installed, it is essential
#  that we are imported first. Otherwise,
#  the original "FSPythonScript._write" is lost and can no longer
#  be rebound
_rebound_write = rebindFunction(FSPythonScript._write.im_func,
                          PythonScript=TrustedPythonScript,
                          _NCPythonScript=TrustedPythonScript,
                          )


class TrustedFSPythonScript(_UnCustomizable, TrustedPythonScriptMixin, FSPythonScript):
  meta_type = 'Trusted Filesystem Python Script'

  def _write(self, *args, **kw):
    _rebound_write(self, *args, **kw)
    # make it debuggable -- stolen from Chris Wither's "zdb"
    size = len(self._body)
    if not size: return
    filename = self._filepath
    try: stat = os.stat(filename)
    except os.error: return 
    if filename.startswith('pypackage:'):
      try: from pypackage import getLocation
      except ImportError: from packageresources import getLocation
      filename = getLocation(filename)
    lines = [l+'\n' for l in self._body.split('\n')]
    linecache.cache[filename] = stat.st_size, stat.st_mtime, lines, filename




registerFileExtension('xpy', TrustedFSPythonScript)
