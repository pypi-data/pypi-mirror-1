### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for add form to redirect on @@commonedit.html

$Id: imageadd.py 52328 2009-01-13 17:59:09Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from nexturl import NextUrl
from zope.app.file.browser.image import ImageAdd 

class ImageAdd(ImageAdd,NextUrl) :
    """ Content """

