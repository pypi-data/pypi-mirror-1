### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Next-Previous view adapter class

$Id: nextprev.py 49797 2008-01-29 22:52:29Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 49797 $"

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
        
