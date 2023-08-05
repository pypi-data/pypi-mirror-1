# -*- coding: utf-8 -*-
"""The newspage MixIn to view class.

$Id: newsrefpage.py 49615 2008-01-21 13:07:36Z cray $
"""
__author__  = "Dima Khozin"
__license__ = "GPL"
__version__ = "$Revision: 49615 $"
__date__ = "$Date: 2008-01-21 16:07:36 +0300 (Пнд, 21 Янв 2008) $"
__credits__ = """Andrey Orlov, for idea and common control"""

import zope.component
from zope.app import zapi
#from zope.app.catalog.interfaces import ICatalog
from zope.interface import implements
from ng.app.rubricator.interfaces import IRubricateAble
from ng.app.converter.object2psadapter.interfaces import IPropertySheet

class Ob(object) :
    def __getattr__(self,key) :
        try :
            return self.ps[key]
        except KeyError :            
            return getattr(self.news,key)

class NewsRefPage(object):
    
    def __init__(self,context,request) :
        self.request = request
        super(NewsRefPage, self).__init__(context, request)
        #self.context = Ob()
        #self.context.news = IRubricateAble(context)
        #self.context.ps = IPropertySheet(self.context.news)
        self.context = IRubricateAble(context)
            