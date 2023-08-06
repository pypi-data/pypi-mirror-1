### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces and schemas for the article factories used by wiki

$Id: interfaces.py 52472 2009-02-08 00:08:16Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 52472 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Bool, URI, Datetime, Object
from ng.content.article.interfaces import IDocShort
from ng.content.annotation.dictannotation.interfaces import IDictAnnotation
from ng.content.annotation.redirectannotation.interfaces import IRedirectAnnotation

class IDictionaryReference(IDocShort,IDictAnnotation,IRedirectAnnotation) :
    """ Attributes of article class """

                                  
    