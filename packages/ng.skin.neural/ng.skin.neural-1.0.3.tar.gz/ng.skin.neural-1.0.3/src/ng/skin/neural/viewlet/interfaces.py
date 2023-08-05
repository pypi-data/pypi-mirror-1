# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: interfaces.py 49689 2008-01-23 14:39:53Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49689 $"
__date__ = "$Date: 2008-01-23 17:39:53 +0300 (Срд, 23 Янв 2008) $"
__credits__ = """Andrey Orlov, for idea and common control"""

from zope.viewlet import interfaces

class IColumn(interfaces.IViewletManager) :
    """ Column """

class IAdmin(interfaces.IViewletManager) :
    """ Admin """

class IHeader(interfaces.IViewletManager) :
    """ Header """

class IBody(interfaces.IViewletManager) :
    """ Body """
    