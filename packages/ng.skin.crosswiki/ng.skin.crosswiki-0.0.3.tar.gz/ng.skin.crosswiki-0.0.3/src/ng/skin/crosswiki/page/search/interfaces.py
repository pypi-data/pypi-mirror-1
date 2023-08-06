### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces and schemas for the crosswiki search engine

$Id: interfaces.py 52472 2009-02-08 00:08:16Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52472 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Bool, URI, Datetime, Object

class ISearchMetatypeHandler(Interface) :
    """ Handler of metatype search """

    def search() :
        """ Return search results """
        
    def factoryURL() :
        """ Return URL of factory form """        
                                  
    