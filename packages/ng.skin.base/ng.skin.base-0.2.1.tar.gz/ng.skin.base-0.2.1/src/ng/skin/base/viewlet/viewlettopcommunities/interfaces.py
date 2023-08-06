### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.skin.greenpsy package

$Id: interfaces.py 52345 2009-01-15 12:22:29Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52345 $"
 
from zope.interface import Interface

class ITopCommunitiesBoxProvider(Interface) :
    """ Interface for TopCommunitiesBox provider
    """
