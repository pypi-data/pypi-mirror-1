# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: titlebox.py 49689 2008-01-23 14:39:53Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49689 $"
__date__    = "$Date: 2008-01-23 17:39:53 +0300 (Срд, 23 Янв 2008) $"

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
           
           