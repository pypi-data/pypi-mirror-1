### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Base class intendent to create adapter joined a few other adapters.

$Id: joininterfaceadapterfactory.py 51050 2008-04-29 03:08:58Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51050 $"
 
from zope.interface import implements
from zc.catalog.interfaces import IIndexValues
from zope.app.catalog.interfaces import ICatalog
from zope.app.zapi import getUtility
from zope.schema import getFieldNames

def joininterfaceadapterfactory(*kv) :
    
    class Adapter(object) :
        def __init__(self,context) :
            self.context = context
            self.__parent__ = context
            
        def _set(self,iface,name,value) :
            print "SET:",self,iface,name,value
            setattr(iface(self.context),name,value)

        def _get(self,iface,name) :
            return getattr(iface(self.context),name)
            
            
    for iface in kv :
        for name in getFieldNames(iface) :
            setattr(
                Adapter,
                name,
                property(lambda x,name=name,iface=iface : x._get(iface,name), lambda x,y,name=name,iface=iface : x._set(iface,name,y))
                )
            
    return Adapter
    
                         