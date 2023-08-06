### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Article class for the Zope 3 based ng.content.article package

$Id: article.py 51577 2008-08-31 12:16:31Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51577 $"
 
from zope.interface import implements

from zope.app.container.ordered import OrderedContainer
from ks.smartimage.smartimage import SmartImage
from ng.content.article.interfaces import IDocShort,IDocFormatSwitcher
from interfaces import IArticleContainerOrdered,IArticleContained,IArticle
import datetime
import pytz 

class ArticleBase(OrderedContainer):
    __doc__ = IArticle.__doc__
    implements(IDocShort,IDocFormatSwitcher,IArticleContainerOrdered,IArticleContained)

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

    