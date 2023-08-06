### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for main page with news.

$Id: main.py 52815 2009-04-03 07:24:12Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52287 $"

from zope.app import zapi
from ng.content.article.article.interfaces import IArticle

class Main(object) :

    @property
    def article(self) :
        try :
            return zapi.getUtility(IArticle,name='mainarticle',context=self.context)
        except LookupError :
            return self.context
                                       
        
