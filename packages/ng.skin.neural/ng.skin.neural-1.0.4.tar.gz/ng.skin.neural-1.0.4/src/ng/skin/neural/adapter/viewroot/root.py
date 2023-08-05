### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Next-Previous view adapter class

$Id: root.py 49701 2008-01-24 08:48:03Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 49701 $"

from zope.publisher.browser import BrowserView    
from interfaces import IRoot
from zope.app.container.interfaces import IContainer
from zope.app.zapi import getSiteManager

def getRoot(context,request) :
    return getSiteManager(context=context) \
            .getUtility(IContainer, 'Main')


class Root(BrowserView) :

    @property
    def root(self) :
        return getSiteManager(context=self.context) \
            .getUtility(IContainer, 'Main')