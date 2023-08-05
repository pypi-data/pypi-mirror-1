# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: body.py 49689 2008-01-23 14:39:53Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49689 $"
__date__    = "$Date: 2008-01-23 17:39:53 +0300 (Срд, 23 Янв 2008) $"

from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from ng.skin.neural.contentlet.viewletbase import ViewletBase

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
        
            