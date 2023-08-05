### -*- coding: utf-8 -*- #############################################
#######################################################################
""" Special widgets for maincontainer browser pages

$Id: widgets.py 49278 2008-01-08 15:44:56Z cray $
"""
__author__  = u"Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49278 $"

from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import ObjectWidget
from zope.app.form.browser import TupleSequenceWidget
from ng.content.article.maincontainer.urldescriptor import UrlDescriptor

UrlDescriptorTupleWidget = CustomWidgetFactory(
   TupleSequenceWidget,
   subwidget=CustomWidgetFactory(
                    ObjectWidget,
                    UrlDescriptor))
