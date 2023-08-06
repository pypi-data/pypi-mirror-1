# -*- coding: utf-8 -*-
"""The subattributeeventdispatcher

$Id: subattributedispatcher.py 35337 2008-05-28 09:01:39Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "ZPL"
__version__ = "$Revision: 35337 $"
__credits__ = """Andrey Orlov, for idea and common control"""

import zope.component
from zope.app.container.interfaces import IContained
from ks.smartimage.interfaces import ISmartImage
import logging
logger = logging.getLogger('ks.smartimage')

def dispatchToSubattributes(object, event):
    for key,value in object.__dict__.items() :
        if key[0]!='_' :
            logger.debug("SMARTIMAGE KEY: %s", key)
            if ISmartImage.providedBy(value) :
                logger.debug("Ok")
                for ignored in zope.component.subscribers((value, event), None):
                    pass
