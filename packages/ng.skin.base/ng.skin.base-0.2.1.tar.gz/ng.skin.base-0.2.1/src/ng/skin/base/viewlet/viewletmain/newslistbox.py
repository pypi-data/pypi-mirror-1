### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with last rss news

$Id: newslistbox.py 52421 2009-01-31 15:40:52Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 52421 $"


from mainbox import MainBox
from ng.app.objectqueue.interfaces import IObjectQueue

class NewsListBox(MainBox) :
    """ Folder List """

    foldername = "news"
    registry = "news"
    
    def _values(self) :
        return IObjectQueue(self.folder).values()        

