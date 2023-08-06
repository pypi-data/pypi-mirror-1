### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Factories for article class used in wiki

$Id: dictionaryitem.py 52472 2009-02-08 00:08:16Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 52472 $"
 
from zope.interface import implements,providedBy
from ng.content.article.article.article import  Article
from ng.content.annotation.annotationswitcher.demo.interfaces import IAnnotationSwitcherDict, IAnnotationSwitcherRedirect

from zope.security.proxy import removeSecurityProxy
from zope.interface import alsoProvides

def DictionaryItem(context,*kv,**kw) :
    article = Article(*kv,**kw)
    alsoProvides(article, IAnnotationSwitcherDict)
    alsoProvides(article, IAnnotationSwitcherRedirect)
    print article
    print list(providedBy(article))
    return article
    
    
    