### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The newspage MixIn to view class.

$Id: linkview.py 51888 2008-10-21 07:10:48Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51888 $"

from ng.app.rubricator.algorithm.base.interfaces import IRubricateAble
from docshortview import Proxy

class LinkView(object):
    
    def __init__(self,context,request) :
        self.request = request
        super(LinkView, self).__init__(context, request)
        self.context = Proxy(IRubricateAble(context))

            