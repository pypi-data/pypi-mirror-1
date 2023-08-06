### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Inreface and schema for ng.kit.interfaceswitcher:
DynamicInterface custumasing page.

$Id: interfaces.py 51250 2008-07-05 12:17:19Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "ZPL"
__version__ = "$Revision: 51250 $"

from zope.schema.interfaces import Interface
from ng.schema.interfaceswitcher.interfacesetfield import InterfaceSet
from interfacevocabulary import InterfaceVocabulary
from zope.schema import Set,Choice

class IInterfaceSwitcher(Interface):
    """Schema of interface switcher page"""

    iface = Set(
      title=u"Select Interfaces",
      value_type=Choice(source = InterfaceVocabulary())
      )

    