### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Container adapters the Zope 3 based ng.content.article package

$Id: directoryfactory.py 51577 2008-08-31 12:16:31Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51577 $"
 
from zope.interface import Interface,implements
from zope.filerepresentation.interfaces import IDirectoryFactory
from os.path import splitext
from ng.content.article.article.article import Article
from ng.content.article.division.division import Division

from ng.ftp.utils import packkey, unpackkey, unpacktype

import datetime

class DirectoryFactory(object) :
    implements(IDirectoryFactory)
    def __init__(self,context) :
        self.context = context
        
    def __call__(self,name) :
        ext = unpacktype(name)
        if ext == "Article" :
            return Article()
        elif ext  == "Division" :
            return Division()
