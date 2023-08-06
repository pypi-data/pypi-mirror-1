### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Base class for all viewlet in contentlet page.

$Id: viewletbase.py 51213 2008-06-30 12:42:36Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 51213 $"

class ViewletBase(object) :
    """ Body """

    order = 0 
    
    def __init__(self,context,request,*kv,**kw) :
        self.context = context
        self.request = request
        self.order = int(str(self.order))
        super(ViewletBase,self).__init__(context,request,*kv,**kw)

    def __cmp__(self,x) :
        return cmp(self.order,x.order)        
        