### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based viewnextpprev package

$Id: interfaces.py 49764 2008-01-28 18:55:09Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49764 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Datetime
from zope.app.container.interfaces import IContained, IContainer
import datetime
from zope.app.container.interfaces import INameChooser

class INextPrev(Interface):
    """Next-Previous interface"""
    
    prev = Field(title = u'Previous Object')

    next = Field(title = u'Next Object')

    up   = Field(title = u'Upper Object')            
