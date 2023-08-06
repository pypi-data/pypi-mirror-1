### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""
$Id: test_smartimagehandler.py 35337 2008-05-28 09:01:39Z cray $
"""

import unittest
from PIL import Image

from zope.app.testing import ztapi, setup, placelesssetup

from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds

from zope.app.component.hooks import setSite

from ks.smartimage.smartimagecache.interfaces import ISmartImageProp
from ks.smartimage.smartimagecache.smartimagecache import Scale, SmartImageCache
from ks.smartimage.smartimageadapter.interfaces import ISmartImageAdapter
from ks.smartimage.smartimageadapter.smartimageadapter import SmartImageAdapter
from ks.smartimage.smartimagehandler.smartimagehandler import addToSmartImageCashe, deleteFromSmartImageCashe, imageModify, imageDelete
from ks.smartimage.smartimage import SmartImage
from ks.smartimage.interfaces import ISmartImage

from zope.app.container.interfaces import IObjectAddedEvent

from zope.app.folder.folder import Folder

from persistent.interfaces import IPersistent
from ZODB.interfaces import IConnection

from zope.app.keyreference.persistent import KeyReferenceToPersistent, connectionOfPersistent
from zope.app.keyreference.interfaces import IKeyReference

from zope.app.container.interfaces import IObjectAddedEvent, IObjectModifiedEvent
from zope.app.container.contained import ObjectAddedEvent, ObjectRemovedEvent
from zope.app.intid import addIntIdSubscriber, removeIntIdSubscriber
from zope.app.intid.interfaces import IIntIdAddedEvent, IIntIdRemovedEvent, IntIdRemovedEvent

# Содержимое файла с GIF-изображением
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

        # Создаём первоначальную структуру папок
        self.root[u'folder1'] = self.folder1 = Folder()
        #self.root[u'folder1'][u'simg'] = self.createSmartImage()
        # Создаём локальный менеджер сайта
        self.sm = setup.createSiteManager(self.folder1)
        # Создаём сайт
        setSite(self.folder1)

        # Формируем SmartImageCashe так, чтобы он хранил GIF изображения и содержал хотя бы один
        # Масштаб для преобразования изображений
        sic = SmartImageCache()
        sic.format = u'GIF'
        sic.scales = (Scale(), )

        self.root[u'folder1'][u'sic'] = sic
        # Создаём и регистрируем "генератор уникальных идентификаторов" с интерфейсом IIntIds
        self.intids_utility = setup.addUtility(self.sm, '', IIntIds, IntIds())
        # Создаём и регистрируем "SmartImageCache" с интерфейсом ISmartImageProp
        self.sic_utility = setup.addUtility(self.sm, '', ISmartImageProp, self.root[u'folder1'][u'sic'])

        self.root[u'folder1'][u'simg'] = self.createSmartImage()

    def tearDown(self):
        setup.placefulTearDown()


class testUsingImageCache(ReferenceSetupMixin, unittest.TestCase):


    def test_imageModify(self):

        # Создаём 'GIf' изображение SmartImage
        smart_image = self.root[u'folder1'][u'simg']
        # Получаем ссылку на папку, в которую будем добавлять изображение
        test_folder = self.root[u'folder1']

        # Создаём пустой список событий
        events = []
	# Заругистрировали обработчик события с итерфейсом IIntIdAddedEvent
        ztapi.subscribe([IIntIdAddedEvent], None, events.append)
	# Вызываем обработчик события ObjectAddedEvent для папки test_site при добавлении в неё
	# smart_image1, и только после этого счётчик событий увеличивается
        addIntIdSubscriber(smart_image, ObjectAddedEvent(test_folder))

	# Проверяем, что счётчик событий увеличился и стал равным 1
	self.assertEquals(len(events), 1)
	# Убеждаемся, что имеющееся события сработало для папки test_folder
        self.assertEquals(events[0].original_event.object, test_folder)
	# Убеждаемся, что событие возникло в результате добавления объекта smart_image1
        self.assertEquals(events[0].object, smart_image)

        # Проверяем, что добавления изображения в кэш не произошло
	self.assertEquals(len(self.sic_utility), 0)

	# Зарегистрировали обработчик события с итерфейсом IObjectModifiedEvent
        ztapi.subscribe([IObjectModifiedEvent], None, events.append)
	# Вызываем обработчик события ObjectAddedEvent для test_folder
	imageModify(smart_image, ObjectAddedEvent(test_folder))

	# Проверяем, что счётчик событий увеличился и стал равным 2
	self.assertEquals(len(events), 2)
	# Проверяем, что событие было сгенерировано для контейнера test_folder
        self.assertEquals(events[1].object, self.sic_utility)

        # Убеждаемся, что произошло добавление в кэш одного изображения
	self.assertEquals(len(self.sic_utility), 1)


    def test_imageDelete(self):

        smart_image = self.root[u'folder1'][u'simg']
        test_folder = self.root[u'folder1']

        # Проверяем, что в кэше нет никаких изображений
        self.assertEquals(len(self.sic_utility), 0)
	# Регистрируем smart_image в генераторе уникальных идентиикаторов и получаем идентификатор
	# зарегистрированного изображения
        id = self.intids_utility.register(smart_image)

        # Добавляем изображение в кэш (У нас есть только 1 масштаб и одно изображение, так что в
	# результате добавления в кэше должно появиться ровно одно изображение в заданном масштабе)
        for cs in self.sic_utility.scales:
	    simg = SmartImageAdapter(smart_image)
	    simg.savetoCache(cs.name)

	# Проверяем, что в кэше появилось ровно одно изображение
        self.assertEquals(len(self.sic_utility), 1)

        # С этим было бы хорошо, но оно почему-то никак не хочет работать
	#events = []
        #ztapi.subscribe([IIntIdRemovedEvent], None, events.append)

	# Регистрируем хендлер для события с интерфейсом IIntIdRemovedEvent (Удаление элемента
	# из генератора уникальных идентификаторов). При удалении чего-то из IntIds должно удаляться
	# Изображение с соответствующим идентификатором из кэша изображений
        ztapi.subscribe([IIntIdRemovedEvent], None, imageDelete)

	# Вызываем удаление изображения smart_image из папки test_folder и вместе с тем удаление
	# изображения из генератора уникальных идентификаторов
	removeIntIdSubscriber(smart_image, ObjectRemovedEvent(test_folder))

        # Проверяем, что произошло удаление объекта из IntIds (При попытке получить отсутствующий
	# объект возникает KeyError)
        self.assertRaises(KeyError, self.intids_utility.getObject, id)
	# Проверяем, что при удалении объекта из утилиты IntIds произошло её удаление и из кэша
        self.assertEquals(len(self.sic_utility), 0)


    def test_addToSmartImageCashe(self):

        smart_image = self.root[u'folder1'][u'simg']
        test_folder = self.root[u'folder1']

        # Проверяем, что в кэше нет никаких изображений
        self.assertEquals(len(self.sic_utility), 0)

        # Проверяем, что информация о кэше соответствует тому, что в нём ничего нет
        self.assertEquals(self.sic_utility.elementsamount, 0)
        self.assertEquals(self.sic_utility.elementssize, 0.0)
        self.assertEquals(self.sic_utility.meansize, 0.0)

        # Регистрируем добавляемое изображение в IntIds
	addIntIdSubscriber(smart_image, ObjectAddedEvent(test_folder))
	# Добавляем изображение в кеш
	imageModify(smart_image, ObjectAddedEvent(test_folder))

	# Проверяем, что изображение добавилось и число элементов кэша увеличилось до 1
        self.assertEquals(len(self.sic_utility), 1)

        # Регистрируем хэндлер
        ztapi.subscribe([IObjectAddedEvent], None, addToSmartImageCashe)

        # вызываваем обработчик
	addToSmartImageCashe(smart_image, ObjectAddedEvent(smart_image, newParent=self.sic_utility))

	# В результате добавления изображения происходит изменение общего числа изображения в кэше,
	# изменение суммарного объёма элементов кэша и изменение среднего размера элементов кэша
        self.assertEquals(self.sic_utility.elementsamount, 1)
        self.assertEquals(self.sic_utility.elementssize, 0.34000000000000002)
        self.assertEquals(self.sic_utility.meansize, 0.34000000000000002)


    def test_deleteFromSmartImageCashe(self):

        # Убеждаемся, что в кэше ничего нет
        self.assertEquals(len(self.sic_utility), 0)
	# Добавляем изображение в кэш
        self.test_addToSmartImageCashe()
	# Проверяем, что изображение добавлено
        self.assertEquals(len(self.sic_utility), 1)

        # Проверяем, что добавленное изображение нужным образом изменило параметры кэша
        self.assertEquals(self.sic_utility.elementsamount, 1)
        self.assertEquals(self.sic_utility.elementssize, 0.34000000000000002)
        self.assertEquals(self.sic_utility.meansize, 0.34000000000000002)

	# Получаем ссылки на добавленнное изображение, контейнер, в который оно добавлено и id
	# изображения в IntIds
        smart_image = self.root[u'folder1'][u'simg']
        test_folder = self.root[u'folder1']
        id = self.intids_utility.getId(smart_image)

        # Удаляем из кэша данные о добавленнм изображении
	deleteFromSmartImageCashe(smart_image, ObjectRemovedEvent(smart_image, oldParent=self.sic_utility))

	# Проверяем, что свойства кэша теперь говорят о его пустоте
        self.assertEquals(self.sic_utility.elementsamount, 0)
        self.assertEquals(self.sic_utility.elementssize, 0.0)
        self.assertEquals(self.sic_utility.meansize, 0.0)

        # Физически удаляем изображение из кэша и его регистрацию в IntIds
        ztapi.subscribe([IIntIdRemovedEvent], None, imageDelete)
	removeIntIdSubscriber(smart_image, ObjectRemovedEvent(test_folder))

        # Проверяем, что в кэше нет никаких изображений и что IntId не хранит информацию об удалённом
	# изображении
        self.assertEquals(len(self.sic_utility), 0)
        self.assertRaises(KeyError, self.intids_utility.getObject, id)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(testUsingImageCache),
        ))

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
