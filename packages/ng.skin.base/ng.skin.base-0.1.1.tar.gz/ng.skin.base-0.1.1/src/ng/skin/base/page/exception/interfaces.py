### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of exceptiion

$Id: interfaces.py 51952 2008-10-23 20:14:11Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from zope.interface import Interface
from zope.schema import URI

class IRedirectException(Interface) :
    """ Basic Skin """

    url = URI(title=u"Redirect url")    