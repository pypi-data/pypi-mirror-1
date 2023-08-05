# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: titlebox.py 49797 2008-01-29 22:52:29Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49797 $"
__date__    = "$Date: 2008-01-30 01:52:29 +0300 (Срд, 30 Янв 2008) $"

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
           
           