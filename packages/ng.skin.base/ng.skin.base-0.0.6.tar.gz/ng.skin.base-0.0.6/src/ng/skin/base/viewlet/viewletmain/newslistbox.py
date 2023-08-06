### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with last rss news

$Id: newslistbox.py 50945 2008-04-05 15:20:20Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 50945 $"


from mainbox import MainBox
from ng.app.objectqueue.interfaces import IObjectQueue

class NewsListBox(MainBox) :
    """ Folder List """

    foldername = "news"
    @property
    def values(self) :
        return IObjectQueue(self.folder).values()        

