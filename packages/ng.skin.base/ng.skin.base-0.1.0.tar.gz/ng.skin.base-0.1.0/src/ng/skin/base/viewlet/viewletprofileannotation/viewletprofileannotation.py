### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for profileannotation viewlet

$Id: viewletprofileannotation.py 51888 2008-10-21 07:10:48Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50943 $"
 
from ng.content.annotation.profileannotation.interfaces import IProfileAnnotation 

class ProfileAnnotationViewlet(object) :
    def __init__(self,*kv,**kw) :
        super(ProfileAnnotationViewlet,self).__init__(*kv,**kw)
        self.parent = self.context
        self.context = IProfileAnnotation(self.context)
        


