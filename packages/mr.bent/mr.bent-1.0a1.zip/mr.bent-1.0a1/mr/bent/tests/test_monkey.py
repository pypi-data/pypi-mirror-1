from unittest import TestCase, defaultTestLoader

from mr.bent.tests import mock
from mr.bent.tests.mock import page
from mr.bent.monkey import wrap, unwrap


def handler(function, *args, **kwargs):
    return -42


def discordia(function, *args, **kwargs):
    return 23


class MonkeyTests(TestCase):

    def testUnwrapFunction(self):
        self.assertEqual(mock.foo.__module__, 'mr.bent.tests.mock')
        wrap(mock.foo, handler)
        self.assertEqual(mock.foo.__module__, 'mr.bent.monkey')
        unwrap(mock.foo)
        self.assertEqual(mock.foo.__module__, 'mr.bent.tests.mock')

    def testUnwrapMethod(self):
        self.assertEqual(page.render.__module__, 'mr.bent.tests.mock')
        wrap(page.render, handler)
        self.assertEqual(page.render.__module__, 'mr.bent.monkey')
        unwrap(page.render)
        self.assertEqual(page.render.__module__, 'mr.bent.tests.mock')

    def testDoubleWrap(self):
        self.assertEqual(mock.foo.__module__, 'mr.bent.tests.mock')
        self.assertEqual(mock.foo(), 42)
        # wrap once...
        wrap(mock.foo, handler)
        self.assertEqual(mock.foo.__module__, 'mr.bent.monkey')
        self.assertEqual(mock.foo(), -42)
        # wrap twice...
        wrap(mock.foo, discordia)
        self.assertEqual(mock.foo.__module__, 'mr.bent.monkey')
        self.assertEqual(mock.foo(), 23)
        # unwrap...
        unwrap(mock.foo)
        self.assertEqual(mock.foo.__module__, 'mr.bent.monkey')
        self.assertEqual(mock.foo(), -42)
        # unwrap again...
        unwrap(mock.foo)
        self.assertEqual(mock.foo.__module__, 'mr.bent.tests.mock')
        self.assertEqual(mock.foo(), 42)


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

