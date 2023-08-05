### -*- coding: utf-8 -*- #############################################
"""ReferenceBase class for the Zope 3 based reference package

$Id: article.py 49689 2008-01-23 14:39:53Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 49689 $"
__date__ = "$Date: 2008-01-23 17:39:53 +0300 (Срд, 23 Янв 2008) $"
 
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
        
