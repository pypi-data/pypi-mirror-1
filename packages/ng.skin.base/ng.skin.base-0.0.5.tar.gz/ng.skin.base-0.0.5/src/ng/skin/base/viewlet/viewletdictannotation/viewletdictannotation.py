### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for dictannotation viewlet

$Id: viewletdictannotation.py 50807 2008-02-21 11:53:14Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50807 $"
 
from ng.content.annotation.dictannotation.interfaces import IDictAnnotation 

class DictAnnotationViewlet(object) :
    def __init__(self,*kv,**kw) :
        super(DictAnnotationViewlet,self).__init__(*kv,**kw)
        self.context = IDictAnnotation(self.context.ob)
        


