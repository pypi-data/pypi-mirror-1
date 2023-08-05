# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: wiki.py 49797 2008-01-29 22:52:29Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49797 $"
__date__    = "$Date: 2008-01-30 01:52:29 +0300 (Срд, 30 Янв 2008) $"

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
