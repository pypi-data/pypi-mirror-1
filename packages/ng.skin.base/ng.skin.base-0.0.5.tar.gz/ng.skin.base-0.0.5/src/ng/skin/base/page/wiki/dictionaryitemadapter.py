### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter dictionary item to article.

$Id: dictionaryitemadapter.py 50807 2008-02-21 11:53:14Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50807 $"
 
from zope.interface import implements
from ng.content.article.interfaces import IDocShort
from ng.content.annotation.dictannotation.interfaces import IDictAnnotation
from joininterfaceadapterfactory import joininterfaceadapterfactory

DictionaryItemAdapter = joininterfaceadapterfactory(IDocShort, IDictAnnotation)

                         