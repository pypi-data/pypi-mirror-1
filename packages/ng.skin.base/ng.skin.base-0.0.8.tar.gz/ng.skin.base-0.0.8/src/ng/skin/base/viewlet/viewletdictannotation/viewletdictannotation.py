### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for dictannotation viewlet

$Id: viewletdictannotation.py 51194 2008-06-26 14:03:08Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51194 $"
 
from ng.content.annotation.dictannotation.interfaces import IDictAnnotation 

class DictAnnotationViewlet(object) :
    def __init__(self,*kv,**kw) :
        super(DictAnnotationViewlet,self).__init__(*kv,**kw)
        self.parent = self.context
        self.context = IDictAnnotation(self.context.ob)
        


