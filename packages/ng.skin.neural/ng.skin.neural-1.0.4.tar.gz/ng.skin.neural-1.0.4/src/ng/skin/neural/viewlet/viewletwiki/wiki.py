# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: wiki.py 49701 2008-01-24 08:48:03Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49701 $"
__date__    = "$Date: 2008-01-24 11:48:03 +0300 (Чтв, 24 Янв 2008) $"

from zope.app.container.interfaces import IContainer
from zope.app import zapi 
import zope.app.catalog.interfaces
from urllib import quote

class Wiki(object) :
    """ Wiki """

    @property
    def length(self) :
        return len(list(zapi.getUtility(
                    zope.app.catalog.interfaces.ICatalog,
                    name="catalog",context=self.context). \
                    searchResults(backname={'any_of':(self.context.__name__,)})))

    @property
    def name(self) :
        return quote(str(self.context.__name__))
