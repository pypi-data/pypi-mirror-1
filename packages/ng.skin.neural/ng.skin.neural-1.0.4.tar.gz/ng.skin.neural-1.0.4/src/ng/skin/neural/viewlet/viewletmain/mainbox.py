# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: mainbox.py 49701 2008-01-24 08:48:03Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49701 $"
__date__    = "$Date: 2008-01-24 11:48:03 +0300 (Чтв, 24 Янв 2008) $"

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