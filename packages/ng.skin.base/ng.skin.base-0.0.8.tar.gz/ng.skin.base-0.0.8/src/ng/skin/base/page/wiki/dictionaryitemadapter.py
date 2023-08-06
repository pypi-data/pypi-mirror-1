### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter dictionary item to article.

$Id: dictionaryitemadapter.py 51194 2008-06-26 14:03:08Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51194 $"
 
from zope.interface import implements
from ng.content.article.interfaces import IDocShort
from ng.content.annotation.dictannotation.interfaces import IDictAnnotation
from joininterfaceadapterfactory import joininterfaceadapterfactory

DictionaryItemAdapter = joininterfaceadapterfactory(IDocShort, IDictAnnotation)

                         