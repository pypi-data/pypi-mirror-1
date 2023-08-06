### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Class for robots page view.

$Id: robots.py 51952 2008-10-23 20:14:11Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

import zope.component
from ng.app.registry.interfaces import IRegistry

class Robots(object) :
    
    def __init__(self,context,request) :
        super(Robots,self).__init__(context,request)
        

    def __call__(self) :
        self.request.response.setHeader("Content-Type","text/plain")
        return IRegistry(self.context).param("robots","User-agent: *\nAllow: /\n" )

                    
        
