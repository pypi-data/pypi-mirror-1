### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.content.article package

$Id: interfaces.py 51946 2008-10-23 19:57:39Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51946 $"
 
from zope.interface import Interface,invariant,Invalid
from zope.schema import Text, TextLine, Field, Bool, URI, Datetime, Object
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from ks.page.idocumentlogo.interfaces import IDocumentLogo
from zope.app.container.interfaces import IReadContainer
from ng.schema.regexp.regexpfield import Regexp
from ng.schema.interfaceswitcher.interfacechoicefield import InterfaceChoice

import datetime
import pytz
from ng.schema.interfaceswitcher.interfacechoicefield import InterfaceChoice
from ng.lib.dynamicdefault import DynamicDefault

class IDocFormatSwitcher(Interface) :
    """ Format of contents document """

class IArticleDesignSwitcher(Interface) :
    iarticledesignswitcher = InterfaceChoice(title=u"Article Design",required=False)
                                    
IArticleDesignSwitcher['iarticledesignswitcher'].iface = IArticleDesignSwitcher

class IDocTitle(Interface) :
    """ Attributes of article class """
    title = Regexp(title = u'Title',
        description = u'Title',
        default = u'',
        required = True,
        regexp = (
#             (True, u"^\s*\w+\s*-\s*?[0-9]+\s*$", u"Название состоит из цифр с буквами"),
              (False, u"^.*/.*$", u"Название не содержит символ /"),
            ),
        rewrite = (
            (u"^\s*(?P<name>\w+)\s*-\s*?(?P<number>[0-9]+)\s*$", u"%(name)s-%(number)s"),
            (u"^\s*(?P<name>[^\s]+)\s*$", u"%(name)s"),
            )
        )

def leni(ob) :
    if len(ob.abstract) > 10 :
        raise Invalid

        
class IDocAbstract(Interface) :
    """ Attributes of article class """
    abstract = Text(title = u'Abstract',
        description = u'Short article desctription',
        default = u'',
        required = False)
                                  
    invariant(leni)                                  
                                  
    created = DynamicDefault(Datetime,title = u'Date/Time',
        description = u'Date/Time',
        default = lambda : datetime.datetime.now(pytz.utc),
        required = True)
   
    author = TextLine(title = u'Author',
        description = u'Article Author',
        default = u'',
        required = False)

class IDocProduct(Interface) :
    svn = URI(title = u'Repository',
        description = u'Repositiory (subversion or other)',
        required = False)
        
    url = URI(title = u'Download Url',
        description = u'URL to download release',
        required = False)        

class ISContent(Interface) :
    """ ISContent """
    iscontent = Bool(title = u"Make content", default=False, required=True);
    idocformatswitcher = InterfaceChoice(interface=IDocFormatSwitcher,  title=u"Document Format")

class IDocBody(ISContent) :
    """ Body of document class """
    
    body = Text(title = u'Doc',
        description = u'Document Text',
        default = u'',
        required = False)

class IDocKind(Interface) :

    isdivision = Bool(title = u"Use as division", default=False, required=True);

    ishidden = Bool(title = u"Hidden", default=False, required=True);

class IDocShort(IDocTitle,IDocAbstract, IDocKind) :
    """ Short list of attributes of article class """

class IDocShortLogo(IDocShort,IDocumentLogo) :
    """ Short list of attributes of article class """

class IContentShowable(Interface) :
    """ Division showable content"""

class IAbstractShowable(IContentShowable) :
    """ Division showable content"""

class IIconShowable(IContentShowable) :
    """ Division showable content"""

class ICommonContainer(Interface) :
    """ Our object can be included only into ICommonContainer """                

# Отображаемые (вообще) страницы (-хидден, -неотображаемые)
class IShowContainer(IReadContainer) :
    """ Container showed items """
    
# Страницы статьи (show -isdivide)
class IPageContainer(IReadContainer) :
    """ Container page items """
    
# Содержимое статьи show & isdivide
class IContentContainer(IReadContainer) :
    """ Container content items """

# Содержимое статьи show & isdivide
class IIconContainer(IContentContainer) :
    """ Container icons items """

# Содержимое статьи show & isdivide
class IAbstractContainer(IContentContainer) :
    """ Container icons items """

class IArticleDesignSwitcher(Interface) :
    """ Design article page """
    
class IArticleDesignSwitcher(Interface) :
    iarticledesignswitcher = InterfaceChoice(title=u"Article Design")
                                    
IArticleDesignSwitcher['iarticledesignswitcher'].iface = IArticleDesignSwitcher
                                            