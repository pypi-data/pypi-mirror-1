### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definition of viewlet interface for
commonedit.html page.

$Id: interfaces.py 51194 2008-06-26 14:03:08Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51194 $"

from zope.viewlet import interfaces

class IEditletManager(interfaces.IViewletManager) :
    """ Content """
