### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based viewroot package

$Id: interfaces.py 49764 2008-01-28 18:55:09Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49764 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Datetime
from zope.app.container.interfaces import IContained, IContainer
import datetime

class IRoot(Interface):
    """IRoot interface"""
    
    root = Field()