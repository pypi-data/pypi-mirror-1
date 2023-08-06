### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################

import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.interface.verify import verifyClass
from zope.app.file.interfaces import IImage
from zope.app.file.image import Image, FileFactory, ImageSized
from zope.app.file.file import File, FileWriteFile, FileReadFile

import ks
from ks.smartimage.smartimage import SmartImage
from ks.smartimage.interfaces import ISmartImage

class TestSmartImage(unittest.TestCase):

    def _makeSmartImage(self, *args, **kw):
        return SmartImage(*args, **kw)

    def test_Title(self, *args, **kw):
        img = self._makeSmartImage(*args, **kw)
	self.assertEqual(img.title, u'')
	img.title = u'some title'
	self.assertEqual(img.title, u'some title')

    def test_Empty(self):
        file = self._makeSmartImage()
        self.assertEqual(file.contentType, '')
        self.assertEqual(file.data, '')

    def test_Constructor(self):
        file = self._makeSmartImage('Data')
        self.assertEqual(file.contentType, '')
        self.assertEqual(file.data, 'Data')

    def test_Mutators(self):
        image = self._makeSmartImage()

        image.contentType = 'image/jpeg'
        self.assertEqual(image.contentType, 'image/jpeg')

        image._setData('hello')
        self.assertEqual(image.data, 'hello')

    def test_Interface(self):
        self.failUnless(ISmartImage.implementedBy(SmartImage))
        self.failUnless(verifyClass(ISmartImage, SmartImage))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestSmartImage),
        ))

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
