# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: currentbox.py 49615 2008-01-21 13:07:36Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49615 $"
__date__    = "$Date: 2008-01-21 16:07:36 +0300 (Пнд, 21 Янв 2008) $"

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
        
