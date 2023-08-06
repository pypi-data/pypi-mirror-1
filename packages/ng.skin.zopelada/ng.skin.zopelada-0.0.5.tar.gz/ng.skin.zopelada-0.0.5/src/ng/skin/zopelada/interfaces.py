# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: interfaces.py 52586 2009-02-12 08:26:52Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52586 $"

from ng.skin.base.interfaces import AuthSkin, RubricatorSkin, RemotefsSkin, CommentSkin, BaseSkin
from zope.app.rotterdam import Rotterdam

class ZopeLadaSkin(RemotefsSkin,BaseSkin,Rotterdam):
    """Skin for ZopeLada Ru"""# -*- coding: utf-8 -*-
