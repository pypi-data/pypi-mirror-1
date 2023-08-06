### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of viewlet interface for common content page.

$Id: interfaces.py 51952 2008-10-23 20:14:11Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51952 $"

from zope.viewlet import interfaces

class IContent(interfaces.IViewletManager) :
    """ Content """
