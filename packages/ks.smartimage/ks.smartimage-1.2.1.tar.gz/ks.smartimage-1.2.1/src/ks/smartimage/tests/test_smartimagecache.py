### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################

import unittest
from PIL import Image
from ks.smartimage.smartimagecache.smartimagecache import Scale, SmartImageCache
from ks.smartimage.smartimagecache.interfaces import IScale
from zope.interface.verify import verifyClass
from ks.smartimage.smartimagecache.interfaces import IScale, ISmartImageProp, ISmartImageCacheContainer, IStat


class TestScale(unittest.TestCase):

    def _makeScale(self, *args, **kw):
        return Scale(*args, **kw)

    def test_Constructor(self, *args, **kw):
        scale = self._makeScale(*args, **kw)
	self.assertEqual(scale.name, u'')
	self.assertEqual(scale.width, 100)
	self.assertEqual(scale.height, 100)
	del scale

	scale = self._makeScale(u'Some scale', 200, 200, *args, **kw)
	self.assertEqual(scale.name, u'Some scale')
	self.assertEqual(scale.width, 200)
	self.assertEqual(scale.height, 200)

    def test_Mutators(self, *args, **kw):
        scale = self._makeScale(*args, **kw)
	scale.name = u'Some scale'
	self.assertEqual(scale.name, u'Some scale')
	scale.width = 200
	self.assertEqual(scale.width, 200)
	scale.height = 200
	self.assertEqual(scale.height, 200)


class testSmartImageCache(unittest.TestCase):

    def _makeSmartImageCache(self, *args, **kw):
        return SmartImageCache(*args, **kw)

    def test_Constructor(self, *args, **kw):
        sic = self._makeSmartImageCache(*args, **kw)

	self.assertEqual(sic.scale, ())
	self.assertEqual(sic.format, u'JPEG')
	self.assertEqual(sic.mode, u'RGB')
	self.assertEqual(sic.maxratio, 100.0)
	self.assertEqual(sic.interval, 900)
	self.assertEqual(sic.iscached, True)
	self.assertEqual(sic.elementsamount, 0)
	self.assertEqual(sic.elementssize, 0.0)
	self.assertEqual(sic.meansize, 0.0)
	self.assertEqual(sic.resample, Image.ANTIALIAS)
	self.assertEqual(sic.quality, 90)

    def test_Mutators(self, *args, **kw):
        sic = self._makeSmartImageCache(*args, **kw)
	sic.scale = (1, 2, 3)
	self.assertEqual(sic.scale, (1, 2 ,3))
	sic.format = u'GIF'
	self.assertEqual(sic.format, u'GIF')
	sic.mode = u'CMYK'
	self.assertEqual(sic.mode, u'CMYK')
	sic.maxratio = 200.0
	self.assertEqual(sic.maxratio, 200.0)
	sic.interval = 1800
	self.assertEqual(sic.interval, 1800)
	sic.iscached = False
	self.assertEqual(sic.iscached, False)
	sic.elementsamount = 5
	self.assertEqual(sic.elementsamount, 5)
	sic.elementssize = 2.0
	self.assertEqual(sic.elementssize, 2.0)
	sic.meansize = 2.0
	self.assertEqual(sic.meansize, 2.0)
	sic.resample = Image.BICUBIC
	self.assertEqual(sic.resample, Image.BICUBIC)
	sic.quality = 70
	self.assertEqual(sic.quality, 70)

    def test_Interface(self):
        self.failUnless(ISmartImageProp.implementedBy(Scale))
        self.failUnless(ISmartImageCacheContainer.implementedBy(Scale))
        self.failUnless(IStat.implementedBy(Scale))

        self.failUnless(verifyClass(ISmartImageProp, Scale))
        self.failUnless(verifyClass(ISmartImageCacheContainer, Scale))
        self.failUnless(verifyClass(IStat, Scale))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestScale),
        ))

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
