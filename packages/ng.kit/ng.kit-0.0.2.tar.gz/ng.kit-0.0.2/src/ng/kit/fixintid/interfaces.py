### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51250 2008-07-05 12:17:19Z cray $
"""
__author__  = "Sergey Alembekov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51250 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
                
                
class IFixIntId(Interface) :
    pass
