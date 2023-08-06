### -*- coding: utf-8 -*- #############################################
#######################################################################
"""UrlDescriptor class for the Zope 3 based UrlDescriptor package

$Id: urldescriptor.py 51946 2008-10-23 19:57:39Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51946 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import IUrlDescriptor

class UrlDescriptor(object) :
    """ Descriptor of URL item"""

    implements(IUrlDescriptor)

    URL = ""
    title = u""
    alternative = u""
    