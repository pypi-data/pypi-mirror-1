# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: titlebox.py 49764 2008-01-28 18:55:09Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49764 $"
__date__    = "$Date: 2008-01-28 21:55:09 +0300 (Пнд, 28 Янв 2008) $"

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
           
           