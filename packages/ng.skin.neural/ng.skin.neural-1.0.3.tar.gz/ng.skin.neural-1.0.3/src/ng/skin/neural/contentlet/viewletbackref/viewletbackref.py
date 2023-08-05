# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: viewletbackref.py 49689 2008-01-23 14:39:53Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49689 $"
__date__    = "$Date: 2008-01-23 17:39:53 +0300 (Срд, 23 Янв 2008) $"

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
                                