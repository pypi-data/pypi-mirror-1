# -*- coding: utf-8 -*-
"""The searchpage MixIn to view class.

$Id: dictionary.py 49615 2008-01-21 13:07:36Z cray $
"""
__author__  = "Andrey Orlov 2006 12 05"
__license__ = "GPL"
__version__ = "$Revision: 49615 $"
__date__ = "$Date: 2008-01-21 16:07:36 +0300 (Пнд, 21 Янв 2008) $"
__credits__ = """Andrey Orlov, for idea and common control"""

import zope.component
from zope.app import zapi
from zope.app.catalog.interfaces import ICatalog
from zope.traversing.browser.absoluteurl import absoluteURL
from zc.catalog.interfaces import IIndexValues

class Dictionary(object) :
    
    def __init__(self,context,request) :
        super(Dictionary,self).__init__(context,request)
        

    def words(self) :
        return (x for x in sorted(zapi.getUtility(IIndexValues, 'keyword', context=self.context).values()) if x)
        
    def articlebyword(self,word) :
        return zapi.getUtility(
                    zope.app.catalog.interfaces.ICatalog,
                    name="catalog",context=self.context).searchResults(keyword={'all_of':(word,)})

                    
        
