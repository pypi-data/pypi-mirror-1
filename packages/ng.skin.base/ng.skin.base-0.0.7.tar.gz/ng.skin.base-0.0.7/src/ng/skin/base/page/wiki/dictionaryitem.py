### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Factories for article class used in wiki

$Id: dictionaryitem.py 51050 2008-04-29 03:08:58Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51050 $"
 
from zope.interface import implements
from ng.content.article.article.article import  Article
from ng.content.annotation.annotationswitcher.demo.interfaces import IAnnotationSwitcherDict 

from zope.security.proxy import removeSecurityProxy
from zope.interface import alsoProvides

def DictionaryItem(context,*kv,**kw) :
    article = Article(*kv,**kw)
    alsoProvides(article, IAnnotationSwitcherDict)
    return article
    
    
    