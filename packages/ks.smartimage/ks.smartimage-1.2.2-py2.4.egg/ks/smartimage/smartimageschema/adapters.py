### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""$Id: adapters.py 35338 2008-06-12 18:42:18Z anatoly $
"""

__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35338 $"
__date__ = "$Date: 2008-06-12 21:42:18 +0300 (Thu, 12 Jun 2008) $"

from interfaces import ISmartImageParent
from zope.interface import implementer
from zope.component import adapter
from zope.interface import Interface

@adapter(None)
@implementer(ISmartImageParent)
def defaultSmartImageParent(context):
    return context
