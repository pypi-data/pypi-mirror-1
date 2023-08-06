### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with last rss news

$Id: article.py 50785 2008-02-20 16:37:28Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 50785 $"


from ng.skin.base.viewlet.viewletmain.mainbox import MainBox
from ng.app.objectqueue.interfaces import IObjectQueue

class ArticleBox(MainBox) :
    """ Folder List """

    foldername = "article"
    @property
    def values(self) :
        return IObjectQueue(self.folder).values()        

