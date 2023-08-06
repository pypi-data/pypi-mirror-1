### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter of article to attribute dir component.

$Id: article2attributediradapter.py 51577 2008-08-31 12:16:31Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51577 $"


from ng.ftp.attributedirectory import AttributeDirBase
from zope.interface import Interface,implements
from ng.ftp.interfaces import IAttributeDir
from ng.content.article.interfaces import IDocShortLogo,IDocBody

class Article2AttributeDirAdapter(AttributeDirBase) :
    implements(IAttributeDir)
    ifaces = [IDocShortLogo,IDocBody]

