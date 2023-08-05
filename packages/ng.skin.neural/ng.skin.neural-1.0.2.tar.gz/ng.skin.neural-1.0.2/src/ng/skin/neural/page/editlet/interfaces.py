# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: interfaces.py 49615 2008-01-21 13:07:36Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49615 $"
__date__ = "$Date: 2008-01-21 16:07:36 +0300 (Пнд, 21 Янв 2008) $"
__credits__ = """Andrey Orlov, for idea and common control"""

from zope.viewlet import interfaces

class IEditletManager(interfaces.IViewletManager) :
    """ Content """
