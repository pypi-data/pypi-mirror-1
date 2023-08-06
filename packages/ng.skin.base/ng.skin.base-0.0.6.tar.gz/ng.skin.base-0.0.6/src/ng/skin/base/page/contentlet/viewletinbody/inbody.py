### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for inbody viewlet 

$Id: inbody.py 50945 2008-04-05 15:20:20Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 50945 $"

from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from ng.skin.base.page.contentlet.viewletbase import ViewletBase

class InBody(ViewletBase) :
    """ Body """
    
    isobject = False
    def __init__(self,*kv,**kw) :
        super(InBody,self).__init__(*kv,**kw)
        items = self.context.values()
            