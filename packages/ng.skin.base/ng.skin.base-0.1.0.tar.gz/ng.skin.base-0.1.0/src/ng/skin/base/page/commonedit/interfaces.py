### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definition of viewlet interface for
commonedit.html page.

$Id: interfaces.py 51888 2008-10-21 07:10:48Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51888 $"

from zope.viewlet import interfaces
from zope.schema import TextLine, Choice, Tuple, Int, Datetime, Set

from ng.content.annotation.profileannotation.interfaces import IProfileAnnotation
from ng.app.rubricator.tag.tagvocabulary.tagvocabulary import TagVocabulary

class IEditletManager(interfaces.IViewletManager) :
    """ Content """

class IProfileAnnotation(IProfileAnnotation) :

    interests = Set(title=u'Interests',
                  description=u'Your interest areas',
                  value_type = Choice(source = TagVocabulary()),
                  required=False,
                  )
 
    
    