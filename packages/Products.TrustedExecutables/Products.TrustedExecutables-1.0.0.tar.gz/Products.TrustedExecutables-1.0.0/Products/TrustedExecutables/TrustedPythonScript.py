# Copyright (C) 2004-2008 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
#       $Id: TrustedPythonScript.py,v 1.1.1.1 2008/05/18 14:00:04 dieter Exp $
'''Python Script unrestricted by Zopes security.

CAUTION: Almost surely, you do not want to make this available.
'''

from Products.PythonScripts.PythonScript import PythonScript

from TrustedPythonScriptMixin import TrustedPythonScriptMixin

class TrustedPythonScript(TrustedPythonScriptMixin, PythonScript):
  '''Python Script unrestriced by Zopes security.'''
  meta_type = 'Trusted Python Script'
