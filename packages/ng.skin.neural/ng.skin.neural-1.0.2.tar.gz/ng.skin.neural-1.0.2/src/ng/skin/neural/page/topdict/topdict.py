# -*- coding: utf-8 -*-
"""The searchpage MixIn to view class.

$Id: topdict.py 49615 2008-01-21 13:07:36Z cray $
"""
__author__  = "Andrey Orlov 2006 12 05"
__license__ = "GPL"
__version__ = "$Revision: 49615 $"
__date__ = "$Date: 2008-01-21 16:07:36 +0300 (Пнд, 21 Янв 2008) $"
__credits__ = """Andrey Orlov, for idea and common control"""

import zope.component
from zope.app.zapi import getUtility
from zope.app.catalog.interfaces import ICatalog
from ng.content.annotation.dictannotation.interfaces import IDictAnnotation
from pd.lib.topsort import TopSortFuzzy
from zope.security.proxy import removeSecurityProxy
from zope.app.intid.interfaces import IIntIds

class TopSortFuzzyContainer(TopSortFuzzy) :
    def __call__(self,context) :
        intids = getUtility(IIntIds)         
        search = getUtility(ICatalog, name="catalog",context=context).searchResults
        oids = dict([(intids.getId(ob),ob) for ob in  context.values()])
        
        return (
            oids[oid] for oid in 
                super(TopSortFuzzyContainer,self).__call__([
                    (
                        oid,
                        [uid for uid in
                           search(backkeyword={'any_of':IDictAnnotation(ob).keyword}).uids
                           if uid in oids
                        ]
                    ) for oid,ob in oids.iteritems()
                ])
        )

class TopDict(object) :
    
    def __init__(self,context,request) :
        super(TopDict,self).__init__(context,request)

    def items(self) :
        return TopSortFuzzyContainer()(self.context)
                                                    
    def updateOrder(self,*kv,**kw) :
        self.context.updateOrder([x.__name__ for x in TopSortFuzzyContainer()(self.context)])
        return getattr(self,'index.html')(*kv,**kw)
        
                    
        
