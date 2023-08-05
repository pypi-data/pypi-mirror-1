### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of new skin interface

$Id: interfaces.py 50807 2008-02-21 11:53:14Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 50807 $"

from zope.app.rotterdam import Rotterdam
from zope.interface import Interface

class BaseSkin(Interface) :
    """ Basic Skin """
    
class NGBaseSkin(BaseSkin, Rotterdam) :
    """ Basic skin with Rotterdam """
    