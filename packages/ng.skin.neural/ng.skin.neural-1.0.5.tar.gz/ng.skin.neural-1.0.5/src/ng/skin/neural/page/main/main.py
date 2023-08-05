### -*- coding: utf-8 -*- #############################################
"""MainView class for the Zope 3 based ng.skin.neural package

$Id: main.py 49764 2008-01-28 18:55:09Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 49764 $"
__date__ = "$Date: 2008-01-28 21:55:09 +0300 (Пнд, 28 Янв 2008) $"
 
from zope.interface import Interface
from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from ks.reference.referenceannotation.interfaces import IReferenceTuple
from zope.app.container.interfaces import  IContainer        
from zope.app.catalog.interfaces import ICatalog
from zope.app.zapi import getUtility
from zope.app.intid.interfaces import IIntIds
from pd.lib.heapsort import HeapSortByIndexSafe, HeapSortByIndex

class MainView(object) :
    def __init__(self,context,*kv,**kw) :
        super(MainView,self).__init__(context,*kv,**kw)
        self.context=context
                
    @property
    def newslist(self) :

        ls = getUtility(IContainer,"news",context=self.context).values()[-10:]
        ls.reverse()
        return ls

    @property        
    def articlelist(self) :
        ls = getUtility(IContainer,"article",context=self.context).values() 
        ls.reverse()
        return ls
    
    @property
    def newremotearticlelist(self) :
        intids = getUtility(IIntIds,context=self.context)
        cat = getUtility(ICatalog,"catalog",context=self.context)
        return ( intids.getObject(x) for x 
                   in HeapSortByIndexSafe(
                        cat.apply({'klass': ("ng.content.remotearticle.remotearticle.remotearticle.RemoteArticle",)*2}),
                        cat['mtime']._rev_index,
                        True
                        ).chunk(10)
                )                   

    @property
    def newarticlelist(self) :
        intids = getUtility(IIntIds,context=self.context)
        cat = getUtility(ICatalog,"catalog",context=self.context) 
        return ( intids.getObject(x) for x 
                   in HeapSortByIndexSafe(
                        cat.apply({'klass': ("ng.content.article.article.article.Article",)*2}),
                        cat['mtime']._rev_index,
                        True
                        ).chunk(10)
                )                   
    
    