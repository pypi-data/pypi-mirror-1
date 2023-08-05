# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: interfaces.py 49764 2008-01-28 18:55:09Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49764 $"
__date__ = "$Date: 2008-01-28 21:55:09 +0300 (Пнд, 28 Янв 2008) $"
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
    