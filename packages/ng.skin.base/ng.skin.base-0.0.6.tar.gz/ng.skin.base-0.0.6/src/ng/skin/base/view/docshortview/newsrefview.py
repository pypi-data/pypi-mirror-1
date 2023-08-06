### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The newspage MixIn to view class.

$Id: newsrefview.py 50945 2008-04-05 15:20:20Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50945 $"

from ng.app.rubricator.interfaces import IRubricateAble
from docshortview import Proxy

class NewsRefView(object):
    
    def __init__(self,context,request) :
        self.request = request
        super(NewsRefView, self).__init__(context, request)
        self.context = Proxy(IRubricateAble(context))

            