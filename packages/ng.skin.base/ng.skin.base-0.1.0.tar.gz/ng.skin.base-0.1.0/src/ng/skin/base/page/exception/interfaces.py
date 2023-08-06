### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of exceptiion

$Id: interfaces.py 51888 2008-10-21 07:10:48Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from zope.interface import Interface
from zope.schema import URI

class IRedirectException(Interface) :
    """ Basic Skin """

    url = URI(title=u"Redirect url")    