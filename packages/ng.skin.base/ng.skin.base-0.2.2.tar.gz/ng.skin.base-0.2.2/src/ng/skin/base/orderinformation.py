### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Open ID authenticator class (use IProfileAnnotation)

$Id: orderinformation.py 52443 2009-02-01 20:09:16Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52443 $"

from ng.lib.orderinformation import OrderInformation

class ContentOrderInformation(OrderInformation) :
    name = ["abstract", "body", "photo",   "backref",  "contenticons", "reference",  "comment", "content" ]

class ColumnOrderInformation(OrderInformation) :
    name = [ "currentbox", "rubriclist", "rubriccloud", "subscribe", "toolbox", "loginbox", "newslistbox", ]
