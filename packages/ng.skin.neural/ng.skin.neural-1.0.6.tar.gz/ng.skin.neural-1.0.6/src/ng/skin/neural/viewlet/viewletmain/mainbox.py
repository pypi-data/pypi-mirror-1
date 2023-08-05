# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: mainbox.py 49797 2008-01-29 22:52:29Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49797 $"
__date__    = "$Date: 2008-01-30 01:52:29 +0300 (Срд, 30 Янв 2008) $"

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