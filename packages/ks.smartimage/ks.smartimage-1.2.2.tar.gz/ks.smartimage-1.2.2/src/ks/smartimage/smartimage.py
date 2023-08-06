### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""SmartImageCache class for the Zope 3 based smartimage package

$Id: smartimage.py 23811 2007-11-15 10:10:37Z anton $
"""
__author__  = "Anton Oprya"
__license__ = "ZPL"
__version__ = "$Revision: 23811 $"
__date__ = "$Date: 2007-11-15 12:10:37 +0200 (Thu, 15 Nov 2007) $"

from zope.interface import implements
from interfaces import ISmartImage
from zope.app.file.image import Image
from zope.app.container.contained import Contained


class SmartImage(Image,Contained):
    implements(ISmartImage)

    title = u''

    clearData = False

    def __init__(self,*kv,**kw) :
        super(SmartImage,self).__init__(*kv,**kw)

