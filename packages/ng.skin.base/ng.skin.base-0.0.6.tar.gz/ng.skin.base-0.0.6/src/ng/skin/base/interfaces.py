### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of new skin interface

$Id: interfaces.py 50945 2008-04-05 15:20:20Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 50945 $"

from zope.app.rotterdam import Rotterdam
from zope.interface import Interface

class BaseSkin(Interface) :
    """ Basic Skin """
    
class NGBaseSkin(BaseSkin, Rotterdam) :
    """ Basic skin with Rotterdam """
    