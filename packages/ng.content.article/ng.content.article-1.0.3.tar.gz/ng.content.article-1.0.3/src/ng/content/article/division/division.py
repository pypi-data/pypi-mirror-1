### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Article class for the Zope 3 based ng.content.article package

$Id: division.py 49687 2008-01-23 14:35:50Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49687 $"
 
from zope.interface import implements
from interfaces import IDivision,IDivisionContainerOrdered,IDivisionContained
from zope.app.container.ordered import OrderedContainer

class DivisionBase(OrderedContainer):
    __doc__ = IDivision.__doc__
    implements(IDivision,IDivisionContainerOrdered)

    title = u""
    abstract = u""
    created = None
    author = u""
    iscontent = False
    isdivision = False
    ishidden = False

     
class Division(DivisionBase):
    __doc__ = IDivision.__doc__


