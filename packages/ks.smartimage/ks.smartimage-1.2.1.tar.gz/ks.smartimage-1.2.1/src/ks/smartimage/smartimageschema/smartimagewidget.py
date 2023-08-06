### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""SmartImageWidger widget for the Zope 3 based smartimage package

$Id: smartimagewidget.py 35337 2008-05-28 09:01:39Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"

from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import ObjectWidget as ObjectWidgetBase

from ks.smartimage.smartimage import SmartImage
from zope.security.proxy import removeSecurityProxy
from zope.app.form.utility import setUpWidgets, applyWidgetsChanges

from zope.app.container.contained import containedEvent,contained, ObjectAddedEvent
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.app.zapi import absoluteURL
from zope.app.form.browser.widget import renderElement
from zope.interface import Interface
from zope.component import ComponentLookupError, getUtility, getMultiAdapter
from ks.smartimage.smartimagecache.interfaces import ISmartImageProp
from ks.smartimage.smartimageadapter.interfaces import ISmartImageContainer
from smartimagedisplaywidget import ImageDisplay

class ObjectWidget(ImageDisplay,ObjectWidgetBase) :


    def getInputValue(self):
        ob = removeSecurityProxy(super(ObjectWidget,self).getInputValue())
        return ob

    def applyChanges(self, content):
        field = self.context
        value = field.query(content, None)
        if value is None:
            value = self.factory()

        changes = applyWidgetsChanges(self, field.schema, target=value,
                                               names=self.names)

        if changes:
            if 'clearData' in self.names:
                clear = self.clearData_widget.getInputValue()
                if clear:
                    value.contentType = u''
                    value.data = ''
            #ob = removeSecurityProxy(value)
            #ob.__parent__ = removeSecurityProxy(content)
            #ob.__name__ = "++attribute++" + field.getName()
            field.set(content, value)
            #notify(ObjectAddedEvent(ob))
            #notify(ObjectModifiedEvent(ob))
            return True
        return False

    def __call__(self):
        value = self.context.query(self.context.context, None)
        if value is None or value == self.context.missing_value:
            value = self.factory()

        return "\n".join([self.imagedisplay(value),super(ObjectWidget, self).__call__()])

SmartImageWidget = CustomWidgetFactory(ObjectWidget, SmartImage)
