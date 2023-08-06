### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""SiteUrl adapters for the Zope 3 based issue package

$Id: smartimageadapter.py 35337 2008-05-28 09:01:39Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"

from zope.interface import implements
from interfaces import ISmartImageAdapter
from ks.smartimage.smartimagecache.interfaces import ISmartImageProp
from zope.publisher.browser import BrowserView
from zope.traversing.browser.absoluteurl import absoluteURL
from scale import scale
from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds
from zope.app.file.image import Image
from zope.app.container.contained import contained,uncontained
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.component.interfaces import ComponentLookupError
import time

from logging import getLogger

logger = getLogger('ks.smartimage')

class SmartImageViewGetBase(BrowserView) :
    def __call__(self) :
        try :
            cache = getUtility(ISmartImageProp)
        except ComponentLookupError,msg :
            logger.warning("Lookup cache failed", exc_info=True)
        else :
            if cache.iscached :
                self.request.response.setHeader('Expires',
                    time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime(time.time()+cache.interval))
                    )
                self.request.response.setHeader('Last-Modified',
                    time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime(time.time()-cache.interval))
                    )
            else :
                self.request.response.setHeader('Expires',
                    time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime(time.time()))
                    )

#class SmartImageViewGet(SmartImageViewGetBase) :
#    def __call__(self) :
#        SmartImageViewGetBase.__call__(self)
#        self.request.response.setHeader("Content-Type",self.context.image.contentType)
#        return self.context.image.data

class SmartImageGet(SmartImageViewGetBase) :
    def __call__(self) :
        SmartImageViewGetBase.__call__(self)
        self.request.response.setHeader("Content-Type",self.context.contentType)
        return self.context.data

class SmartImageAdapter(object):
    implements(ISmartImageAdapter)

    def __init__(self,context):
        self.context = context

    def getfromCache(self, name):
        ids = getUtility(IIntIds,context=self.context.__parent__)
        id = ids.getId(self.context)
        cache = getUtility(ISmartImageProp)
        imname = name + '-' + str(id)
        if cache.has_key(imname):
            return cache[imname]
        else :
            return self.savetoCache(name)

    def savetoCache(self, name):
        ids = getUtility(IIntIds,context=self.context.__parent__)
        id = ids.getId(self.context)
        cache = getUtility(ISmartImageProp)
        imname = name + '-' + str(id)

        for sc in cache.scales:
            if sc.name == name:
                if self.context.data:
                    body = scale(self.context.data,cache.mode,cache.format,sc.width,sc.height,cache.maxratio,cache.resample,cache.quality)
                else:
                    body = self.context.data
                im = Image(body)
                notify(ObjectCreatedEvent(im))
                if cache.has_key(imname):
                    uncontained(cache[imname],cache)
                    del cache[imname]

                cache[imname] = im
                return contained(im,cache)
        raise KeyError,name

class SmartImageAdapterById(SmartImageAdapter) :
    implements(ISmartImageAdapter)

    def __init__(self,context):
        ids = getUtility(IIntIds,context=context.__parent__)
        self.context = ids.getObject(int(context.lastname))
