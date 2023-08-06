### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""SmartImageDisplayWidget class for the Zope 3 based ks.widget package

$Id: imagedisplay.py 35337 2008-05-28 09:01:39Z cray $
"""

__author__  = "Anatoly Orlov"
__license__ = "ZPL" 
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"
__credits__ = "Based heavily on Anatoly Bubenkov sources"

from zope.interface import Interface
from zope.app.zapi import absoluteURL
from zope.app.form.browser.widget import DisplayWidget, renderElement
from ks.smartimage.smartimageadapter.interfaces import ISmartImageContainer
from ks.smartimage.smartimagecache.interfaces import ISmartImageProp
from zope.component import ComponentLookupError, getUtility, getMultiAdapter

from logging import getLogger
logger = getLogger('ks.smartimage')

class ImageDisplay(object) :

    cssClass = u''

    extra = u''

    def imagedisplay(self,value) :
        res = [
         renderElement('p', contents=value.title)
        ]
        if value.data is not None and value.data:
            try :        
                cache = getUtility(ISmartImageProp)
            except ComponentLookupError, msg :
                logger.warning("Getting image cache fault, widgets will be used without cache", exc_info=False)
                src = absoluteURL(self.context.context,self.request) + \
                        "/++attribute++" + self.context.__name__ 
            else :
                img = ISmartImageContainer(value)[
                        self.context.scale or getUtility(ISmartImageProp).scale
                        ]

                if cache.use_basepath :
                    src = ""
                    if cache.basepath :
                        src = cache.basepath + "/"

                    src = src + "@@smartimagebyid/" +  str(img.uniqid) + "/" + img.__name__ + "/get"
                else :
                    src = absoluteURL(self.context.context,self.request) + \
                        "/++attribute++" + self.context.__name__ + "/" + \
                        "@@smartimagecontainer/" + img.__name__ + "/get"

            res.append(
                renderElement('img', src=src, alt=value.title, cssClass=self.cssClass, extra=self.extra)
                )

        return "\n".join(res)                                
        
