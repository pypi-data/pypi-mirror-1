### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.content.article.maincontainer package

$Id: interfaces.py 51224 2008-07-01 09:00:22Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51224 $"

from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, URI, Tuple, Object
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint

#from ng.content.article.interfaces import IDocShort
from ng.schema.interfaceswitcher.interfacechoicefield import InterfaceChoice
from zope.app.component.interfaces import IPossibleSite
from zope.app.container.interfaces import IOrderedContainer
from ng.content.article.interfaces import IDocTitle, IDocAbstract

from zope.app.file.interfaces import IImage


class IMainSwitcher(Interface) :
    """ Interface of Maincontainer
    """


class IMainContent(Interface) :
    """ Interface for Maincontainer content
    """


class IMainContained(IContained) :
    """ Maincontainer contained
    """

    #IMainContainerContained.__parent__ = ContainerTypesConstraint()

    
class IMainContainer(IPossibleSite, IOrderedContainer) :
    """ Maincontainer container
    """

    def __setitem__(name, object) :
        """ Add IMainContainer content
        """
    
    __setitem__.precondition = ItemTypePrecondition(IMainContent)


class IMainContainerOrdered(IMainContainer) :
    """ Division Container """


class IUrlDescriptor(Interface) :
    """ Describe URL its title and alternative text
    """

    URL = URI(
        title = u'URL',
        description = u'URL',
        required = True)
    
    title = TextLine(
        title = u'Title',
        description = u'Title',
        default = u'',
        required = True)
    
    alternative = Text(
        title = u'Alternative text',
        description = u'Alternative text',
        default = u'',
        required = False)


class IUrlPage(Interface) :
    """ Allow to use tuple of object with IUrlDescriptor interface
    """

    urls = Tuple(
        title=u'External links',
        description=u'External links',
        value_type=Object(
            title=u'URL descriptor',
            description=u'URL descriptor',
            schema=IUrlDescriptor))


class IMainPage(IDocTitle,IDocAbstract) :
    """ Settings of MainPage
    """

    mainiface = InterfaceChoice(
        interface = IMainSwitcher,
        title = u'Design Choice',
        description=u'Design Choice',
        required = False)

    logo = Object(
        title = u"Logo",
        description = u"Logo",
        schema = IImage,
        )
