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
import sys

class IdeaBox(MainBox) :
    """ Folder List """

    foldername = "idea"
    @property
    def values(self) :
        print 1
        try :
            return IObjectQueue(self.folder).values()        
        except Exception:
            print sys.excepthook(*sys.exc_info())            

