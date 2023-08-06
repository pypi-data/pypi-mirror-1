### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: fixintid.py 51250 2008-07-05 12:17:19Z cray $
"""
__author__  = "Sergey Alembekov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51250 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.app.zapi import getUtility,getSiteManager
from zope.app.intid.interfaces import IIntIds
from zope.app.container.interfaces import IReadContainer
                
class FixIntId(object) :
    fixobjects=("qqqqqq",)

    def getData(self) :
        print "getData"
        return ()
        
    def update(self) :
        # Пришлось перенести сюда, так как setData вызывается только если
        # изменилось хотя бы одно поле Тебе задание: нужно привести объект,
        # возвращаемый getSiteManager() к интерфейсу, предоставляющему
        # атрибут __parent__, и, объект из __parent__ - к интерфейсу с
        # атрибутом __name__. Я об этом много писал в лекциях, не ожидал,
        # что ты это пропустишь: как-то на тебя не похоже.
        # 
        
    
        #self.fixobjects=[getSiteManager().__parent__.__name__]
        queue=[(getSiteManager().__parent__.__name__)]
        #return super(FixIntId,self).update()
        while queue :
            ob  = queue.pop()
            try :
                intid = getUtility(IIntIds,context=ob)
            except LookupError :
                pass
            else :
                try :
                    intid.getId(ob)
                except KeyError, msg :
                    print "registered"
                    #intid.register(ob)
                else :
                    print "already been registered"
            if IReadContainer.providedBy(ob) :
            #    l = [ (x,path + "/" + x.__name__) for x in ob.values() ]
            #    l = [(x.__name__) for x in ob.values()]
            #    l.extend(queue)
                 self.fixobjects.append(ob)
        return super(FixIntId,self).update()

                
    def setData(self,data) :
       pass 
