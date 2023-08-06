### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""HMTMLDisplayWidget class for the Zope 3 based smartimage package

$Id: smartimagefield.py 35337 2008-05-28 09:01:39Z cray $
"""

__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"
__credits__ = "Based heavily on zope.app.form.browser.objectwidget.ObjectWidget"

from zope.schema import Object
from interfaces import ISmartImageField
from zope.interface import implements
from ks.smartimage.interfaces import ISmartImage

from zope.event import notify
from zope.app.container.contained import containedEvent,contained, ObjectAddedEvent
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.security.proxy import removeSecurityProxy
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
        ob = removeSecurityProxy(ob)
        ob.__parent__ = removeSecurityProxy(content)
        ob.__name__ = "++attribute++" + self.getName()
        logger.debug("SET::::")
        logger.debug(removeSecurityProxy(content).__parent__)
        super(SmartImage, self).set(content,ob)
        notify(ObjectAddedEvent(ob))
        notify(ObjectModifiedEvent(ob))
