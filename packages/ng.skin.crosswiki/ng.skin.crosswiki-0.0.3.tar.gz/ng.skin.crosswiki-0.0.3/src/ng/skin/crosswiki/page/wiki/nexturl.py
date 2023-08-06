### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for add form to redirect on @@commonedit.html

$Id: nexturl.py 52472 2009-02-08 00:08:16Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52472 $"

from zope.traversing.browser.absoluteurl import absoluteURL
from ng.content.annotation.redirectannotation.interfaces import IRedirectAnnotation

class NextUrl(object) :
    """ Content """

    def create(self, *args, **kw):
       """Do the actual instantiation."""
       self.ob = self._factory(*args, **kw)
       return self.ob
                   

    def nextURL(self):
        return IRedirectAnnotation(self.ob).redirect
            
            