# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: currentbox.py 49689 2008-01-23 14:39:53Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49689 $"
__date__    = "$Date: 2008-01-23 17:39:53 +0300 (Срд, 23 Янв 2008) $"

from zope.app.container.interfaces import  IContainer        
from zope.app.zapi import getUtility
from zope.app.zapi import getSiteManager
from zope.proxy import sameProxiedObjects

class CurrentBox(object) :
    """ Folder List """

    @property
    def values(self) :
        return self.folder.values()
        
    @property
    def folder(self) :
        parent = self.context.__parent__
        if sameProxiedObjects(parent,getSiteManager(context=self.context).getUtility(IContainer, "Main")) :
            raise ValueError

        if sameProxiedObjects(parent,getSiteManager(context=self.context).getUtility(IContainer, "news")) :
            raise ValueError
            
        return parent
        
