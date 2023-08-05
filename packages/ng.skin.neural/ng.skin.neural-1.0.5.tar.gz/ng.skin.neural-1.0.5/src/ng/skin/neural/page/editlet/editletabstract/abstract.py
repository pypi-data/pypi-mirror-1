# -*- coding: utf-8 -*-
"""Sample of one editletitem

$Id: abstract.py 49764 2008-01-28 18:55:09Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 49764 $"
__date__    = "$Date: 2008-01-28 21:55:09 +0300 (Пнд, 28 Янв 2008) $"

from ng.zcmlmultiform.viewletbase import ViewletBase
from ng.content.article.interfaces import IDocShortLogo
from zope.app.form.browser.editview import EditView
from zope.schema import getFieldsInOrder, getFieldNames
from zope.viewlet.viewlet import simple

class Abstract(EditView,ViewletBase) :
    """ Abstract """
    schema = IDocShortLogo
    fieldNames = getFieldNames(IDocShortLogo)
    prefix = "abstract"

    def __init__(self,context,request,*kv,**kw) :
        super(simple,self).__init__(context,request,*kv,**kw)
        self._setUpWidgets()
        self.setPrefix(self.prefix)

    def update(self) :
        pass
    
    def update_form(self) :
        return EditView.update(self)
        
        