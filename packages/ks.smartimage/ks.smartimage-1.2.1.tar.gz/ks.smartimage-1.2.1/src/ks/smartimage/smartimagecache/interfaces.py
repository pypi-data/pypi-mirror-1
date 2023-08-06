### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Inrefaces for the Zope 3 based smartimagecache package

$Id: interfaces.py 35337 2008-05-28 09:01:39Z cray $
"""
__author__  = "Anton Oprya"
__license__ = "ZPL"
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"

from zope.interface import Interface
from zope.schema import TextLine, Float, Tuple, Object, Int, Bool, Choice
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.interfaces import IContainer
from PIL import Image

from ks.smartimage.interfaces import _

class IScale(Interface):

    name = TextLine(
                    title = _(u"Name"),
                    description = _(u"Name"),
                    default = u'',
                    )

    width = Int(
                title = _(u"Image width"),
                description = _(u"Image width"),
                min = 0,
                max = 1280,
                default = 100,
                )

    height = Int(
                 title = _(u"Image height"),
                 description = _(u"Image height"),
                 min = 0,
                 max = 1024,
                 default = 100,
                 )

class ISmartImageProp(Interface):

    scales = Tuple(
                   title = _(u'Scales'),
                   value_type=Object(schema=IScale, title = _(u"Scale"))
                   )

    mode = TextLine(
                        title = _(u"Image Mode"),
                        description = _(u"Image Mode"),
                        default = u'RGB',
                        )

    format = TextLine(
                        title = _(u"Image Format"),
                        description = _(u"Image Format"),
                        default = u'JPEG',
                        )

    maxratio = Float(
                     default = 100.,
                     title = _(u'Max Image Resize Ratio'),
                     description = _(u'Max Image Resize Ratio'),
                     )

    iscached = Bool(
                    title = _(u'Use cache headers'),
                    default=True
                    )

    interval = Int(
                    title = _(u'Cache interval in seconds'),
                    default=900
                    )

    quality = Int(title = _(u'Quality of Conversion'),
                        default=90)

    resample = Choice(title = _(u'Resample Type'),
                    vocabulary = 'ResampleVocabulary',
                    required=True, default=Image.ANTIALIAS
                    );

    scale = Choice(title = _(u'Default Scale'),
                    description = _(u'Scale to use as default in any widgets and so on'),
                    vocabulary = 'ScaleVocabulary',
                    required=True)

    basepath = TextLine(
        title = _(u"Base Path"),
        description = _(u"Base Path for Cached Images Url"),
        default = u'',
        required=False,
       )

    use_basepath = Bool(
         title = _(u"Use Base Path"),
         description = _(u"Use Base Path for Cached Images Url"),
         default = False,
        )

class IStat(Interface):

    elementsamount = Int(
                          title = _(u'Amount of elements'),
                          readonly = True
                          )

    elementssize = Float(
                          title = _(u'Summary size of elements'),
                          readonly = True
                          )

    meansize = Float(
                     title = _(u'Mean size of elements'),
                     readonly = True
                     )

class ISmartImageCacheContent(Interface):
    pass

class ISmartImageCacheContainer(IContainer):

    def __setitem__(name, object) :
        pass

    __setitem__.precondition = ItemTypePrecondition(ISmartImageCacheContent)


