### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The newspage MixIn to view class.

$Id: newsrefview.py 51213 2008-06-30 12:42:36Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51213 $"

from ng.app.rubricator.interfaces import IRubricateAble
from docshortview import Proxy

class NewsRefView(object):
    
    def __init__(self,context,request) :
        self.request = request
        super(NewsRefView, self).__init__(context, request)
        self.context = Proxy(IRubricateAble(context))

            