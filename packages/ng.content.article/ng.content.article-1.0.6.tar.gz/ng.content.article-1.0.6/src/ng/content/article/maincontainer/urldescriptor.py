### -*- coding: utf-8 -*- #############################################
#######################################################################
"""UrlDescriptor class for the Zope 3 based UrlDescriptor package

$Id: urldescriptor.py 51224 2008-07-01 09:00:22Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51224 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import IUrlDescriptor

class UrlDescriptor(object) :
    """ Descriptor of URL item"""

    implements(IUrlDescriptor)

    URL = ""
    title = u""
    alternative = u""
    