### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definition of viewlet interface for
commonedit.html page.

$Id: interfaces.py 51213 2008-06-30 12:42:36Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51213 $"

from zope.viewlet import interfaces

class IEditletManager(interfaces.IViewletManager) :
    """ Content """
