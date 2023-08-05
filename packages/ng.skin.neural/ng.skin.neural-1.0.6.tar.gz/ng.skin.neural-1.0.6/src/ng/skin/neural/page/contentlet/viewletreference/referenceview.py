# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: referenceview.py 49797 2008-01-29 22:52:29Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49797 $"
__date__    = "$Date: 2008-01-30 01:52:29 +0300 (Срд, 30 Янв 2008) $"

from ks.reference.referenceannotation.interfaces import IReferenceTuple
from ng.skin.neural.page.contentlet.viewletbase import ViewletBase

class Reference(ViewletBase) :
    """ Reference """
    def __init__(self,*kv,**kw) :
        super(Reference,self).__init__(*kv,**kw)

    @property
    def islink(self) :
        return bool(self.forward) or bool(self.backward)

    @property
    def forward(self) :
        return IReferenceTuple(self.context).items(self.context)

    @property
    def backward(self) :
        return IReferenceTuple(self.context).items(self.context,backward=True)
        
        