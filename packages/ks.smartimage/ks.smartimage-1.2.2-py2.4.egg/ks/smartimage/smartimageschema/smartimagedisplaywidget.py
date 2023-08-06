### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""SmartImageDisplayWidget class for the Zope 3 based ks.widget package

$Id: smartimagedisplaywidget.py 35338 2008-06-12 18:42:18Z anatoly $
"""

__author__  = "Anatoly Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 35338 $"
__date__ = "$Date: 2008-06-12 21:42:18 +0300 (Thu, 12 Jun 2008) $"
__credits__ = "Based heavily on Anatoly Bubenkov sources"

from zope.interface import implements
from zope.interface import Interface
from zope.app.form.interfaces import IDisplayWidget
from zope.app.form.browser.widget import DisplayWidget
from zope.component import getMultiAdapter
from zope.security.proxy import getObject
from imagedisplay import ImageDisplay
from zope.app.form.browser.widget import renderElement


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

        return renderElement('a', href=self.imageurl(value),
                             contents=self.imagedisplay(value),
                             id=self.name)
