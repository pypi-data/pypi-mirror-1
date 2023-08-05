### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Divisions Adapter to attribute directory component.

$Id: division2attributediradapter.py 49278 2008-01-08 15:44:56Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49278 $"


from ng.ftp.attributedirectory import AttributeDirBase
from zope.interface import Interface,implements
from ng.ftp.interfaces import IAttributeDir
from ng.content.article.interfaces import IDocShort

class Division2AttributeDirAdapter(AttributeDirBase) :
    __doc__ = __doc__
    implements(IAttributeDir)
    ifaces = [IDocShort]
    
    
