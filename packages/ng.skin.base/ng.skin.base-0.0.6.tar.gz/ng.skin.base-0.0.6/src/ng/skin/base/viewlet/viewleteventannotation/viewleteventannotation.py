### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for eventannotation viewlet

$Id: viewleteventannotation.py 50945 2008-04-05 15:20:20Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50945 $"
 
from ng.content.annotation.eventannotation.interfaces import IEventAnnotation 

class EventAnnotationViewlet(object) :
    def __init__(self,*kv,**kw) :
        super(EventAnnotationViewlet,self).__init__(*kv,**kw)
        self.context = IEventAnnotation(self.context.ob)
               


