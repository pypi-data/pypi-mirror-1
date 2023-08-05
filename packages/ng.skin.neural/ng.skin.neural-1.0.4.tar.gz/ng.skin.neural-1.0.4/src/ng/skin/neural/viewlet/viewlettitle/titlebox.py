# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: titlebox.py 49701 2008-01-24 08:48:03Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49701 $"
__date__    = "$Date: 2008-01-24 11:48:03 +0300 (Чтв, 24 Янв 2008) $"

from zope.app.zapi import getSiteManager
from zope.app.container.interfaces import IContainer
from ng.adapter.title.interfaces import ITitle 
class TitleBox(object) :
    """ Title Box """

    @property
    def title(self) :
        return ITitle(getSiteManager(context=self.context) \
                .getUtility(IContainer, 'Main')).title

    def __cmp__(self,ob) :
        return cmp(self.order,ob.order)
           
           