### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based viewroot package

$Id: interfaces.py 49689 2008-01-23 14:39:53Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49689 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Datetime
from zope.app.container.interfaces import IContained, IContainer
import datetime

class IRoot(Interface):
    """IRoot interface"""
    
    root = Field()