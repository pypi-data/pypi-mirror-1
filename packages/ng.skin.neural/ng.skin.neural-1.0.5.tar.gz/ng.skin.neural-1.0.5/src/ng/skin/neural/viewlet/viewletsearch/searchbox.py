# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: searchbox.py 49764 2008-01-28 18:55:09Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49764 $"
__date__    = "$Date: 2008-01-28 21:55:09 +0300 (Пнд, 28 Янв 2008) $"

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