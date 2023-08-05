### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Next-Previous view adapter class

$Id: nextprev.py 49701 2008-01-24 08:48:03Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 49701 $"

from zope.publisher.browser import BrowserView    
from zope.interface import implements
from interfaces import INextPrev
from ng.adapter.pager.interfaces import  IPagerSource

class NextPrev(BrowserView) :
    __doc__ = __doc__
    implements(INextPrev)
    prev = None
    next = None
    
    def __init__(self,*kv,**kw) :
        super(NextPrev,self).__init__(*kv,**kw)
        up = IPagerSource(self.up)

        keys = up.keys()
        index = keys.index(self.context.__name__)
        if index :
            self.prev = self.up[keys[index-1]]
        if index < len(keys)-1 :
            self.next = self.up[keys[index+1]]

    @property
    def up(self) :
        return self.context.__parent__
        
