### -*- coding: utf-8 -*- #############################################
#######################################################################
""" Special widgets for maincontainer browser pages

$Id: widgets.py 51946 2008-10-23 19:57:39Z cray $
"""
__author__  = u"Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51946 $"

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
