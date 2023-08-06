# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: interfaces.py 52569 2009-02-11 20:09:26Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52569 $"

from ng.skin.base.interfaces import AuthSkin,RubricatorSkin, CommunitySkin,CommentSkin,BaseSkin
from zope.app.rotterdam import Rotterdam

class NPCLiderSkin(AuthSkin,RubricatorSkin,BaseSkin,Rotterdam):
    """Skin for for NPCLider"""
