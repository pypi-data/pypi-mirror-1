### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for undefined page provide list all references on unknown
documents

$Id: undefined.py 51841 2008-10-10 18:12:52Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51841 $"
 
from zope.interface import implements
from zc.catalog.interfaces import IIndexValues
from zope.app.catalog.interfaces import ICatalog
from zope.app.zapi import getUtility

class UnDefined(object) :
    def undefined(self,backindexname,indexname) :
        index = getUtility(IIndexValues, context=self.context, name=backindexname)
        catalog = getUtility(ICatalog,context=self.context)
        for keyword in index.values() :
            if len(catalog.searchResults(**{indexname:{'any_of':(keyword,keyword)}})) == 0 :
                yield {
                    'keyword' : keyword, 
                    'document' : catalog.searchResults(**{backindexname:{'any_of':(keyword,keyword)}})
                    }
            
    
    @property
    def keyword(self) :
        return self.undefined('backkeyword','keyword')
                    
    @property
    def name(self) :
        return self.undefined('backname','name')            
            

    
    