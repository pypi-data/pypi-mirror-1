### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few viewlet provider.

$Id: interfaces.py 50807 2008-02-21 11:53:14Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50807 $"

from zope.viewlet import interfaces

class IColumn(interfaces.IViewletManager) :
    """ Column viewlet"""

class IAnnotations(interfaces.IViewletManager) :
    """ Annotations viewlet """


    