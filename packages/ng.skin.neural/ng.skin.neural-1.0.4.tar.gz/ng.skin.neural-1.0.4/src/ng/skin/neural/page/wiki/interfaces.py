### -*- coding: utf-8 -*- #############################################
"""Interfaces for the Zope 3 based article package

$Id: interfaces.py 49701 2008-01-24 08:48:03Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49701 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Bool, URI, Datetime, Object
from ng.content.article.interfaces import IDocShortLogo

class IDictionaryItem(IDocShortLogo) :
    """ Attributes of article class """
    keyword = Text(title = u'Keywords',
        description = u'Keywords for article',
        default = u'',
        required = True)
                                  
class IArticleByName(IDocShortLogo) :
    """ Attributes of article class """
    name = TextLine(title = u'Article Name',
        description = u'Article Name',
        default = u'',
        required = True)
                                  
    