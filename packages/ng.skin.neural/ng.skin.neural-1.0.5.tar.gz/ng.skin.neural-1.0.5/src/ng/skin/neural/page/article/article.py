### -*- coding: utf-8 -*- #############################################
"""ReferenceBase class for the Zope 3 based reference package

$Id: article.py 49764 2008-01-28 18:55:09Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 49764 $"
__date__ = "$Date: 2008-01-28 21:55:09 +0300 (Пнд, 28 Янв 2008) $"
 
from zope.interface import Interface
from ng.content.article.article.interfaces import IArticle
from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from zope.publisher.browser import BrowserView
        
class Proxy(object) :

    def __init__(self,ob) :
        self.ob = ob
        self.ps = IPropertySheet(ob)
                        
    @property
    def abstract(self) :
        return self.ps['abstract']
        
    @property
    def body(self) :
        return self.ps['body']
        
    @property
    def title(self) :
        return self.ps['title']
        
    def __getattr__(self,name) :
        return getattr(self.ob,name)

        
class ArticleView(BrowserView) :
    def __init__(self,*kv,**kw) :
        super(ArticleView,self).__init__(*kv,**kw)
        self.context = Proxy(self.context)
        
