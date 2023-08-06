### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with last rss news

$Id: newslistbox.py 50545 2008-02-06 09:00:53Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"


from ng.skin.base.viewlet.viewletmain.mainbox import MainBox
from ng.app.objectqueue.interfaces import IObjectQueue

class ArticleBox(MainBox) :
    """ Folder List """

    foldername = "article"
    @property
    def values(self) :
        return IObjectQueue(self.folder).values()        

