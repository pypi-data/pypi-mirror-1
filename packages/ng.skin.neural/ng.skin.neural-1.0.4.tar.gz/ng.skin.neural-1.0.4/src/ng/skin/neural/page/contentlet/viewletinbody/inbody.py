# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: inbody.py 49701 2008-01-24 08:48:03Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49701 $"
__date__    = "$Date: 2008-01-24 11:48:03 +0300 (Чтв, 24 Янв 2008) $"

from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from ng.skin.neural.page.contentlet.viewletbase import ViewletBase

class InBody(ViewletBase) :
    """ Body """
    
    isobject = False
    def __init__(self,*kv,**kw) :
        super(InBody,self).__init__(*kv,**kw)
        items = self.context.values()
        #if len(list(items)) == 1 :
        #    self.ob = list(items)[0]
        #    self.isobject = True            
            