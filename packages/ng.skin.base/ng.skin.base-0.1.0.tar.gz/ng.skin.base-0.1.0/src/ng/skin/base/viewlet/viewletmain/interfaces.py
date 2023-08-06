### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few special interfaces used to bind viewlet provider
and viewlet content

$Id: interfaces.py 51888 2008-10-21 07:10:48Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51888 $"

from zope.viewlet import interfaces
from zope.interface import Interface

class INewsListBoxProvider(Interface) :
    """ Interface of newslistbox provider """

class ICommonNewsListBoxProvider(Interface) :
    """ Interface of newslistbox provider """

class ICurrentBoxProvider(Interface) :
    """ Interface of currentbox provider """

    