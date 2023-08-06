### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for content viewlet

$Id: contenticons.py 52321 2009-01-13 13:43:00Z corbeau $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 52321 $"

from ng.lib.viewletbase import ViewletBase
from ng.content.article.interfaces import IIconContainer

class ContentIcons(ViewletBase) :
    """ Content """

    @property
    def images(self) :
        
        return IIconContainer(self.context).values()
