### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Base class for a few viewlet display different folderish content
as menu.

$Id: mainbox.py 50945 2008-04-05 15:20:20Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 50945 $"

from zope.app.container.interfaces import IContainer
from zope.app.zapi import getSiteManager

class MainBox(object) :
    """ Folder List """

    foldername = "Main"
    folderinterface = IContainer
    order = 0

    @property
    def values(self) :
        return self.folder.values()

    @property
    def folder(self) :
        return getSiteManager(context=self.context) \
                .getUtility(self.folderinterface, self.foldername)
                
    def __cmp__(self,ob) :
        return cmp(self.order,ob.order)                