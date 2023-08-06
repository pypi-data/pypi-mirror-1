### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few viewlet provider.

$Id: interfaces.py 51050 2008-04-29 03:08:58Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51050 $"

from zope.viewlet import interfaces

class IColumn(interfaces.IViewletManager) :
    """ Column viewlet"""

class IAnnotations(interfaces.IViewletManager) :
    """ Annotations viewlet """


    