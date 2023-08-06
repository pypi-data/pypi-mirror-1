### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of viewlet interface for common content page.

$Id: interfaces.py 51888 2008-10-21 07:10:48Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51888 $"

from zope.viewlet import interfaces

class IContent(interfaces.IViewletManager) :
    """ Content """
