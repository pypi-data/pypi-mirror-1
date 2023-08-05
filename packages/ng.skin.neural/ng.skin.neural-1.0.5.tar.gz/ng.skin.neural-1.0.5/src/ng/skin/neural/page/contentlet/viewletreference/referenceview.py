# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: referenceview.py 49764 2008-01-28 18:55:09Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49764 $"
__date__    = "$Date: 2008-01-28 21:55:09 +0300 (Пнд, 28 Янв 2008) $"

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
        
        