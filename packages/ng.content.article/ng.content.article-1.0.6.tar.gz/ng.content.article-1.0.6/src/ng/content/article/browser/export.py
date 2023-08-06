### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Export mix in for export page of article

$Id: export.py 51224 2008-07-01 09:00:22Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51224 $"
 
from zope.interface import Interface
from ng.app.converter.object2psadapter.interfaces import IPropertySheet
                
class ExportView(object) :
    attrname = "export"

    def __call__(self) :
        self.request.response.setHeader("ContentType","text/plain")
        return IPropertySheet(self.context)[self.attrname]

        
        
        
