### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Interfaces for the Zope 3 based smartimageadapter package

$Id: interfaces.py 35337 2008-05-28 09:01:39Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"

from zope.interface import Interface
from zope.schema import Text, TextLine, Date, Datetime, Tuple, Set, Choice, Field, Float
from ks.smartimage.interfaces import _
from zope.app.file.interfaces import IImage

from zope.app.container.interfaces import IReadContainer
from zope.interface.common.mapping import IItemMapping
from zope.app.container.interfaces  import ISimpleReadContainer

class ISmartImageById(ISimpleReadContainer) :
    pass

class ISmartImageContainer(IReadContainer):
    pass

class ISmartImageCached(IImage) :

    height = TextLine(title=_(u'Height'),
        description=_(u'Image Height'),
        default=u'',
        required=False)

    width = TextLine(title=_(u'Width'),
        description=_(u'Image Width'),
        default=u'',
        required=False)

    title = TextLine(title=_(u'Title'),
        description=_(u'Image Title'),
        default=u'',
        required=False)

    uniqid = TextLine(title=_(u'Unique ID'),
        description=_(u'Image Unique ID'),
        default=u'',
        required=False)

    url = TextLine(title=_(u'URL'),
        description=_(u'URL'),
        default=u'',
        required=False)

    tag = TextLine(title=_(u'TAG'),
        description=_(u'Image Tag'),
        default=u'',
        required=False)

class ISmartImageAdapter(Interface):

    def getfromCache(name):
        """Get image body from cache"""

    def savetoCache(name):
        """Save resized image to Cache"""

class IScaleError(Interface):

    sizein = Tuple(title=_(u'Input Image Size'), required=False)

    sizeout = TextLine(title=_(u'Output Image Size'), required=False)

    ratio = Float(title=_(u'Resize Ratio'), required=False)

    msg = TextLine(title=_(u'Error message'), required=False)

    res = Field()

