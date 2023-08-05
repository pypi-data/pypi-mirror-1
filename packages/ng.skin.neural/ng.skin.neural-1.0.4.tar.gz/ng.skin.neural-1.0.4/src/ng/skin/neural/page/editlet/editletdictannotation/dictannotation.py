# -*- coding: utf-8 -*-
"""Sample of one editletitem

$Id: dictannotation.py 49701 2008-01-24 08:48:03Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 49701 $"
__date__    = "$Date: 2008-01-24 11:48:03 +0300 (Чтв, 24 Янв 2008) $"

from ng.zcmlmultiform.viewletbase import ViewletBase
from ng.content.annotation.dictannotation.interfaces import IDictAnnotation
from zope.app.form.browser.editview import EditView
from zope.schema import getFieldsInOrder, getFieldNames
from zope.viewlet.viewlet import simple

class DictAnnotation(EditView,ViewletBase) :
    """ DictAnnotation """
    schema = IDictAnnotation
    fieldNames = getFieldNames(IDictAnnotation)
    prefix = "dict"

    def __init__(self,context,request,*kv,**kw) :
        super(simple,self).__init__(context,request,*kv,**kw)
        self._setUpWidgets()
        self.setPrefix(self.prefix)
        
    def update(self) :
        pass

    def update_form(self) :
        return EditView.update(self)
