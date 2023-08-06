### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Article class for the Zope 3 based ng.content.article package

$Id: article.py 51946 2008-10-23 19:57:39Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51946 $"
 
from zope.interface import implements

from zope.app.container.ordered import OrderedContainer
from ks.smartimage.smartimage import SmartImage
from ng.content.article.interfaces import IDocShort,IDocFormatSwitcher,IArticleDesignSwitcher
from interfaces import IArticleContainerOrdered,IArticleContained,IArticle
import datetime
import pytz 

class ArticleBase(OrderedContainer):
    __doc__ = IArticle.__doc__
    implements(IDocShort,IDocFormatSwitcher,IArticleDesignSwitcher,IArticleContainerOrdered,IArticleContained)

    def __init__(self,*kv,**kw) :
        super(ArticleBase,self).__init__(*kv,**kw)
        #self.logo = SmartImage()
        #self.logo.__parent__ = self
        #self.logo.__name__ = "logo"
        self.created = datetime.datetime.now(pytz.utc)        
        
    title = u""
    abstract = u""
    created = datetime.datetime.now(pytz.utc)        
    author = u""
    iscontent = False
    isdivision = False
    ishidden = False
    #logo = None

class Article(ArticleBase):
    __doc__ = IArticle.__doc__

    implements(IArticle)

    # See ng.content.article.article.interfaces.IArticle
    body = u""

    