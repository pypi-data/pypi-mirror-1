# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: interfaces.py 52839 2009-04-06 17:03:12Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52839 $"


from ng.skin.base.interfaces import AuthSkin,RubricatorSkin, CommunitySkin,CommentSkin,BaseSkin
from zope.app.rotterdam import Rotterdam

class FreeYellowSkinBase(BaseSkin) :
    """Base Free Skin"""
    
class FreeYellowSkin(FreeYellowSkinBase,AuthSkin,RubricatorSkin,BaseSkin,Rotterdam):
    """Free Skin"""
