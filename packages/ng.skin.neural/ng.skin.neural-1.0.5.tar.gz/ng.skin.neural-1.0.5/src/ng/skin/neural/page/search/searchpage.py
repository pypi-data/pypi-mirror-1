# -*- coding: utf-8 -*-
"""The searchpage MixIn to view class.

$Id: searchpage.py 49764 2008-01-28 18:55:09Z cray $
"""
__author__  = "Andrey Orlov 2006 12 05"
__license__ = "GPL"
__version__ = "$Revision: 49764 $"
__date__ = "$Date: 2008-01-28 21:55:09 +0300 (Пнд, 28 Янв 2008) $"
__credits__ = """Andrey Orlov, for idea and common control"""

import zope.component
from zope.app import zapi
from zope.app.catalog.interfaces import ICatalog
from zope.traversing.browser.absoluteurl import absoluteURL
from urllib import quote
from zope.publisher.browser import Record
from ng.adapter.path.interfaces import IPath
from ng.adapter.pager.resultset2pagersourceadapter import ResultSet2PagerSourceAdapter
from ng.adapter.pager.interfaces import IPager
from zope.app.securitypolicy.interfaces import IPrincipalPermissionMap
import zope.app.securitypolicy.zopepolicy
import re

class Participation(object) :
    interaction = None
    def __init__(self,principal) :
        self.principal = principal

def check(context,request) :
    interaction = zope.app.securitypolicy.zopepolicy.ZopeSecurityPolicy()
    participation = Participation(request.principal)
    interaction.add(participation)
    return interaction.checkPermission("zope.ManageContent",context)

class Search(object) :

    @property
    def nextkeyword(self) :
        if "keyword" in self.request.form :
            return str(self.request.form['keyword']['any_of'][0])
        elif "name" in self.request.form :
            return str(self.request.form['name']['any_of'][0])
        return self.request.form.get('common','')

    @property
    def quotenextkeyword(self) :
        return quote(self.nextkeyword)
    
    @property
    def pager(self) :
        d = {}
        for key,value in self.request.form.items() :
            if isinstance(value,Record) :
                value = dict(value) 

            d[str(key)] = value

        try :
            del d['current']
        except KeyError :
            pass

        if 'keyword' in d :
            d['keyword']['any_of'] = (re.sub("\s+"," ",d['keyword']['any_of'][0]).strip().lower(),)
        elif 'name' in d :
            d['name']['any_of'] = (re.sub("\s+"," ",d['name']['any_of'][0]),)            
        else :
            path=IPath(self.context).path
            d['urlpath'] = {'between' : (path,path+u'\xff',True,True) }            
        
        res = zapi.getUtility(ICatalog,name="catalog",context=self.context).searchResults(**d)        
        pagersource = ResultSet2PagerSourceAdapter(res)

        if len(res) == 0 :
            if "keyword" in self.request.form :
                url = \
                  absoluteURL(zapi.getUtility(
                      zope.app.container.interfaces.IContainer,
                      name="Main",context=self.context)['dictionary'],self.request)
                if check(self.context,self.request) :
                    self.request.response.redirect(url+"/+/AddDictionaryItem.html=?field.keyword="+self.quotenextkeyword)
            elif "name" in self.request.form :
                url = absoluteURL(self.context,self.request)

                if check(self.context,self.request) :
                    self.request.response.redirect(url+"/+/AddArticleByName.html=?field.name="+self.quotenextkeyword)

        if len(res) == 1 :
            self.request.response.redirect(absoluteURL(
                pagersource[pagersource.keys()[0]],
                self.request)) 
            
        return pagersource
                                       
        
