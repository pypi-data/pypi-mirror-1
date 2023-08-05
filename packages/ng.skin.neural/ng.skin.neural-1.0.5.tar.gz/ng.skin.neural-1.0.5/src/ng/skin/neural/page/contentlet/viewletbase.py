# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: viewletbase.py 49764 2008-01-28 18:55:09Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49764 $"
__date__    = "$Date: 2008-01-28 21:55:09 +0300 (Пнд, 28 Янв 2008) $"

class ViewletBase(object) :
    """ Body """

    order = 0 
    
    def __init__(self,context,request,*kv,**kw) :
        self.context = context
        self.request = request
        self.order = int(str(self.order))
        super(ViewletBase,self).__init__(context,request,*kv,**kw)

    def __cmp__(self,x) :
        return cmp(self.order,x.order)        
        