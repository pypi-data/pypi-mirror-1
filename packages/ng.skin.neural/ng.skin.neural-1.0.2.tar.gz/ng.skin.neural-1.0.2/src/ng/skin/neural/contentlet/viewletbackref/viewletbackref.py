# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: viewletbackref.py 49615 2008-01-21 13:07:36Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49615 $"
__date__    = "$Date: 2008-01-21 16:07:36 +0300 (Пнд, 21 Янв 2008) $"

from ng.site.content.search.interfaces import ISearchKeyword,ISearchName
from zope.app import zapi 
import zope.app.catalog.interfaces

class ViewletBackRef(object) :
    """ Wiki """

    @property
    def backref(self) :
        try :
            keyword = ISearchKeyword(self.context).keyword
        except TypeError :
            pass
        else :                        
            for item in zapi.getUtility(
                    zope.app.catalog.interfaces.ICatalog,
                    name="catalog",context=self.context). \
                    searchResults(backkeyword={'any_of':keyword}) :
                yield item                    
                    
        for item in zapi.getUtility(
                    zope.app.catalog.interfaces.ICatalog,
                    name="catalog",context=self.context). \
                    searchResults(backname={'any_of':ISearchName(self.context).name}) :
            yield item
                                