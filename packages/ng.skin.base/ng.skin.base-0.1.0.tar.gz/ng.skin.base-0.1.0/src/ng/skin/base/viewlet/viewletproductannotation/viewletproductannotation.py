### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for productannotation viewlet

$Id: viewletproductannotation.py 51888 2008-10-21 07:10:48Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51888 $"
 
from ng.content.annotation.productannotation.interfaces import IProductAnnotation 

class ProductAnnotationViewlet(object) :
    def __init__(self,*kv,**kw) :
        super(ProductAnnotationViewlet,self).__init__(*kv,**kw)
        self.parent = self.context
        self.context = IProductAnnotation(self.context.ob)
               


