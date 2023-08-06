### -*- coding: utf-8 -*- #############################################
"""XMLRPC Edit class to edit any text attributes in vlass

$Id: xmlrpcedit.py 51898 2008-10-21 11:36:39Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51898 $"
 
from zope.interface import Interface
from zope.security.proxy import removeSecurityProxy
from zope.app.container.interfaces import IContainer
from zope.component.interface import nameToInterface
from zope.lifecycleevent import ObjectModifiedEvent, Attributes
from zope.event import notify

class XMLRPCEdit(object) :

    def getattr(self,interface,name) :
        return getattr(nameToInterface(self.context,interface)(self.context),name) or u""                   

    def setattr(self,interface,name,value) :
        schema = nameToInterface(self.context,interface)
        setattr(nameToInterface(self.context,interface)(self.context),name,value) 
        notify(ObjectModifiedEvent(self.context,Attributes(schema,name)))
        
    def keys(self) :
        if IContainer.providedBy(self.context) :
            return list(IContainer(self.context).keys())
        return []            

    def klass(self) :
        ob = removeSecurityProxy(self.context)
        return ob.__class__.__module__ + "." + ob.__class__.__name__

    def check(self,interface) :
        try :
            nameToInterface(self.context,interface)(self.context)
        except TypeError,msg :
            return False
        return  True
        
    __nonzero__ = True
    