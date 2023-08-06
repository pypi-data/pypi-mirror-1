### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definition of viewlet interface for
commonedit.html page.

$Id: interfaces.py 51050 2008-04-29 03:08:58Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51050 $"

from zope.viewlet import interfaces

class IEditletManager(interfaces.IViewletManager) :
    """ Content """
