### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter dictionary item to article.

$Id: dictionaryitemadapter.py 51888 2008-10-21 07:10:48Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51888 $"
 
from zope.interface import implements
from ng.content.article.interfaces import IDocShort
from ng.content.annotation.dictannotation.interfaces import IDictAnnotation
from joininterfaceadapterfactory import joininterfaceadapterfactory

DictionaryItemAdapter = joininterfaceadapterfactory(IDocShort, IDictAnnotation)

                         