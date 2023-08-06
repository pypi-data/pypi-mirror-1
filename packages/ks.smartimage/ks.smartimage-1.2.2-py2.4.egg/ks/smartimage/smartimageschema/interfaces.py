### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Inrefaces for the Zope 3 based smartimagecache package

$Id: interfaces.py 35338 2008-06-12 18:42:18Z anatoly $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35338 $"
__date__ = "$Date: 2008-06-12 21:42:18 +0300 (Thu, 12 Jun 2008) $"

from zope.schema.interfaces import IObject
from zope.schema import TextLine
from zope.interface import Interface

class ISmartImageField(IObject):
    """Smart Image Field"""

    scale = TextLine()

class ISmartImageParent(Interface):
    """Smart Image Parent"""
