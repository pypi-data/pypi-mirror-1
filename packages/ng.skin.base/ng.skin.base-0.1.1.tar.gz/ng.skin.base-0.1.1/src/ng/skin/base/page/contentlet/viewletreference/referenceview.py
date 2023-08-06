### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for reference viewlet

$Id: referenceview.py 51952 2008-10-23 20:14:11Z cray $
"""
__author__  = "Andrey Orlov,2007"
__license__ = "GPL"
__version__ = "$Revision: 51952 $"

from ks.reference.referenceannotation.interfaces import IReferenceTuple
from ng.skin.base.page.contentlet.viewletbase import ViewletBase

class Reference(ViewletBase) :
    """ Reference """
    def __init__(self,*kv,**kw) :
        super(Reference,self).__init__(*kv,**kw)

    @property
    def islink(self) :
        return bool(self.forward) or bool(self.backward)

    @property
    def forward(self) :
        return IReferenceTuple(self.context).items(self.context)

    @property
    def backward(self) :
        return IReferenceTuple(self.context).items(self.context,backward=True)
        
        