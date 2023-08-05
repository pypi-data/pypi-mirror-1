# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: titlebox.py 49615 2008-01-21 13:07:36Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49615 $"
__date__    = "$Date: 2008-01-21 16:07:36 +0300 (Пнд, 21 Янв 2008) $"

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
           
           