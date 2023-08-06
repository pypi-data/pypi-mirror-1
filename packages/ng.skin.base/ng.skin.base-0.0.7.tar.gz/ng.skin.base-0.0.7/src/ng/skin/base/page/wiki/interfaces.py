### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces and schemas for the article factories used by wiki

$Id: interfaces.py 51050 2008-04-29 03:08:58Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51050 $"
 
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
                                  
    