### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.content.article.division package

$Id: interfaces.py 51224 2008-07-01 09:00:22Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51224 $"
 
from zope.interface import Interface
from zope.schema import Text, TextLine, Field, Bool, Datetime
from zope.app.container.interfaces import IContained, IOrderedContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from ng.content.article.interfaces import ICommonContainer,IDocShort

class IDivisionContent(Interface) :
    """ Interface for division content """

class IDivisionContained(IContained,IDivisionContent) :
    """ Division Contained """

#IDivisionContained.__parent__ = ContainerTypesConstraint(ICommonContainer)

class IDivisionContainer(IOrderedContainer,ICommonContainer) :
    """ Division Container """
    
    def __setitem__(name, object) : 
        """ Add IDivision Content """

    __setitem__.precondition = ItemTypePrecondition(IDivisionContent)                    

class IDivisionContainerOrdered(IDivisionContainer) :
    """ Division Container """

class IDivision(IDocShort,IDivisionContained) :
    """ Division content-class """

    
