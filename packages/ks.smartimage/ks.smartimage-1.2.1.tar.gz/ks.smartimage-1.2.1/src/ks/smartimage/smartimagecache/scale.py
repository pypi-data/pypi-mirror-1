### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007                                       
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007                                       
#######################################################################
"""SmartImageCache class for the Zope 3 based smartimage package

$Id: scale.py 35337 2008-05-28 09:01:39Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"

from zope.interface import implements
from interfaces import IScale

class Scale(object) :

    implements(IScale)

    name = u''

    width = 100

    height = 100


    def __init__(self, name=u'', width=100, height=100, *kv, **kw):
        super(Scale, self).__init__(self, *kv, **kw)
        self.name = name
        self.width = width
        self.height = height
