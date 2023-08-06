# Copyright (C) 2004-2008 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
#       $Id: Utils.py,v 1.1.1.1 2008/05/18 14:00:04 dieter Exp $
'''Utilities'''

from ExtensionClass import Base

class _UnCustomizable(Base):
  '''mixin class to prevent customization.'''
  def manage_doCustomize(self):
    "do not allow customization"
    raise TypeError('This object does not support customization')
