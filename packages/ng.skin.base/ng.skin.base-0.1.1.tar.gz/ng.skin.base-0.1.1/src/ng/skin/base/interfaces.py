### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of new skin interface

$Id: interfaces.py 51952 2008-10-23 20:14:11Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51952 $"

from zope.app.rotterdam import Rotterdam
from zope.interface import Interface

class BaseSkin(Interface) :
    """ Basic Skin """
    
class NGBaseSkin(BaseSkin, Rotterdam) :
    """ Basic skin with Rotterdam """
    