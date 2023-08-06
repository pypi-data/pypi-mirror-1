### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""SmartImageSelectAdapter for the Zope 3 based smartimage package

$Id: smartimagebyid.py 35337 2008-05-28 09:01:39Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"

from zope.interface import implements
from zope.publisher.browser import BrowserView
from interfaces import ISmartImageById,ISmartImageContainer,ISmartImageCached
from zope.location.interfaces import ILocation
from zope.component import getUtility
from ks.smartimage.smartimagecache.interfaces import ISmartImageProp
from smartimagecontainer import SmartImageContainerView

from logging import getLogger

logger = getLogger('ks.smartimage')

class SmartImageById(BrowserView) :
    u"""Дать изображение по идентификатору"""

    implements(ISmartImageById)

    __name__ = "@@smartimagebyid"
    
    def __init__(self,context,request) :
        super(SmartImageById,self).__init__(context,request)
        self.__parent__ = \
            self.context = context

    def __getitem__(self,name) :
        #ids = getUtility(IIntIds,context=self.context)
        #image = ids.getObject(int(self.name))
        adapter = SmartImageContainerView(self,self.request)
        adapter.__name__ = name
        self.lastname = name
        return adapter

    def __contains__(self,name) :
        return True
        
    def get(self,name,d) :
        return[name]         

    @property
    def title(self) :
        return "blablabla"
