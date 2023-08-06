### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter owner to nickname in browse represetative

$Id: articlelink.py 51577 2008-08-31 12:16:31Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51475 $"

from zope.app.zapi import getUtility
from ng.content.article.article.interfaces import IArticle

class ArticleLink(object) :
    """ Return article registered by name """

    def __init__(self,context,request) :
        self.context = context
        self.request = request
        
    def __getitem__(self,name) :
      return getUtility(IArticle,context=self.context,name=name)

