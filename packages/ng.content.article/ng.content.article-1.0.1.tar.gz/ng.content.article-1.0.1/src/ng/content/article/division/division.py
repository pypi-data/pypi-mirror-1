### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Article class for the Zope 3 based ng.content.article package

$Id: division.py 49278 2008-01-08 15:44:56Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49278 $"
 
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


