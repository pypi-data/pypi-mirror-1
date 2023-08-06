### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""HMTMLDisplayWidget class for the Zope 3 based smartimage package

$Id: smartimagefield.py 35338 2008-06-12 18:42:18Z anatoly $
"""

__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35338 $"
__date__ = "$Date: 2008-06-12 21:42:18 +0300 (Thu, 12 Jun 2008) $"
__credits__ = "Based heavily on zope.app.form.browser.objectwidget.ObjectWidget"

from zope.schema import Object
from interfaces import ISmartImageField, ISmartImageParent
from zope.interface import implements
from ks.smartimage.interfaces import ISmartImage

from zope.event import notify
from zope.app.container.contained import containedEvent,contained, ObjectAddedEvent
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.security.proxy import removeSecurityProxy, getObject
import logging
logger = logging.getLogger('ks.smartimage')

class SmartImage(Object):
    implements(ISmartImageField)
    scale = None
    schema = ISmartImage
    def __init__(self, scale=None, **kw):
        self.scale = scale
        self.schema = ISmartImage
        super(SmartImage, self).__init__(ISmartImage, **kw)

    def set(self,content,ob) :
        ob = getObject(ob)
        clean_content = getObject(ISmartImageParent(content))
        ob.__parent__ = clean_content
        ob.__name__ = "++attribute++" + self.getName()
        super(SmartImage, self).set(content,ob)
        notify(ObjectAddedEvent(ob))
        notify(ObjectModifiedEvent(ob))
