### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Maincontainer class for the Zope 3 based maincontainer package

$Id: maincontainer.py 49612 2008-01-21 12:55:05Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49612 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.app.component.site import SiteManagerContainer
from zope.app.container.ordered import OrderedContainer
from interfaces import IMainContainer, IMainContained, IUrlPage, IMainPage

class MainContainer(OrderedContainer, SiteManagerContainer) :
    """ Basic container for future CMS
    """

    implements(IMainContainer, IMainContained, IUrlPage, IMainPage)

    urls = ()

    mainiface = None

    title = u""
    
    abstract = u""
    
    author = u""
    
    created = None
    