### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of viewlet interface for common content page.

$Id: interfaces.py 51050 2008-04-29 03:08:58Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51050 $"

from zope.viewlet import interfaces

class IContent(interfaces.IViewletManager) :
    """ Content """
