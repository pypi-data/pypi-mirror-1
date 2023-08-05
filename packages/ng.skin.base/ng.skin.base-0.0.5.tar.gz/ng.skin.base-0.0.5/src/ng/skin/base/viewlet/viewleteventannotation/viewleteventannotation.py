### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for eventannotation viewlet

$Id: viewleteventannotation.py 50807 2008-02-21 11:53:14Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50807 $"
 
from ng.content.annotation.eventannotation.interfaces import IEventAnnotation 

class EventAnnotationViewlet(object) :
    def __init__(self,*kv,**kw) :
        super(EventAnnotationViewlet,self).__init__(*kv,**kw)
        self.context = IEventAnnotation(self.context.ob)
               


