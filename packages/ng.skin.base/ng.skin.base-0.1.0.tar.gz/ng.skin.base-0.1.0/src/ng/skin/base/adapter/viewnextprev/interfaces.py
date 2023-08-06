### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based viewnextpprev package

$Id: interfaces.py 51888 2008-10-21 07:10:48Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51888 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Datetime

class INextPrev(Interface):
    """Next-Previous interface"""
    
    prev = Field(title = u'Previous Object')

    next = Field(title = u'Next Object')

    up   = Field(title = u'Upper Object')            

