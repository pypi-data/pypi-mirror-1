### -*- coding: utf-8 -*- #############################################
#######################################################################
"""View Adapter used to get view with one word random selected
from the index.

$Id: viewword.py 51213 2008-06-30 12:42:36Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51213 $"

from zope.interface import Interface
from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from zope.publisher.browser import BrowserView
from random import choice
from zc.catalog.interfaces import IIndexValues
from zope.app.zapi import getUtility
        
class WordView(BrowserView) :
    def __init__(self,*kv,**kw) :
        super(WordView,self).__init__(*kv,**kw)

    def word(self) :
        try :
            return choice(list(getUtility(IIndexValues, name='keyword',context=self.context).values()))
        except IndexError :
            return ""                
        
        
