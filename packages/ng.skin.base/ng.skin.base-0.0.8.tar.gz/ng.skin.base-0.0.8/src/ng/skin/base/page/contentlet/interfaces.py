### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of viewlet interface for common content page.

$Id: interfaces.py 51194 2008-06-26 14:03:08Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51194 $"

from zope.viewlet import interfaces

class IContent(interfaces.IViewletManager) :
    """ Content """
