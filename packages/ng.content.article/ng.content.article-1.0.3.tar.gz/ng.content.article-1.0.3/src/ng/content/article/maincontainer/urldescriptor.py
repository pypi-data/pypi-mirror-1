### -*- coding: utf-8 -*- #############################################
#######################################################################
"""UrlDescriptor class for the Zope 3 based UrlDescriptor package

$Id: urldescriptor.py 49687 2008-01-23 14:35:50Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49687 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import IUrlDescriptor

class UrlDescriptor(object) :
    """ Descriptor of URL item"""

    implements(IUrlDescriptor)

    URL = ""
    title = u""
    alternative = u""
    