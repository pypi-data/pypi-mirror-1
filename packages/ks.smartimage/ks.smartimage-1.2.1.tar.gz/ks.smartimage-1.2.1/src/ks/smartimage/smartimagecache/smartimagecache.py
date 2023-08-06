### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""SmartImageCache class for the Zope 3 based smartimage package

$Id: smartimagecache.py 35337 2008-05-28 09:01:39Z cray $
"""
__author__  = "Anton Oprya"
__license__ = "ZPL"
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"

from zope.interface import implements
from interfaces import IScale, ISmartImageProp, ISmartImageCacheContainer, IStat
from zope.app.container.btree import BTreeContainer

from PIL import Image
from scale import Scale

class SmartImageCache(BTreeContainer):
    implements(ISmartImageProp, ISmartImageCacheContainer, IStat)

    scales = ()

    format = u'JPEG'

    mode = u'RGB'

    maxratio = 100.0

    interval = 900

    iscached = True

    elementsamount = 0

    elementssize = 0.0

    meansize = 0.0

    resample = Image.ANTIALIAS

    quality = 90

    scale = ""

    basepath = u""

    use_basepath = False
