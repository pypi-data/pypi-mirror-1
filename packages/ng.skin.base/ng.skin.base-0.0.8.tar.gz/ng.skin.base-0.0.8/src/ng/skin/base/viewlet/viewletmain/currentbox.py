### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for the viewlet display content of parent
container current object.

$Id: currentbox.py 51194 2008-06-26 14:03:08Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51194 $"

from zope.app.container.interfaces import  IContainer        
from zope.app.zapi import getUtility
from zope.app.zapi import getSiteManager
from zope.proxy import sameProxiedObjects
from ng.content.article.interfaces import IContentContainer

class CurrentBox(object) :
    """ Folder List """

    @property
    def values(self) :
        return IContentContainer(self.folder).values()
        
    @property
    def folder(self) :
        if sameProxiedObjects(self.context,getSiteManager(context=self.context).getUtility(IContainer, "Main")) :
            raise ValueError

        parent = self.context.__parent__
        if sameProxiedObjects(parent,getSiteManager(context=self.context).getUtility(IContainer, "Main")) :
            raise ValueError

        if sameProxiedObjects(parent,getSiteManager(context=self.context).getUtility(IContainer, "news")) :
            raise ValueError
            
        return parent
        
