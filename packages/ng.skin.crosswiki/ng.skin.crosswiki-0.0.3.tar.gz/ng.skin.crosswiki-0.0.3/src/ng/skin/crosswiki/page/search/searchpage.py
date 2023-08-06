### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for searchpage.

$Id: searchpage.py 52472 2009-02-08 00:08:16Z cray $



"""
__author__  = "Andrey Orlov 2009"
__license__ = "GPL"
__version__ = "$Revision: 52472 $"

import zope.component
from zope.app import zapi
from zope.app.catalog.interfaces import ICatalog
from urllib import quote
from zope.publisher.browser import Record
from ng.adapter.path.interfaces import IPath
from ng.adapter.pager.resultset2pagersourceadapter import ResultSet2PagerSourceAdapter
from ng.adapter.pager.interfaces import IPager
from ng.adapter.adaptiveurl.adaptiveurl import adaptiveURL
from zope.app.securitypolicy.interfaces import IPrincipalPermissionMap
from ng.content.annotation.redirectannotation.interfaces import IRedirectAnnotation
import zope.app.securitypolicy.zopepolicy
import re

from ng.site.addon.profile.profileadapter.profileadapter import profileadaptersimple
from interfaces import ISearchMetatypeHandler

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
    def pager(self) :
        handler = zapi.getMultiAdapter((self.context,self.request), ISearchMetatypeHandler,  name=self.request.form['predicate'])
        res = handler.search()

        if len(res) == 0 and check(profileadaptersimple(self.context),self.request) :
            self.request.response.redirect(handler.factoryURL())

        if len(res) == 1 :
            ps = ResultSet2PagerSourceAdapter(res)

            ob = ps[ps.keys()[0]]
            try :
                url = IRedirectAnnotation(ob).redirect            
            except LookupError :
                url = self.request.response.redirect(adaptiveURL(ob))                

            self.request.response.redirect(url)

        return ResultSet2PagerSourceAdapter(res)

class SearchBase(object) :
    def __init__(self,context,request) :
        self.context = context
        self.request = request

    def search(self) :
        return zapi.getUtility(ICatalog,context=self.context).searchResults(**self.query())
        
    def factoryURL(self) :
        return adaptiveURL(profileadaptersimple(self.context),self.request) + self.factory()        
    
class SearchByKeyword(SearchBase) :
    def query(self) :
        return { 'keyword' : { 'any_of' : (re.sub("\s+"," ",self.request.form['query']).strip().lower(),) } } 
        
    def factory(self) :
        return ("/+/AddDictionaryItem.html=?"
                "field.keyword.0.=%(keyword)s&"
                "field.keyword.count=1&"
                "field.title=%(keyword)s" % { 'keyword': quote(str(self.request.form["query"])) } )
    
class SearchByName(SearchBase) :
    def query(self,request) :
        return { 'name' : { 'any_of' : (re.sub("\s+"," ",self.request.form['query']).strip().lower(),) }  }
    
    def factory(self) :
        return ("/+/AddArticle.html=?"
                "field.title="+quote(self.request.form["query"]) )
