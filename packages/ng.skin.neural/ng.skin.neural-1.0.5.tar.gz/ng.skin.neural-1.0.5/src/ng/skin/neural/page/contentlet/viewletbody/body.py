# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: body.py 49764 2008-01-28 18:55:09Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49764 $"
__date__    = "$Date: 2008-01-28 21:55:09 +0300 (Пнд, 28 Янв 2008) $"

from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from ng.skin.neural.page.contentlet.viewletbase import ViewletBase

class Proxy(object) :
    def __init__(self,ob) :
        self.ob = ob
        self.ps = IPropertySheet(ob)
                        
    @property
    def body(self) :
        return self.ps['body']
        
    def __getattr__(self,name) :
        return getattr(self.ob,name)

class Body(ViewletBase) :
    """ Body """

    def __init__(self,*kv,**kw) :
        super(Body,self).__init__(*kv,**kw)
        self.context = Proxy(self.context)
        
            