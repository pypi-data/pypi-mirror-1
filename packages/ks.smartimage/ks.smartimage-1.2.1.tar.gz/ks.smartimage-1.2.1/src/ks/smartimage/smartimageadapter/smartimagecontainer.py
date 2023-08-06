### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""SmartImageContainerAdapter for the Zope 3 based smartimage package

$Id: smartimagecontainer.py 35337 2008-05-28 09:01:39Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"

from zope.interface import implements
from zope.publisher.browser import BrowserView
from interfaces import ISmartImageContainer,ISmartImageCached
from zope.location.interfaces import ILocation
from zope.component import ComponentLookupError, getUtility
from ks.smartimage.smartimagecache.interfaces import ISmartImageProp
from smartimagecached import SmartImageCached

from logging import getLogger

logger = getLogger('ks.smartimage')

class SmartImageContainerAdapter(object) :
    u"""Контейнер отмасштабированных изображений """
    
    implements(ISmartImageContainer)
    __name__ = "@@smartimagecontainer"


    scales = []
    ignore = False

    def __init__(self,context) :
        self.context = context
        self.scales = [ scale.name for scale in getUtility(ISmartImageProp).scales ]
        
    def __contains__(self,key) :
        return key in self.scales or self.ignore
        
    def items(self) :
        return [ (key,self[key]) for key in self.keys() ]
        
    def keys(self) :
        return self.scales[:]
        
    def values(self) :
        return [ self[key] for key in self.keys() ]        
        
    def __iter__(self) :
        return iter(self.keys())
        
    def __len__(self) :
        return len(self.keys())                             

    def __getitem__(self,name) :
        return SmartImageCached(self,name)

    def get(self,name,d) :
        try :    
            return self[name]
        except KeyError :
            return d            

class SmartImageContainerView(SmartImageContainerAdapter, BrowserView) :
    u"""Контейнер отмасштабированных изображений """
    
    implements(ILocation)


    def __init__(self,context,request) :
        self.__parent__ = context
        BrowserView.__init__(self,context,request)
        SmartImageContainerAdapter.__init__(self,context)


