### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter of article to attribute dir component.

$Id: article2attributediradapter.py 51881 2008-10-20 19:05:41Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51881 $"


from ng.ftp.attributedirectory import AttributeDirBase
from zope.interface import Interface,implements
from ng.ftp.interfaces import IAttributeDir
from ng.content.article.interfaces import IDocShortLogo,IDocBody

class Article2AttributeDirAdapter(AttributeDirBase) :
    implements(IAttributeDir)
    ifaces = [IDocShortLogo,IDocBody]

