### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Article class for the Zope 3 based ng.content.article package

$Id: division.py 51881 2008-10-20 19:05:41Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51881 $"
 
from zope.interface import implements
from interfaces import IDivision,IDivisionContainerOrdered,IDivisionContained
from zope.app.container.ordered import OrderedContainer
import pytz,datetime

class DivisionBase(OrderedContainer):
    __doc__ = IDivision.__doc__
    implements(IDivision,IDivisionContainerOrdered)

    def __init__(self,*kv,**kw) :
        super(DivisionBase,self).__init__(*kv,**kw)
        self.created = datetime.datetime.now(pytz.utc)        

    title = u""
    abstract = u""
    created = datetime.datetime.now(pytz.utc)
    author = u""
    iscontent = False
    isdivision = False
    ishidden = False

     
class Division(DivisionBase):
    __doc__ = IDivision.__doc__


