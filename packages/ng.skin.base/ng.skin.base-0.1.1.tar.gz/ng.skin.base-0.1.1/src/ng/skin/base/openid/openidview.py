### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for the OpenId view

$Id: openidview.py 51952 2008-10-23 20:14:11Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51952 $"

from zope.interface import Interface
from zope.publisher.browser import BrowserView
from openid.consumer.consumer import Consumer
from openid.consumer.consumer import FAILURE, SUCCESS, CANCEL, SETUP_NEEDED
from openid.store.memstore import MemoryStore
from zope.traversing.browser import absoluteURL
session = {}
store = MemoryStore()
        
class OpenIDView(BrowserView) :

    def openid(self) :
        self.consumer = Consumer(session, store)
        print session
        try :
            self.authrequest = self.consumer.begin(self.request.form['openid'])    
        except KeyError :
            return "None"
        else :
            self.request.response.redirect(
                self.authrequest.redirectURL(
                    absoluteURL(self.context,self.request),
                    absoluteURL(self.context,self.request) + "/@@openid2.html"
                    )
                )
            print session                
            return "Exist"
                    
class OpenIDView2(BrowserView) :

    def openid(self) :
        self.consumer = Consumer(session, store)
        print session
        print type(self.request.form)
        res = self.consumer.complete(
            self.request.form, 
            absoluteURL(self.context,self.request) + "/@@openid2.html"
            )
            
        if res.status == SUCCESS :
            print res.signed_fields
            print res.message
            print res.getDisplayIdentifier()
            return "OK: " + res.identity_url             
        return "Access Denied"
        
