# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: searchbox.py 49615 2008-01-21 13:07:36Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49615 $"
__date__    = "$Date: 2008-01-21 16:07:36 +0300 (Пнд, 21 Янв 2008) $"

from zope.app.zapi import getSiteManager
#from zope.app.file.interfaces import IFile
from random import choice
from zc.catalog.interfaces import IIndexValues
class SearchBox(object) :
    """ Search Box """


    @property
    def word(self) :
        try :
            return choice(list(getSiteManager(context=self.context) \
                .getUtility(IIndexValues, 'keyword').values()))
        except IndexError :
            return ""                

    def __cmp__(self,ob) :
        return cmp(self.order,ob.order)