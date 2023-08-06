### -*- coding: utf-8 -*- #############################################
"""ReferenceBase class for the Zope 3 based reference package

$Id: editform.py 51250 2008-07-05 12:17:19Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 51250 $"
 
from zope.interface import Interface
                
class EditForm(object) :

    def update(self) :
        super(RemoteObjectEdit, self).update()
        if "update" in self.request :
            self.context.update()
                    

        
        
        
