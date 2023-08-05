# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: viewletbackref.py 49797 2008-01-29 22:52:29Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49797 $"
__date__    = "$Date: 2008-01-30 01:52:29 +0300 (Срд, 30 Янв 2008) $"

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
                                