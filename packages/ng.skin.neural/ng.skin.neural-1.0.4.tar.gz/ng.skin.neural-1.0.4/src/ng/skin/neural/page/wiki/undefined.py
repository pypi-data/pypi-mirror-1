### -*- coding: utf-8 -*- #############################################
"""Undefined page provide list all references on unknown documents

$Id: undefined.py 49701 2008-01-24 08:48:03Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49701 $"
 
from zope.interface import implements
from zc.catalog.interfaces import IIndexValues
from zope.app.catalog.interfaces import ICatalog
from zope.app.zapi import getUtility

class UnDefined(object) :

    def undefined(self,backindexname,indexname) :
        index = getUtility(IIndexValues, context=self.context, name=backindexname)
        catalog = getUtility(ICatalog,context=self.context, name='catalog')
        for keyword in index.values() :
            if len(catalog.searchResults(**{indexname:{'any_of':(keyword,keyword)}})) == 0 :
                yield {
                    'keyword' : keyword, 
                    'document' : catalog.searchResults(**{backindexname:{'any_of':(keyword,keyword)}})
                    }
            
    
    @property
    def keyword(self) :
        return self.undefined('backkeyword','keyword')
                    
    @property
    def name(self) :
        return self.undefined('backname','name')            
            

    
    