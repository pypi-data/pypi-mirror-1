### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few viewlet provider.

$Id: interfaces.py 52446 2009-02-02 13:41:19Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52446 $"

from zope.viewlet import interfaces
from viewletmain.interfaces import INewsListBoxProvider, \
    ICurrentBoxProvider
from viewletsubscribe.interfaces import ISubscribeProvider
from viewletloginbox.interfaces import ILoginBoxProvider
from viewletrubriclist.interfaces import IRubricListProvider,IRubricCloudProvider,IRubricAllCloudProvider

class IColumn( 
    INewsListBoxProvider, 
    ICurrentBoxProvider, 
    ISubscribeProvider,
    ILoginBoxProvider, 
    IRubricListProvider,
    IRubricCloudProvider,
    IRubricAllCloudProvider,
    interfaces.IViewletManager) :
    """ Column viewlet provider """

class IAnnotations(interfaces.IViewletManager) :
    """ Annotations viewlet provider """


    