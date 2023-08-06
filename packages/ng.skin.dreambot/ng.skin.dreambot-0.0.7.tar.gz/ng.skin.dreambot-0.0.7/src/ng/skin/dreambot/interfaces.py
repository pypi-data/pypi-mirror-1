# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: interfaces.py 52582 2009-02-12 08:25:51Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52582 $"

from ng.skin.base.interfaces import AuthSkin, RubricatorSkin, RemotefsSkin, CommentSkin,BaseSkin
from zope.app.rotterdam import Rotterdam

class DreamBotSkin(RemotefsSkin,BaseSkin,Rotterdam):
    """Skin for DreamBot Ru"""
    
