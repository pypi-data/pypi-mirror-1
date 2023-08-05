# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: interfaces.py 49797 2008-01-29 22:52:29Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49797 $"
__date__ = "$Date: 2008-01-30 01:52:29 +0300 (Срд, 30 Янв 2008) $"
__credits__ = """Andrey Orlov, for idea and common control"""

from zope.viewlet import interfaces

class IContent(interfaces.IViewletManager) :
    """ Content """
