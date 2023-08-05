# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: mainbox.py 49689 2008-01-23 14:39:53Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49689 $"
__date__    = "$Date: 2008-01-23 17:39:53 +0300 (Срд, 23 Янв 2008) $"

from zope.app.container.interfaces import IContainer
from zope.app.zapi import getSiteManager

class MainBox(object) :
    """ Folder List """

    foldername = "Main"
    folderinterface = IContainer
    order = 0

    @property
    def values(self) :
        return self.folder.values()

    @property
    def folder(self) :
        return getSiteManager(context=self.context) \
                .getUtility(self.folderinterface, self.foldername)
                
    def __cmp__(self,ob) :
        return cmp(self.order,ob.order)                