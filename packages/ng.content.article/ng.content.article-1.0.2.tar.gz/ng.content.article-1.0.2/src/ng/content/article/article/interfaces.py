### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.content,article.article package

$Id: interfaces.py 49612 2008-01-21 12:55:05Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49612 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Bool, Datetime
from zope.app.container.interfaces import IContained, IOrderedContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from ks.page.idocumentlogo.interfaces import IDocumentLogo
from ng.content.article.interfaces import ICommonContainer,IDocShortLogo,IDocBody

class IArticleContent(Interface) :
    """ Interface for article content """

class IArticleContained(IContained,IArticleContent) :
    """ Article Contained """
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ICommonContainer))


class IArticleContainer(IOrderedContainer,ICommonContainer) :
    """ Article Container """
    
    def __setitem__(name, object) : 
        """ Add IArticle Content """

    __setitem__.precondition = ItemTypePrecondition(IArticleContent)                    

class IArticleContainerOrdered(IArticleContainer) :
    """ Article Container """

class IArticle(IDocShortLogo,IDocBody,IArticleContained) :
    """ Article content-class """
    pass

    