### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Main view adapter class

$Id: main.py 51050 2008-04-29 03:08:58Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51050 $"

from zope.publisher.browser import BrowserView    
from zope.app.container.interfaces import IContainer
from zope.app.zapi import getSiteManager

def getMain(context,request) :
    return getSiteManager(context=context) \
            .getUtility(IContainer, 'Main')

