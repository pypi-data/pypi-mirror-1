### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MainContainer class for the Zope 3 based
ng.content.article.maincontainer package

$Id: maincontainer.py 51224 2008-07-01 09:00:22Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51224 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.app.component.site import SiteManagerContainer
from zope.app.container.ordered import OrderedContainer
from interfaces import IMainContainerOrdered, IMainContained, IUrlPage, IMainPage
import datetime,pytz

class MainContainer(OrderedContainer, SiteManagerContainer) :
    """ Basic container for some storages
    """
    implements(IMainContainerOrdered, IMainContained, IUrlPage, IMainPage)

    def __init__(self,*kv,**kw) :
        super(MainContainer,self).__init__(*kv,**kw)
        self.created = datetime.datetime.now(pytz.utc)        


    urls = ()

    mainiface = None

    title = u""
    
    abstract = u""
    
    author = u""
    
    created = datetime.datetime.now(pytz.utc)
    