### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################

import unittest
from zope.app.testing.placelesssetup import PlacelessSetup
from zope.app.form.browser.tests import support
from ks.smartimage.smartimageschema.smartimagewidget import ObjectWidget
from zope.schema import Text
from zope.app.form.browser.widget import SimpleInputWidget
from zope.interface import Interface, implements
from zope.publisher.browser import TestRequest
from zope.app.form.interfaces import ConversionError
from zope.app.form.interfaces import WidgetInputError, MissingInputError


class BrowserWidgetTest(PlacelessSetup,
                        support.VerifyResults,
                        unittest.TestCase):

    _FieldFactory = Text
    _WidgetFactory = None

    def setUpContent(self, desc=u'', title=u'Foo Title'):
        class ITestContent(Interface):
            foo = self._FieldFactory(
            title=title,
            description=desc)
        class TestObject:
            implements(ITestContent)
        self.content = TestObject()

        field = ITestContent['foo']
        field = field.bind(self.content)

        request = TestRequest(HTTP_ACCEPT_LANGUAGE='ru')
        request.form['field.foo'] = u'Foo Value'

        self._widget = self._WidgetFactory(field, request)

    def setUp(self):
        super(BrowserWidgetTest, self).setUp()
        self.setUpContent()


class TestWidget(SimpleInputWidget):

    def _toFieldValue(self, v):
        if v == u'barf!':
            raise ConversionError('ralph')
        return v or None


class TestObjectWidget(BrowserWidgetTest):

    _WidgetFactory = TestWidget

    def test_getInputValue(self):
        self.assertEqual(self._widget.getInputValue(), u'Foo Value')

        self._widget.request.form['field.foo'] = (1, 2)
        self.assertRaises(WidgetInputError, self._widget.getInputValue)

        self._widget.request.form['field.foo'] = u'barf!'
        self.assertRaises(ConversionError, self._widget.getInputValue)

        del self._widget.request.form['field.foo']
        self._widget.context.required = True
        self.assertRaises(MissingInputError, self._widget.getInputValue)

        self._widget.context.required = False
        self._widget.request.form['field.foo'] = u''
        self.assertEqual(self._widget.getInputValue(), None)

    def test_applyChanges(self):
        self.assertEqual(self._widget.applyChanges(self.content), True)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestObjectWidget),
        ))

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
