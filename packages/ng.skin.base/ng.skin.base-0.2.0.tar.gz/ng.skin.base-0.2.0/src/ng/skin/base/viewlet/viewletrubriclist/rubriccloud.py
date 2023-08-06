### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with list of rubric

$Id: rubriccloud.py 52446 2009-02-02 13:41:19Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52446 $"


from rubriclist import RubricList
from pd.lib.linear_quantizator import quantizator, mapper
from zope.app.zapi import getUtility
from ng.app.link.linkbackreference.interfaces import ILinkBackReference, ILinkBackReferenceContainer
from zope.app.intid.interfaces import IIntIds
from ng.lib.viewletbase import ViewletBase

class RubricCloudBase(object) :
    @property
    def values(self) :
        return (x for x,y in self._values)

    @property
    def records(self) :
        return ( {'value':x, 'class':str(y)} for x,y in self._values)

    @property
    def _values(self) :
        return reversed(mapper(quantizator([ (x,len(x)) for x in super(RubricCloudBase,self).values ],6),7))
        
class RubricCloud(RubricCloudBase,RubricList) :
    """ Cloud of rubric for this object
    """

class RubricAllCloudBase(object) :
    @property
    def values(self) :
        brf = getUtility(ILinkBackReference,context=self.context)
        intid = getUtility(IIntIds, brf.newsRefId)
        s = set()
        for items in ILinkBackReferenceContainer(brf) .values() :
            for item in items :
                rubric = intid.getObject(int(item[1:])).__parent__
                rid = intid.getId(rubric)
                if rid not in s :
                    s.update([rid])
                    yield rubric


class RubricAllCloud(RubricCloudBase,RubricAllCloudBase,ViewletBase) :
    """ Cloud of all rubric for this object """