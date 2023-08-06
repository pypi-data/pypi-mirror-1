### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""SmartImageCache class for the Zope 3 based smartimage package

$Id: smartimagecache.py 35335 2008-05-27 16:02:13Z anatoly $
"""
__author__  = "Anton Oprya"
__license__ = "ZPL"
__version__ = "$Revision: 35335 $"
__date__ = "$Date: 2008-05-27 19:02:13 +0300 (Tue, 27 May 2008) $"

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
