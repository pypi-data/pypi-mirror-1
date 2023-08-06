### -*- coding: utf-8 -*- #############################################
#######################################################################
""" Special widgets for maincontainer browser pages

$Id: widgets.py 51224 2008-07-01 09:00:22Z cray $
"""
__author__  = u"Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51224 $"

from zope.app.form import CustomWidgetFactory
from ng.lib.objectwidget import ObjectWidget
from zope.app.form.browser import TupleSequenceWidget
from ng.content.article.maincontainer.urldescriptor import UrlDescriptor
from zope.app.file.image import Image

UrlDescriptorTupleWidget = CustomWidgetFactory(
   TupleSequenceWidget,
   subwidget=CustomWidgetFactory(
                    ObjectWidget,
                    UrlDescriptor))

LogoWidget = CustomWidgetFactory(
    ObjectWidget,
    Image
    )
