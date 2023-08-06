### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Intermediate class used to edit directly provided interfaces

$Id: interfaceswitcher.py 51250 2008-07-05 12:17:19Z cray $
"""

__author__  = "Andrey Orlov, 2008"
__license__ = "ZPL"
__version__ = "$Revision: 51245 $"

from zope.interface import directlyProvidedBy, noLongerProvides, alsoProvides
from zope.security.proxy import removeSecurityProxy

class InterfaceSwitcher(object) :
    def getData(self,*kv,**kw) :
        return (
          ('iface', set(directlyProvidedBy(removeSecurityProxy(self.context)))),
        )
        
    def setData(self,d,**kw) :
	context = removeSecurityProxy(self.context)
        for interface in directlyProvidedBy(context) :
	    print "clear:",interface
            noLongerProvides(context, interface)          
            
	print self.context, type(self.context)
	print context, type(context)
        for interface in dict(d)['iface'] :
	    print "set:",interface, type(interface)
            alsoProvides(context, interface)            

        return True

