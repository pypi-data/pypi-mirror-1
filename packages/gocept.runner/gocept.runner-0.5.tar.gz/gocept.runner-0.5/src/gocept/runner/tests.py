# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import gocept.runner
import os.path
import unittest
import zope.app.appsetup.product
import zope.app.testing.functional


runner_layer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'RunnerLayer', allow_teardown=True)


class TestFromConfig(unittest.TestCase):

    def setUp(self):
        self.old_config = zope.app.appsetup.product.saveConfiguration()
        zope.app.appsetup.product.setProductConfiguration('test', dict(
            foo='bar'))

    def tearDown(self):
        zope.app.appsetup.product.restoreConfiguration(self.old_config)

    def test_invalid_section(self):
        self.assertRaises(KeyError,
                          gocept.runner.from_config('invalid', 'foo'))

    def test_invalid_value(self):
        self.assertRaises(KeyError,
                          gocept.runner.from_config('test', 'invalid'))

    def test_valid(self):
        self.assertEqual('bar',
                         gocept.runner.from_config('test', 'foo')())

    def test_returns_callable(self):
        self.assertTrue(callable(gocept.runner.from_config('baz', 'boink')))


flags = doctest.INTERPRET_FOOTNOTES | doctest.ELLIPSIS


def test_suite():
    suite = unittest.TestSuite()
    test = zope.app.testing.functional.FunctionalDocFileSuite(
        'README.txt',
        optionflags=flags)
    test.layer = runner_layer
    suite.addTest(test)

    suite.addTest(doctest.DocFileSuite(
        'appmain.txt',
        'once.txt',
        optionflags=flags))
    suite.addTest(unittest.makeSuite(TestFromConfig))

    return suite
