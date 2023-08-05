### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of viewlet interface for common content page.

$Id: interfaces.py 50807 2008-02-21 11:53:14Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 50807 $"

from zope.viewlet import interfaces

class IContent(interfaces.IViewletManager) :
    """ Content """
