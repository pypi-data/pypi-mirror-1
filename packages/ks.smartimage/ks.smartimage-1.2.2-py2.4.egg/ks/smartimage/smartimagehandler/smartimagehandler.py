### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Handlers for the Zope 3 based smartimage package

$Id: smartimagehandler.py 35319 2007-12-31 04:26:30Z cray $
"""
__author__  = "Anton Oprya"
__license__ = "ZPL"
__version__ = "$Revision: 35319 $"
__date__ = "$Date: 2007-12-31 06:26:30 +0200 (Mon, 31 Dec 2007) $"

from zope.component import ComponentLookupError, getUtility, getMultiAdapter
from ks.smartimage.smartimagecache.interfaces import ISmartImageProp
from ks.smartimage.smartimageadapter.interfaces import ISmartImageAdapter
from zope.component.interfaces import ComponentLookupError
from ks.smartimage.interfaces import ISmartImage
from zope.app.intid.interfaces import IIntIds
import math

from logging import getLogger

logger = getLogger('ks.smartimage')

def imageModify(ob ,event):
    try :
        cache = getUtility(ISmartImageProp)
    except ComponentLookupError,msg :
        logger.warning("Create cache image fault", exc_info=True)
    else :
        for sc in cache.scales:
            smim = ISmartImageAdapter(ob)
            smim.savetoCache(sc.name)

def imageDelete(event):
    ob = event.object
    if ISmartImage.providedBy(ob) :
      try :
          cache = getUtility(ISmartImageProp)
          id = getUtility(IIntIds).getId(ob)
      except (ComponentLookupError,KeyError),msg :
          logger.warning("Delete cache image fault", exc_info=True)
      else :
          for sc in cache.scales:
              try :
                  del cache["%s-%s" % (sc.name,id)]
              except KeyError :
                  pass

def addToSmartImageCashe(ob, event):
    cache = getUtility(ISmartImageProp, context=ob)
    if event.newParent == cache:
        cache.elementsamount = len(cache)
        cache.elementssize = 0.0
        cache.meansize = 0.0
        for im in cache.values():
            cache.elementssize += len(im.data)
        cache.elementssize /= 1024
        cache.elementssize *= 100
        cache.elementssize = math.ceil(cache.elementssize)/100
        cache.meansize = math.ceil(cache.elementssize/cache.elementsamount*100)/100



def deleteFromSmartImageCashe(ob, event):
    cache = getUtility(ISmartImageProp, context=ob)
    if event.oldParent == cache:
        cache.elementsamount = len(cache)-1
        cache.elementssize = 0.0
        cache.meansize = 0.0
        if cache.elementsamount:
            for im in cache.values():
                cache.elementssize += len(im.data)
            cache.elementssize /= 1024
            cache.elementssize *= 100
            cache.elementssize = math.ceil(cache.elementssize)/100
            cache.meansize = math.ceil(cache.elementssize/cache.elementsamount*100)/100
