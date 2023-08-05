# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: abstract.py 49701 2008-01-24 08:48:03Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49701 $"
__date__    = "$Date: 2008-01-24 11:48:03 +0300 (Чтв, 24 Янв 2008) $"

from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from ng.skin.neural.page.contentlet.viewletbase import ViewletBase

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



class Abstract(ViewletBase) :
    """ Abstract """

    def __init__(self,*kv,**kw) :
        super(Abstract,self).__init__(*kv,**kw)
        self.context = Proxy(self.context)
        
        