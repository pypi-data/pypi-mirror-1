# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id$
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision$"

from ng.skin.base.interfaces import AuthSkin, RubricatorSkin, RemotefsSkin, CommentSkin, BaseSkin
from zope.app.rotterdam import Rotterdam

class NeuralSkin(RemotefsSkin,BaseSkin,Rotterdam):
    """Skin for Neural Ru"""
    
