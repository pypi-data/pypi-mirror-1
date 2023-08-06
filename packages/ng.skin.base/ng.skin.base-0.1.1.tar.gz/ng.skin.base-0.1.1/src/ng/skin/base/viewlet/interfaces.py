### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few viewlet provider.

$Id: interfaces.py 51952 2008-10-23 20:14:11Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51952 $"

from zope.viewlet import interfaces
from viewletmain.interfaces import INewsListBoxProvider, \
    ICurrentBoxProvider
from viewletsubscribe.interfaces import ISubscribeProvider

class IColumn( INewsListBoxProvider, 
    ICurrentBoxProvider, 
    ISubscribeProvider, 
    interfaces.IViewletManager) :
    """ Column viewlet provider """

class IAnnotations(interfaces.IViewletManager) :
    """ Annotations viewlet provider """


    