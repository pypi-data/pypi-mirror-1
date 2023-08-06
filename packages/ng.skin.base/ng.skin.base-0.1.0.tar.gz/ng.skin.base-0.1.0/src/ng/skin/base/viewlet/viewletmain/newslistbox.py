### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with last rss news

$Id: newslistbox.py 51888 2008-10-21 07:10:48Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 51888 $"


from mainbox import MainBox
from ng.app.objectqueue.interfaces import IObjectQueue

class NewsListBox(MainBox) :
    """ Folder List """

    foldername = "news"
    @property
    def values(self) :
        return IObjectQueue(self.folder).values()        

class CommonNewsListBox(NewsListBox) :
    """ Folder List """

    foldername = "Main"

