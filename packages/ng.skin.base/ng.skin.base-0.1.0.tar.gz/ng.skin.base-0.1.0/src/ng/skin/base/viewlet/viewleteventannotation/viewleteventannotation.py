### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for eventannotation viewlet

$Id: viewleteventannotation.py 51888 2008-10-21 07:10:48Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51888 $"
 
from ng.content.annotation.eventannotation.interfaces import IEventAnnotation 

class EventAnnotationViewlet(object) :
    def __init__(self,*kv,**kw) :
        super(EventAnnotationViewlet,self).__init__(*kv,**kw)
        self.context = IEventAnnotation(self.context.ob)
               


