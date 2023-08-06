### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter dictionary item to article.

$Id: dictionaryreferenceadapter.py 52472 2009-02-08 00:08:16Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52472 $"
 
from zope.interface import implements
from ng.content.article.interfaces import IDocShort
from ng.content.annotation.dictannotation.interfaces import IDictAnnotation
from ng.content.annotation.redirectannotation.interfaces import IRedirectAnnotation
from ng.skin.base.page.wiki.joininterfaceadapterfactory import joininterfaceadapterfactory

DictionaryReferenceAdapter = joininterfaceadapterfactory(IDocShort, IDictAnnotation, IRedirectAnnotation)

                         