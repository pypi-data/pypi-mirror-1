### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""SmartImageDisplayWidget class for the Zope 3 based ks.widget package

$Id: smartimagedisplaywidget.py 35337 2008-05-28 09:01:39Z cray $
"""

__author__  = "Anatoly Orlov"
__license__ = "ZPL" 
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"
__credits__ = "Based heavily on Anatoly Bubenkov sources"

from zope.interface import implements
from zope.interface import Interface
from zope.app.form.interfaces import IDisplayWidget
from zope.app.form.browser.widget import DisplayWidget
from zope.component import getMultiAdapter
from zope.security.proxy import getObject
from imagedisplay import ImageDisplay


class SmartImageDisplayWidget(ImageDisplay, DisplayWidget):
    """Smart Image Display Widget"""

    implements (IDisplayWidget)

    def __call__(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        if value == self.context.missing_value:
            return ""
                    
        return self.imagedisplay(value)
        