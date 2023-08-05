# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: inbody.py 49689 2008-01-23 14:39:53Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49689 $"
__date__    = "$Date: 2008-01-23 17:39:53 +0300 (Срд, 23 Янв 2008) $"

from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from ng.skin.neural.contentlet.viewletbase import ViewletBase

class InBody(ViewletBase) :
    """ Body """
    
    isobject = False
    def __init__(self,*kv,**kw) :
        super(InBody,self).__init__(*kv,**kw)
        items = self.context.values()
        #if len(list(items)) == 1 :
        #    self.ob = list(items)[0]
        #    self.isobject = True            
            