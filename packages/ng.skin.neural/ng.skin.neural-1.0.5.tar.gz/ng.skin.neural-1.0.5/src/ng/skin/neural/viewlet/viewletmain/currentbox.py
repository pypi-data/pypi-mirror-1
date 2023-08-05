# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: currentbox.py 49764 2008-01-28 18:55:09Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49764 $"
__date__    = "$Date: 2008-01-28 21:55:09 +0300 (Пнд, 28 Янв 2008) $"

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
        
