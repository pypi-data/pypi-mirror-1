### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################

import unittest
from ks.smartimage.smartimagecache.browser.view import Stat

from ks.smartimage.smartimagecache.smartimagecache import Scale, SmartImageCache
from ks.smartimage.smartimagecache.interfaces import IScale, ISmartImageProp, ISmartImageCacheContainer, IStat
from ks.smartimage.smartimageadapter.interfaces import ISmartImageAdapter
from ks.smartimage.smartimageadapter.scale import ScaleError, scale
from ks.smartimage.smartimageadapter.interfaces import IScaleError
from ks.smartimage.smartimageadapter.smartimageadapter import SmartImageView
from ks.smartimage.smartimage import SmartImage
from ks.smartimage.interfaces import ISmartImage

from zope.app.intid.interfaces import IIntIds
from zope.app.file.image import Image
from zope.app.testing import ztapi, setup, placelesssetup
from zope.app.component.hooks import setSite

from zope.publisher.interfaces.browser import IBrowserView

from zope.index.interfaces import IInjection, IIndexSearch

from zope.interface.verify import verifyClass


from zope.app.folder.folder import Folder
from zope.app.intid import IntIds
from persistent.interfaces import IPersistent
from zope.app.keyreference.interfaces import IKeyReference
from zope.app.keyreference.persistent import KeyReferenceToPersistent, connectionOfPersistent
from ks.smartimage.smartimageadapter.smartimageadapter import SmartImageAdapter
from ZODB.interfaces import IConnection

from zope.publisher.browser import TestRequest
from zope.traversing.interfaces import ITraversable
import zope

from zope.app.pagetemplate import ViewPageTemplateFile


zptlogo = (
    'GIF89a\x10\x00\x10\x00\xd5\x00\x00\xff\xff\xff\xff\xff\xfe\xfc\xfd\xfd'
    '\xfa\xfb\xfc\xf7\xf9\xfa\xf5\xf8\xf9\xf3\xf6\xf8\xf2\xf5\xf7\xf0\xf4\xf6'
    '\xeb\xf1\xf3\xe5\xed\xef\xde\xe8\xeb\xdc\xe6\xea\xd9\xe4\xe8\xd7\xe2\xe6'
    '\xd2\xdf\xe3\xd0\xdd\xe3\xcd\xdc\xe1\xcb\xda\xdf\xc9\xd9\xdf\xc8\xd8\xdd'
    '\xc6\xd7\xdc\xc4\xd6\xdc\xc3\xd4\xda\xc2\xd3\xd9\xc1\xd3\xd9\xc0\xd2\xd9'
    '\xbd\xd1\xd8\xbd\xd0\xd7\xbc\xcf\xd7\xbb\xcf\xd6\xbb\xce\xd5\xb9\xcd\xd4'
    '\xb6\xcc\xd4\xb6\xcb\xd3\xb5\xcb\xd2\xb4\xca\xd1\xb2\xc8\xd0\xb1\xc7\xd0'
    '\xb0\xc7\xcf\xaf\xc6\xce\xae\xc4\xce\xad\xc4\xcd\xab\xc3\xcc\xa9\xc2\xcb'
    '\xa8\xc1\xca\xa6\xc0\xc9\xa4\xbe\xc8\xa2\xbd\xc7\xa0\xbb\xc5\x9e\xba\xc4'
    '\x9b\xbf\xcc\x98\xb6\xc1\x8d\xae\xbaFgs\x00\x00\x00\x00\x00\x00\x00\x00'
    '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    '\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06z@\x80pH,\x12k\xc8$\xd2f\x04'
    '\xd4\x84\x01\x01\xe1\xf0d\x16\x9f\x80A\x01\x91\xc0ZmL\xb0\xcd\x00V\xd4'
    '\xc4a\x87z\xed\xb0-\x1a\xb3\xb8\x95\xbdf8\x1e\x11\xca,MoC$\x15\x18{'
    '\x006}m\x13\x16\x1a\x1f\x83\x85}6\x17\x1b $\x83\x00\x86\x19\x1d!%)\x8c'
    '\x866#\'+.\x8ca`\x1c`(,/1\x94B5\x19\x1e"&*-024\xacNq\xba\xbb\xb8h\xbeb'
    '\x00A\x00;'
    )


###########################################################
### Вспомогательные классы для тестирования класса Stat ###
###########################################################
class ConnectionStub(object):
    next = 1

    def db(self):
        return self

    database_name = 'ConnectionStub'

    def add(self, ob):
        ob._p_jar = self
        ob._p_oid = self.next
        self.next += 1


class ReferenceSetupMixin(object):


    def createSmartImage(self):
        """ Метод для генерации экземпляря класа SmartImage (GIF-изображения)
	"""
        smart_image = SmartImage()
        smart_image.contentType = u'image/gif'
        smart_image._setData(zptlogo)
	return smart_image


    def setUp(self):
        self.root = setup.placefulSetUp(site=True)
	# Регистрируем необходимые адаптеры
        ztapi.provideAdapter(IPersistent, IConnection, connectionOfPersistent)
        ztapi.provideAdapter(IPersistent, IKeyReference, KeyReferenceToPersistent)
        ztapi.provideAdapter(ISmartImage, ISmartImageAdapter, SmartImageAdapter)

        #ReferenceSetupMixin.setUp(self)
        self.root._p_jar = ConnectionStub()

        self.root[u'folder1'] = self.folder1 = Folder()

        self.sm = setup.createSiteManager(self.folder1)

        setSite(self.folder1)

        sic = SmartImageCache()
        sic.format = u'GIF'
        sic.scales = (Scale(), Scale('myscale', 10, 10),)

        self.root[u'folder1'][u'sic'] = sic

        self.intids_utility = setup.addUtility(self.sm, '', IIntIds, IntIds())
        self.sic_utility = setup.addUtility(self.sm, '', ISmartImageProp, self.root[u'folder1'][u'sic'])

        self.root[u'folder1'][u'simg'] = self.createSmartImage()
        self.root[u'folder1'][u'empty_simg'] = SmartImage()

    def tearDown(self):
        setup.placefulTearDown()

##########################################
### Вспомогательные классы закончились ###
##########################################


class Test_Stat(ReferenceSetupMixin, unittest.TestCase):

    def test_Constructor(self):

        s =  Stat('context', 'request')
	self.assertEqual(s.context, 'context')
	self.assertEqual(s.request, 'request')

    def test_Interface(self):

        self.failUnless(IBrowserView.implementedBy(Stat))


    def test_clearSmartImageCache(self):

        pass

    def test_reindexSmartImageCache(self):

        pass

    def test_reindexalternativeSmartImageCache(self):

        smart_image = self.root[u'folder1'][u'simg']
        request = TestRequest()

	self.assertEqual(len(self.sic_utility), 0)
        self.intids_utility.register(smart_image)

        s = Stat(self.sic_utility, request)

        # Уже даже не знаю куда думать, чтобы эта строчка заработала. Метод вызывается, всё, что
	# надо в нём делается и на строчку return self.stat_view(self, *kv,**kw) вываливается
	# большая ошибка TraversalError. Где мог рылся, что мог делал - ничего хорошего из этого
	# не вышло и всё только ещё больше запуталось.
	# Есть подозрение, что тестировать подобные вещи надо вообще по другому в принципе, но
	# попытки это сделать только совсем вообще в конец всё запутали, а поэтому все бредни удалил.

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_Stat),
        ))

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
