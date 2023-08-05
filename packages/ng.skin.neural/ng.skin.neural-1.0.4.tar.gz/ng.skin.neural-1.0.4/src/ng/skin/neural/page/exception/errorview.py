### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ErrorView - is base class for zope3 errors

$Id: errorview.py 49701 2008-01-24 08:48:03Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49701 $"

from zope.publisher.browser import BrowserView
from zope.app.exception.systemerror import SystemErrorView
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app import zapi
from zope.app.container.interfaces import IContainer

class ErrorView(BrowserView,SystemErrorView):
    """Class for errorpage view"""

    @property
    def mainurl(self) :
        return absoluteURL(zapi.getUtility(
            IContainer,
            name="Main"),self.request)
            
class UnauthorizedView(ErrorView):
    """Class for errorpage view"""

    def __init__(self,context,request) :
        super(UnauthorizedView,self).__init__(context,request)
        request.response.setStatus(401)
        request.response.addHeader("WWW-Authenticate",'basic realm="Zope"')
            
            