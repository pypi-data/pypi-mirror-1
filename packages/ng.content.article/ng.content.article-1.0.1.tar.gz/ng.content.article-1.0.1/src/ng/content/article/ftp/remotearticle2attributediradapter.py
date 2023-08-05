### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Adapter of division to attribute dir component.

$Id: remotearticle2attributediradapter.py 49278 2008-01-08 15:44:56Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49278 $"


from ng.ftp.attributedirectory import AttributeDirBase
from zope.interface import Interface,implements
from ng.ftp.interfaces import IAttributeDir
from ng.content.article.remotearticle.interfaces import IRemoteArticle

class RemoteArticle2AttributeDirAdapter(AttributeDirBase) :
    __doc__ = __doc__
    implements(IAttributeDir)
    ifaces = [IRemoteArticle]
    
    
