### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with last rss news

$Id: idea.py 52431 2009-01-31 16:38:16Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 52431 $"


from ng.skin.base.viewlet.viewletmain.mainbox import MainBox
from ng.app.objectqueue.interfaces import IObjectQueue
import sys

class IdeaBox(MainBox) :
    """ Folder List """

    foldername = "idea"
    @property
    def values(self) :
        try :
            return IObjectQueue(self.folder).values()        
        except Exception:
            print sys.excepthook(*sys.exc_info())            

