### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Base class for a few viewlet display different folderish content
as menu.

$Id: mainbox.py 51952 2008-10-23 20:14:11Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51952 $"

from zope.app.container.interfaces import IContainer
from zope.app.zapi import getSiteManager
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
        
class MainBox(object) :
    """ Folder List """

    template = ViewPageTemplateFile("mainbox.pt")
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