### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""
$Id: test_smartimageadapter.py 35337 2008-05-28 09:01:39Z cray $
"""

import unittest

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


#from zope.app.form.interfaces import ConversionError
#from zope.app.form.interfaces import WidgetInputError, MissingInputError

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


#################################################################
### Вспомогательные классы для тестирования SmartImageAdapter ###
#################################################################
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


class testScaleError(unittest.TestCase):

    def _makeScaleError(self, *args, **kw):
        return ScaleError(*args, **kw)

    def test_Constructor(self):
        scale_error = self._makeScaleError((10,10), (20, 20), 3, u'ScaleError Message')
	self.assertEqual(scale_error.sizein, (10,10))
	self.assertEqual(scale_error.sizeout, (20,20))
	self.assertEqual(scale_error.ratio, 3)
	self.assertEqual(scale_error.msg, u'ScaleError Message')

    def test_sizein(self, *args, **kw):
        scale_error = self._makeScaleError((10,10), (20, 20), 3, u'ScaleError Message')
	self.assertEqual(scale_error.sizein, (10,10))
	scale_error.sizein = (15,15)
	self.assertEqual(scale_error.sizein, (15,15))
        # Тут я ещё хотел проверить то, что значением sizein может быть только tuple, однако строчка
	# scale_error.sizein = 5 выполняется без проблем и я уже даже не знаю, надо ли это проверять
	# То же самое про остальные атрибуты ...

    def test_sizeout(self, *args, **kw):
        scale_error = self._makeScaleError((10,10), (20, 20), 3, u'ScaleError Message')
	self.assertEqual(scale_error.sizeout, (20,20))
	scale_error.sizeout = (15,15)
	self.assertEqual(scale_error.sizeout, (15,15))

    def test_ratio(self, *args, **kw):
        scale_error = self._makeScaleError((10,10), (20, 20), 3, u'ScaleError Message')
	self.assertEqual(scale_error.ratio, 3)
	scale_error.ratio = 7
	self.assertEqual(scale_error.ratio, 7)

    def test_msg(self, *args, **kw):
        scale_error = self._makeScaleError((10,10), (20, 20), 3, u'ScaleError Message')
	self.assertEqual(scale_error.msg, u'ScaleError Message')
	scale_error.msg = u'New ScaleError Message'
	self.assertEqual(scale_error.msg, u'New ScaleError Message')

    def test_Interface(self):
        self.failUnless(IScaleError.implementedBy(ScaleError))
        self.failUnless(verifyClass(IScaleError, ScaleError))

class test_scale(unittest.TestCase):

    def test_Scaling(self, *args, **kw):

        # Создаём изображение с нужными свойствами
        smart_image = SmartImage()
        smart_image.contentType = u'image/gif'
        smart_image._setData(zptlogo)

        # Создаём кэш с нужными значениями масштабов и свойствами
        sic = SmartImageCache()
	sic.format = u'GIF'
	# Для тестирования понадобятся 2 масштаба с разными свойствами
	sic.scales = (Scale(), Scale(u'SomeScale', 10, 10),)

        # Для начала вопсользуется масштабом под индексом 0
        sc = sic.scales[0]
	# устанавливаем максимальное значение коэффициента масштабирования равное 1
	sic.maxratio = 1
	# Отношение между размерами старого и нового изображения превосходят единицу, поэтому при
	# его смасштабировать возникает ScaleError
        self.assertRaises(ScaleError, scale, smart_image.data, sic.mode, sic.format, sc.width, \
        	                             sc.height, sic.maxratio, sic.resample, sic.quality)

        # Возвращаем назад значение maxratio
	sic.maxratio = 100.0
	# Вызываем функцию масштабирования. Поскольку размеры нового изображения не превосходят
	# размеры исходного - с изображением ничего произойти не должно
        result = scale(smart_image.data, sic.mode, sic.format, sc.width, sc.height, sic.maxratio, \
	                                 sic.resample, sic.quality)
	self.assertEqual(result, smart_image.data)

        # Теперь воспользуемся масштабом под индексом 1
        sc = sic.scales[1]
	# масштабируем изображение
	scaled_image = Image(scale(smart_image.data, sic.mode, sic.format, sc.width, sc.height, \
	                                             sic.maxratio , sic.resample, sic.quality))
	# Убеждаемся, что его ширина и высота изменились и соответствуют значениям масштаба с индексом 1
	self.assertEqual(scaled_image._height, sc.height)
	self.assertEqual(scaled_image._width, sc.width)

        # В этом месте хорошо бы проверить как перекодируются форматы, например из GIF в JPEG, но при
	# попытке этого выдаётся IOError: encoder jpeg not available, хотя PIL вроде стоит...
	# Надо будет покопаться
        #sic.format = u'JPEG'
        #sc = sic.scales[0]
	#scaled_image = Image(scale(smart_image.data, sic.mode, sic.format, sc.width, sc.height, sic.maxratio , sic.resample, sic.quality))


class testSmartImageView(ReferenceSetupMixin, unittest.TestCase):

    def test_url(self):

        simg = self.root[u'folder1'][u'simg']
        # Создаём тестовый request. Значение его параметра SERVER_URL равно http://127.0.0.1
        request = TestRequest()
        
        smart_image_view = SmartImageView(simg, request)
        
        # Наше изображение с именем simg лежит в папке folder1, которая лежит в корне. Знчит её url
	# должен быть вот таким: http://127.0.0.1/folder1/simg/@@. Проверяем.
	self.assertEqual(smart_image_view.url, u'http://127.0.0.1/folder1/simg/@@')
        
        # Устанавливаем свойство name в значение u'somename'. Теперь url объекта должно соответствующим
	# образом измениться (после @@ добавится someview). Проверяем
        smart_image_view.name = u'someview'
        self.assertEqual(smart_image_view.name, u'someview')
	self.assertEqual(smart_image_view.url, u'http://127.0.0.1/folder1/simg/@@someview')

    def test_call(self):

        smart_image = self.root[u'folder1'][u'simg']
        # Создаём тестовый request. Значение его параметра SERVER_URL равно http://127.0.0.1
        request = TestRequest()

        # Прописываем адаптер для преобразования ISmartImage к ISmartImageAdapter
        ztapi.provideAdapter(ISmartImage, ISmartImageAdapter, SmartImageAdapter)
	self.intids_utility.register(smart_image)

        # Проходим по всем необходимым масштабам, которых у нас 2
        for cs in self.sic_utility.scales:
	    # Приводим наше изображение к классу SmartImage
	    simg = SmartImageAdapter(smart_image)
	    # Сохраняем изображение в кэш
	    simg.savetoCache(cs.name)
	
        smart_image_view = SmartImageView(smart_image, request)

        # Проверяем, что никакие header'ы не установлены
	self.assertEqual(smart_image_view.request.response.getHeader(u'Content-Type'), None)
	self.assertEqual(smart_image_view.request.response.getHeader(u'Expires'), None)
	self.assertEqual(smart_image_view.request.response.getHeader(u'Last-Modified'), None)

        # Устанавливая различные значения свойства name мы можем получать изображение из кэша в том
	# или ином виде
	
	# Устанавливаем свойство name равным имени первого масштаба
	smart_image_view.name = self.sic_utility.scales[0].name
	img = Image()
	img._setData(smart_image_view())
	# Проверяем, что мы получили несмасштабированное изображение (оно не превосходит 100 х 100)
	self.assertEqual(img._height, 16)
	self.assertEqual(img._width, 16)

	smart_image_view.name = self.sic_utility.scales[1].name
	img = Image()
	img._setData(smart_image_view())
        # Проверяем, что мы получили смасштабированное изображение (его размеры уменьшены до 10 х 10)
	self.assertEqual(img._height, 10)
	self.assertEqual(img._width, 10)

        # Проверяем, что необходимые header'ы перестали быть None и стали чему-то равны
	self.assertEqual(smart_image_view.request.response.getHeader(u'Content-Type'), 'image/gif')
	self.assertEqual((smart_image_view.request.response.getHeader(u'Expires') != None), True)
	self.assertEqual((smart_image_view.request.response.getHeader(u'Last-Modified') != None), True)

	empty_smart_image = self.root[u'folder1'][u'empty_simg']
        self.intids_utility.register(empty_smart_image)

        smart_image_view = SmartImageView(empty_smart_image, request)
	smart_image_view.name = self.sic_utility.scales[0].name
	# При попытке посмотреть изображение, которого нет в кэше, возыращается ''
	self.assertEqual(smart_image_view(), '')

        # Вообще говоря, здесь бы ещё проверить возникновение ComponentLookupError, однако по моим
	# наблюдениям сделать это не получится, потому что этот ексепшен никогда не возникнет. Дело
	# в том, что перед try cache = getUtility(ISmartImageProp) except выполняется строчка
	# im = ISmartImageAdapter(self.context).getfromCache(self.name)
	# А в методе getfromCache есть строчка 
	# cache = getUtility(ISmartImageProp) и если уж она сработала, то она и тут сработает
	# Короче, что-то тут, как я полагаю, надо переделать. Ну а уж делать это или нет - решайте


class testSmartImageAdapter(ReferenceSetupMixin, unittest.TestCase):

    def test_saveToCache(self):
        
        smart_image = self.root[u'folder1'][u'simg']
	empty_smart_image = self.root[u'folder1'][u'empty_simg']
        test_folder = self.root[u'folder1']
        
        # Убедимся, что в кэше ничего нет
        self.assertEquals(len(self.sic_utility), 0)

        #id = self.intids_utility.register(smart_image)
        #id = self.intids_utility.register(smart_image)

        self.intids_utility.register(smart_image)
        self.intids_utility.register(empty_smart_image)

        
        # Проходим по всем необходимым масштабам, которых у нас 2
        for cs in self.sic_utility.scales:
	    # Приводим наше изображение к классу SmartImage
	    simg = SmartImageAdapter(smart_image)
	    # Сохраняем изображение в кэш
	    simg.savetoCache(cs.name)

        # При добавлении в кэш изображения с неправильным именем масштаба возникает KeyError
	# и добавления не происходит
        self.assertRaises(KeyError, simg.savetoCache, u'some_scale')

        # Одно изображение добавлено в кэш в двух различных масштабах, значит в кэше должно
	# быть 2 изображения
        self.assertEquals(len(self.sic_utility), 2)

	# Получаем из кэша изображение, подгнанное под масштаб с индексом 0. Поскольку масштаб требует
	# размеров не более чем 100 х 100, а исходное изображение было размерами 16 х 16, оно не должно
	# было смасштабироваться
	scaled_img0 = simg.getfromCache(self.sic_utility.scales[0].name)
	self.assertEquals(scaled_img0._width, 16)
	self.assertEquals(scaled_img0._height, 16)

	# Получаем из кэша изображение, подгнанное под масштаб с индексом 1. Максимальные размеры его
	# элементов 10 х 10, поэтому и исходное изображение должно было уменьшиться под эти величины
	scaled_img1 = simg.getfromCache(self.sic_utility.scales[1].name)
	self.assertEquals(scaled_img1._width, 10)
	self.assertEquals(scaled_img1._height, 10)

        # Попробуем добавить изображение в кэш повторно. В результате старое должно удалиться и
	# замениться новым аналогичным старому
	simg.savetoCache(self.sic_utility.scales[1].name)
	simg.savetoCache(self.sic_utility.scales[1].name)
	
	# Проверяем, что число изображений в кэше не изменилось
        self.assertEquals(len(self.sic_utility), 2)

        # Пытаемся добавить в кэш пустое изображение (будет отсутствовать self.context.data)
	simg = SmartImageAdapter(empty_smart_image)
	# При попытке добавить его в кэш возвращается None и добавления не происходит
	self.assertEqual(simg.savetoCache(self.sic_utility.scales[1].name), None)

	# Проверяем, что число изображений в кэше не изменилось
        self.assertEquals(len(self.sic_utility), 2)


    def test_getFromCache(self):
        
        smart_image = self.root[u'folder1'][u'simg']
        test_folder = self.root[u'folder1']
        
        self.assertEquals(len(self.sic_utility), 0)
        id = self.intids_utility.register(smart_image)
        
        for cs in self.sic_utility.scales:
	    simg = SmartImageAdapter(smart_image)
	    # При попытке взять из кэша изображение, которого там ещё нет, происходит его добавление
	    # в кэш
	    simg.getfromCache(cs.name)

        # Убеждаемся в том, что число изображений в кэше стало равно 2
        self.assertEquals(len(self.sic_utility), 2)

        # Получаем каждое из отмасштабированных изображений и убеждаемся, что в одном случае оно не
	# изменилось, а в другом изменилось под требования масштаба
	scaled_img0 = simg.getfromCache(self.sic_utility.scales[0].name)
	self.assertEquals(scaled_img0._width, 16)
	self.assertEquals(scaled_img0._height, 16)
	scaled_img1 = simg.getfromCache(self.sic_utility.scales[1].name)
	self.assertEquals(scaled_img1._width, 10)
	self.assertEquals(scaled_img1._height, 10)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(testSmartImageView),
        unittest.makeSuite(testSmartImageAdapter),
        unittest.makeSuite(testScaleError),
        unittest.makeSuite(test_scale),
        ))

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
