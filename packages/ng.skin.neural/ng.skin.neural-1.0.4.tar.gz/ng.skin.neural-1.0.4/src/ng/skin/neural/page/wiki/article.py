### -*- coding: utf-8 -*- #############################################
"""Article class for the Zope 3 based ng.content.article package

$Id: article.py 49701 2008-01-24 08:48:03Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49701 $"
 
from zope.interface import implements
from ng.content.article.article.article import  Article
from zope.dublincore.interfaces import IZopeDublinCore

def DictionaryItem(context,*kv,**kw) :
    article = Article()
    IZopeDublinCore(article).description = kw["keyword"]
    return article
    
def ArticleByName(context,*kv,**kw) :
    article = Article()
    context.request.form["add_input_name"] = context.request.form["field.name"]
    return article
    
    