### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Container adapters the Zope 3 based ng.content.article package

$Id: containeradapter.py 51577 2008-08-31 12:16:31Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51577 $"
 
from zope.interface import Interface,implements
from zope.app.container.interfaces import  IReadContainer        
from ng.content.article.interfaces import IContentShowable, IIconShowable, IAbstractShowable
from ng.content.article.interfaces import ISContent, IDocKind, IContentContainer
from ng.content.article.interfaces import IContentContainer, IIconContainer, IAbstractContainer


class BaseContainerAdapter(object) :
    def __init__(self,context,*kv,**kw) :
        self.context = context
            
    def __getitem__(self,key) :
        try :
            res = self.context[key]
            return res
        except Exception,msg :
            print msg            

    def  __contains__(self,key) :
        try :
            self.__getitem__(key)
        except KeyError :
            return False
            
        return True            
        
    def keys(self) :
        return ( key for key,value in self.items() if key in self)
 
    def items(self) :
        
        for key in self.context.keys() :
            try :
                res = self[key]
                yield (key,res)
            except KeyError,msg :
                pass                
 
    def get(self, key, default=None) :
        try :
            return self[key]
        except KeyError :
            return default              
        
    def __iter__(self) :
        return iter(self.keys())

    def values(self) :
        return [ value for key,value in self.items()]

    def __len__(self) :
        return len(list(self.items()))

class ShowContainerAdapter(BaseContainerAdapter) :

    iface = IContentShowable

    def __getitem__(self,key) :
        value = super(ShowContainerAdapter,self).__getitem__(key)
        if self.iface.providedBy(value) :
            try :
                if not IDocKind(value).ishidden :
                    return value
            except TypeError :
                return value
        raise KeyError,key                               
                                                                                            

class PageContainerAdapter(ShowContainerAdapter) :

    def __getitem__(self,key) :
        value = super(PageContainerAdapter,self).__getitem__(key)
        try :
            if ISContent(self.context).iscontent :
                if not IDocKind(value).isdivision :
                    return value                        
            raise KeyError, key                                    
        except TypeError :
            raise KeyError,key                

class ContentContainerAdapter(ShowContainerAdapter) :
    implements(IContentContainer)
    
    def __getitem__(self,key) :
        value = super(ContentContainerAdapter,self).__getitem__(key)
        try :
            if ISContent(self.context).iscontent :
                if not IDocKind(value).isdivision :
                    raise KeyError, key            
            return value                    
        except TypeError :
            return value

class IconContainerAdapter(ContentContainerAdapter) :
    implements(IIconContainer) 
    iface = IIconShowable

class AbstractContainerAdapter(ContentContainerAdapter) :
    implements(IAbstractContainer) 
    iface = IAbstractShowable

                