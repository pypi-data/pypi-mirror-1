### -*- coding: utf-8 -*- #############################################
#######################################################################
""" Special widgets for photosequence adding page

$Id: addimagesequence.py 52421 2009-01-31 15:40:52Z cray $
"""
__author__  = u"Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 52421 $"

from zope.app.form import CustomWidgetFactory
from ng.lib.objectwidget import ObjectWidget
from zope.app.form.browser import TupleSequenceWidget
from interfaces import IPhotoItem
from zope.interface import implements
from ng.app.photo.photo import Photo
from ng.content.article.interfaces import IDocShort 
from zope.app.zapi import absoluteURL
from zope.app.container.interfaces import INameChooser

class AddImageSequence(object) :
    def getData(self,*kv,**kw) :
        return (('photos',()),('ishidden',False))
        
    def setData(self,d,**kw) :
        count = -1
        for image in d['photos'] :
            count += 1
            if not image.data :
                continue
                
            filename = getattr(self.request.form['field.photos.%u.data' % count],"filename",None)
            photo = Photo()
            #photo.__parent__ = self.context
            #photo.__name__ = 'qq'
            #if image.title :
            #    filename = unicode(image.title)
            self.context[INameChooser(self.context).chooseName(filename,Photo)] = photo
            IDocShort(photo).title = unicode(image.title)
            IDocShort(photo).abstract = unicode(image.abstract)
            IDocShort(photo).ishidden = d['ishidden']
            photo.data = image.data

        self.request.response.redirect(absoluteURL(self.context,self.request))
        return True


class PhotoItem(object) :
    implements(IPhotoItem)
    title = None
    data = None

PhotoItemTupleWidget = CustomWidgetFactory(
   TupleSequenceWidget,
   subwidget=CustomWidgetFactory(
                    ObjectWidget,
                    PhotoItem
                    ))


