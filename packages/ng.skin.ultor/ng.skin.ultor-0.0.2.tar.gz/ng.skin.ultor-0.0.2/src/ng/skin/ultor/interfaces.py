# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: interfaces.py 52449 2009-02-02 17:53:16Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52449 $"

from ng.skin.base.interfaces import BaseSkin,RubricatorSkin,CommentSkin,AuthSkin
from zope.app.rotterdam import Rotterdam

class UltorSkin(BaseSkin,RubricatorSkin,CommentSkin,AuthSkin,Rotterdam):
    """Skin for for UltorLider
    """