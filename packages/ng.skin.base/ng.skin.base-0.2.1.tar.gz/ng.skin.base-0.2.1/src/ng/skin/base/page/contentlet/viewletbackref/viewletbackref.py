### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for backreference viewlet.

$Id: viewletbackref.py 52240 2008-12-29 00:25:58Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 52240 $"

from ng.site.content.search.interfaces import ISearch, ISearchName
from zope.app import zapi 
import zope.app.catalog.interfaces
from ng.lib.viewletbase import ViewletBase

class ViewletBackRef(ViewletBase) :
    """ Wiki """

    @property
    def backref(self) :
        try :
            keyword = ISearch(self.context).keyword
        except TypeError,msg :
            pass
        else :  
            for item in zapi.getUtility(
                    zope.app.catalog.interfaces.ICatalog,
                    context=self.context). \
                    searchResults(backkeyword={'any_of':keyword}) :
                yield item                    
                    
        for item in zapi.getUtility(
                    zope.app.catalog.interfaces.ICatalog,
                    context=self.context). \
                    searchResults(backname={'any_of':ISearchName(self.context).name}) :
            yield item
                                