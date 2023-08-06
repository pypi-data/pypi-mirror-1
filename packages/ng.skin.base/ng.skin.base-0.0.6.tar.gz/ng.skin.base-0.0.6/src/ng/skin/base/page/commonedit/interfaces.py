### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definition of viewlet interface for
commonedit.html page.

$Id: interfaces.py 50945 2008-04-05 15:20:20Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 50945 $"

from zope.viewlet import interfaces

class IEditletManager(interfaces.IViewletManager) :
    """ Content """
