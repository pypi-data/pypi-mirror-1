### -*- coding: utf-8 -*- #############################################
"""ReferenceBase class for the Zope 3 based reference package

$Id: division.py 49615 2008-01-21 13:07:36Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 49615 $"
__date__ = "$Date: 2008-01-21 16:07:36 +0300 (Пнд, 21 Янв 2008) $"
 
from zope.interface import Interface
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
    def title(self) :
        return self.ps['title']
        
    def __getattr__(self,name) :
        return getattr(self.ob,name)
        
class DivisionView(BrowserView) :
    def __init__(self,*kv,**kw) :
        super(DivisionView,self).__init__(*kv,**kw)
        self.context = Proxy(self.context)
        
