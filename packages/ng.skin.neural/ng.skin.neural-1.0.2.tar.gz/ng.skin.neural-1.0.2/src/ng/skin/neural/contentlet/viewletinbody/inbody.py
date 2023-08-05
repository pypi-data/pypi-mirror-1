# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: inbody.py 49615 2008-01-21 13:07:36Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49615 $"
__date__    = "$Date: 2008-01-21 16:07:36 +0300 (Пнд, 21 Янв 2008) $"

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
            