### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few viewlet provider.

$Id: interfaces.py 50945 2008-04-05 15:20:20Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50945 $"

from zope.viewlet import interfaces

class IColumn(interfaces.IViewletManager) :
    """ Column viewlet"""

class IAnnotations(interfaces.IViewletManager) :
    """ Annotations viewlet """


    