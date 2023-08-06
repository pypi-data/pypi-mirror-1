### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-In class for the views of remote container.

$Id: remotecontainerview.py 51050 2008-04-29 03:08:58Z cray $
"""
__author__  = "Andrey Orlov,2007"
__license__ = "GPL"
__version__ = "$Revision: 51050 $"
 
from zope.interface import Interface
from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from zope.publisher.browser import BrowserView
        
class Proxy(object) :
    def __init__(self,ob) :
        self.ob = ob
        self.ps = IPropertySheet(ob)
                        
    @property
    def title(self) :
        return self.ps['title'] or self.ob.__name__
        
    def __getattr__(self,name) :
        return getattr(self.ob,name)
        
class RemoteContainerView(BrowserView) :
    def __init__(self,*kv,**kw) :
        super(RemoteContainerView,self).__init__(*kv,**kw)
        self.context = Proxy(self.context)
        
