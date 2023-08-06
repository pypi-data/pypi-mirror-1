### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for the viewlet display content of parent
container current object.

$Id: currentbox.py 53268 2009-06-13 06:44:19Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 53268 $"

from zope.app.container.interfaces import  IContainer        
from zope.app.zapi import getUtility
from zope.app.zapi import getSiteManager
from zope.proxy import sameProxiedObjects
from ng.content.article.interfaces import IContentContainer
from ng.lib.viewletbase import ViewletBase
from ng.app.registry.interfaces import IRegistry

class CurrentBox(ViewletBase) :
    """ Folder List """

    @property
    def values(self) :
        return IContentContainer(self.folder).values()
        
    @property
    def folder(self) :
        if sameProxiedObjects(self.context,getSiteManager(context=self.context).getUtility(IContainer, "Main")) :
            raise ValueError

        parent = self.context.__parent__

        for name in IRegistry(self.context).param("currentbox_disabled_on","").split() + ["Main","news"]:
            if sameProxiedObjects(parent,getSiteManager(context=self.context).getUtility(IContainer, name)) :
                raise ValueError

        return parent
        
