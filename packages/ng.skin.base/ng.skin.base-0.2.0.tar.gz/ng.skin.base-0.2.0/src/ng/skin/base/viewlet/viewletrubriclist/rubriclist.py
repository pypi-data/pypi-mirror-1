### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with list of rubric

$Id: rubriclist.py 52399 2009-01-27 14:36:50Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52399 $"


from zope.app.zapi import getUtility
from ng.app.link.linkbackreference.interfaces import ILinkBackReference
from zope.app.intid.interfaces import IIntIds
from ng.lib.viewletbase import ViewletBase

class RubricList(ViewletBase) :
    """ List of rubric for this object
    """

    @property
    def values(self) :
        brf = getUtility(ILinkBackReference,context=self.context)
        intid = getUtility(IIntIds, brf.newsRefId)
        for item in brf["c%016u" % intid.getId(self.context)] :
            yield intid.getObject(int(item[1:])).__parent__
