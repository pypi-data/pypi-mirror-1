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
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"

from zope.schema.interfaces import IObject
from zope.schema import TextLine
from zope.interface import Interface

class ISmartImageField(IObject):
    """Smart Image Field"""

    scale = TextLine()
    