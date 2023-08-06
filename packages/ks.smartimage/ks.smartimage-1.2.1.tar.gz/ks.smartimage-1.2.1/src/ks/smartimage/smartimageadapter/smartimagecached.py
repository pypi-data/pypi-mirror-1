### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""SiteUrl adapters for the Zope 3 based issue package

$Id: smartimagecached.py 35337 2008-05-28 09:01:39Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"

from zope.interface import implements
from interfaces import ISmartImageCached,ISmartImageAdapter
from zope.app.container.contained import Contained
from zope.cachedescriptors.property import Lazy
from zope.publisher.browser import BrowserView
from zope.app.intid.interfaces import IIntIds
from ks.smartimage.smartimagecache.interfaces import ISmartImageProp

from zope.component import ComponentLookupError, getUtility, getMultiAdapter

from zope.traversing.browser.absoluteurl import absoluteURL

from logging import getLogger
logger = getLogger('ks.smartimage')

class SmartImageCached(Contained) :
    implements(ISmartImageCached)

    def __init__(self,context,name) :
        self.context = self.__parent__ = context
        self.__name__ = name

    @Lazy
    def getCachedImage(self) :
        return ISmartImageAdapter(self.context.context).getfromCache(self.__name__)        

    def getSize(self) :
        return self.getCachedImage.getSize()

    def getImageSize(self) :
        return self.getCachedImage.getImageSize()
        
    @Lazy
    def getImage(self) :
        return self.context.context        

    @Lazy
    def uniqid(self) :
     #   ids = getUtility(IIntIds,context=self.context)
        ids = getUtility(IIntIds)
        return ids.getId(self.getImage)
        
    @property
    def height(self) :
        return self.getImageSize()[1]
              
    @property
    def width(self) :
        return self.getImageSize()[0]

    @property
    def contentType(self) :
        return self.getCachedImage.contentType
        
    @property
    def data(self) :        
        return self.getCachedImage.data

    @property
    def title(self) :
        return self.getImage.title

    @property
    def url(self) :
        try :
            request = self.context.request
        except AttributeError,msg :
            logger.warning("Use url image function without request is not possible")
            return ""
        else :
            cache = getUtility(ISmartImageProp)
            if cache.use_basepath :
                src = ""
                if cache.basepath :
                    src = cache.basepath + "/"
                        
                return src + "@@smartimagebyid/" +  str(self.uniqid) + "/" + self.__name__ + "/get" 
            else:
                return absoluteURL(self,self.context.request) + "/get"

#    @property            
    def tag(self,**kw) :
        if self.getImage.getSize() > 0 :
            return '<img src="%s" width="%s" height="%s" alt="%s" %s/>' % (
                self.url,self.width,self.height,self.title,
                " ".join([('%s="%s"' % (x,y)) for x,y in kw.items()])
                )
        return ""            
