### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of new skin interface

$Id: interfaces.py 51194 2008-06-26 14:03:08Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51194 $"

from zope.app.rotterdam import Rotterdam
from zope.interface import Interface

class BaseSkin(Interface) :
    """ Basic Skin """
    
class NGBaseSkin(BaseSkin, Rotterdam) :
    """ Basic skin with Rotterdam """
    