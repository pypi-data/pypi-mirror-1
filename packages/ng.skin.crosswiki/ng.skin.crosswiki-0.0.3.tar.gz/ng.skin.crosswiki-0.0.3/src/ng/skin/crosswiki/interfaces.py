# -*- coding: utf-8 -*-
"""The definitions of new skin interface

$Id: interfaces.py 52485 2009-02-08 09:52:52Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52485 $"

from zope.app.rotterdam import Rotterdam

from ng.skin.base.interfaces import AuthSkin,BaseSkin

class CrossWikiSkin(AuthSkin,BaseSkin,Rotterdam):
    """Skin for the CrossWiki site"""