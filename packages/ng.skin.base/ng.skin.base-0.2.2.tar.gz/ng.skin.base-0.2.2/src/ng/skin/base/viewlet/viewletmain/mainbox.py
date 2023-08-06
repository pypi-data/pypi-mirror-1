### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Base class for a few viewlet display different folderish content
as menu.

$Id: mainbox.py 52841 2009-04-06 18:01:31Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 52841 $"

from zope.app.container.interfaces import IContainer
from zope.app.zapi import getSiteManager
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from ng.lib.viewletbase import ViewletBase
from ng.app.registry.interfaces import IRegistry
        
class MainBox(ViewletBase) :
    """ Folder List """

    template = ViewPageTemplateFile("mainbox.pt")
    foldername = "Main"
    folderinterface = IContainer
    size = None
    registry = ""
        

    @property
    def values(self) :
        l = self._values()
        size = IRegistry(self.context).param( 'menu_' + self.registry + 'size', self.size )
        if size :
            return l[:size]
        else :
            return l

    def _values(self) :
        return self.folder.values()

    @property
    def folder(self) :
        return getSiteManager(context=self.context) \
                .getUtility(self.folderinterface, self.foldername)
                
