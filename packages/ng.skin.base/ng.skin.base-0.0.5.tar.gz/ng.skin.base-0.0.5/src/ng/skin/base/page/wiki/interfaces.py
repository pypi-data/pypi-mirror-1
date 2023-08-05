### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces and schemas for the article factories used by wiki

$Id: interfaces.py 50807 2008-02-21 11:53:14Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 50807 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Bool, URI, Datetime, Object
from ng.content.article.interfaces import IDocShort
from ng.content.annotation.dictannotation.interfaces import IDictAnnotation

class IDictionaryItem(IDocShort,IDictAnnotation) :
    """ Attributes of article class """

class IArticleByName(IDocShort) :
    """ Attributes of article class """

    name = TextLine(title = u'Article Name',
        description = u'Article Name',
        default = u'',
        required = True)
                                  
    