### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Export mix in for export page of article

$Id: export.py 51946 2008-10-23 19:57:39Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51946 $"
 
from zope.interface import Interface
from ng.app.converter.object2psadapter.interfaces import IPropertySheet
                
class ExportView(object) :
    attrname = "export"

    def __call__(self) :
        self.request.response.setHeader("ContentType","text/plain")
        return IPropertySheet(self.context)[self.attrname]

        
        
        
