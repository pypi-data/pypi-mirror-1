### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ErrorView - is base class for zope3 errors

$Id: redirectexception.py 51952 2008-10-23 20:14:11Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49544 $"


from zope.interface import implements
from interfaces import IRedirectException

class RedirectException(Exception) :
    implements(IRedirectException)
    
    url = ""
    
    def __init__(self,url) :
        self.url = url
        