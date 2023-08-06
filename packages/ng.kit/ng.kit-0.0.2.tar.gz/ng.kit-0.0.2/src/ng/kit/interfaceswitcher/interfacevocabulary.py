### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Vocabulary this all non-dynamic interfaces

$Id: interfacevocabulary.py 51250 2008-07-05 12:17:19Z cray $
"""

__author__  = "Andrey Orlov, 2008"
__license__ = "ZPL"
__version__ = "$Revision: 51250 $"

from zope.interface import implements, providedBy, directlyProvidedBy
from zope.interface.interfaces import IInterface
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import  IContextSourceBinder
from zope.app.zapi import getUtilitiesFor
from zope.security.proxy import removeSecurityProxy
    
class InterfaceVocabulary(object) :
    implements(IContextSourceBinder)

    def __call__(self, ob) :        
        ob = removeSecurityProxy(ob)
        return SimpleVocabulary.fromItems(
            sorted(set(
                [(interface.__module__ + '.' + interface.__name__,interface) for interface in
                  [ interface
                    for (name,interface) in getUtilitiesFor(IInterface, object) 
                    if not interface.providedBy(ob)  ]
                +
                  [ interface for interface in directlyProvidedBy(ob) ]
                ]),
                key = lambda (name,interface): name)
            )
