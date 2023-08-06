### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""Stat view

$Id: view.py 35337 2008-05-28 09:01:39Z cray $
"""
__author__  = "Anton Oprya"
__license__ = "ZPL"
__version__ = "$Revision: 35337 $"
__date__ = "$Date: 2008-05-28 13:01:39 +0400 (Срд, 28 Май 2008) $"

from zope.publisher.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from ks.smartimage.smartimageadapter.interfaces import ISmartImageAdapter
from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds
from ks.smartimage.interfaces import ISmartImage
from zope.interface import providedBy

from logging import getLogger

logger = getLogger('ks.smartimage')

class Stat(BrowserView):
    stat_view = ViewPageTemplateFile("stat.pt")

    def __init__(self, context, request):
        super(Stat, self).__init__(context, request)
        self.context = context
        self.request = request

    def clearSmartImageCache(self, *kv,**kw):
        while len(self.context) > 0:
            for key in self.context.keys():
                del self.context[key]
        return self.stat_view(self,*kv,**kw)

    def reindexSmartImageCache(self, *kv,**kw):
        res = set()
        while len(self.context) > 0:
            for key in self.context.keys():
                try:
                    res.add(int(key.split('-')[-1]))
                except ValueError, msg:
                    logger.warning('%(key)s is wrong name for SmartImageCache element', dict(key=key), exc_info=True)
                del self.context[key]
        ids = getUtility(IIntIds,context=self.context)
        for id in res:
            try:
                ob = ids.getObject(id)
                for sc in self.context.scales:
                    smim = ISmartImageAdapter(ob)
                    smim.savetoCache(sc.name)
            except:
                logger.warning('Lookup %(id)s error', dict(id=id), exc_info=True)
        return self.stat_view(self,*kv,**kw)

    def reindexalternativeSmartImageCache(self, *kv,**kw):
        ids = getUtility(IIntIds,context=self.context)
        for id, kr in ids.items():
            try:
                ob = ids.getObject(id)
                if ISmartImage.providedBy(ob):
                    for sc in self.context.scales:
                        smim = ISmartImageAdapter(ob)
                        smim.savetoCache(sc.name)
            except:
                logger.warning('Lookup %(id)s error', dict(id=id), exc_info=True)
        return self.stat_view(self,*kv,**kw)


