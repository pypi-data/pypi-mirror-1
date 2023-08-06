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
from zope.app.file.interfaces import IImage
from zope.schema import TextLine
from ks.schema.smartbytes.smartbytes import SmartBytes
from ks.schema.notset.notset import BoolNotSet

import zope.i18nmessageid
_ = zope.i18nmessageid.MessageFactory('ks.smartimage')

class ISmartImage(IImage) :

    data = SmartBytes(
        title=IImage['data'].title,
        description=IImage['data'].description,
        default=IImage['data'].default,
        missing_value=IImage['data'].missing_value,
        required=IImage['data'].required,
        )

    title = TextLine(
                    title = _(u"Title"),
                    description = _(u"Title"),
                    default = u'',
                    required = False,
                    )

    clearData = BoolNotSet(
        title=_(u'Clear Data'),
        description=_(u'Clear Data'),
        default=False,
        missing_value=False,
        required=False,
        )
