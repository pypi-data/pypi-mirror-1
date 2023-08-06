from unittest import TestCase, defaultTestLoader

from mr.bent.tests import mock
from mr.bent.tests.mock import page, viewletmanager, viewlet
from mr.bent.tests.utils import mkcallback
from mr.bent.wrapper import fqfn, mkwrapper, mkcontext, mkfilter
from mr.bent.plugins import callcounter
from mr.bent.monkey import unwrap


sample = page((
    viewletmanager((viewlet('foo'), viewlet('bar'))),
    viewletmanager((viewlet('gay'), viewlet('bar')))
))


class FQFNTests(TestCase):

    def testFQFName(self):
        self.assertEqual(fqfn(mock.foo), 'mr.bent.tests.mock.foo')
        self.assertEqual(fqfn(page.render), 'mr.bent.tests.mock.page.render')


class WrapperTests(TestCase):

    def tearDown(self):
        unwrap(mock.foo)
        unwrap(mock.reindex)
        unwrap(mock.summary)
        unwrap(page.render)
        unwrap(viewletmanager.render)
        unwrap(viewletmanager.render)

    def testMkWrapper(self):
        self.assertEqual(mock.foo.__module__, 'mr.bent.tests.mock')
        mkwrapper(mock.foo, callcounter, 'foo')
        self.assertEqual(mock.foo.__module__, 'mr.bent.monkey')
        self.assertEqual(mock.foo(), 42)
        unwrap(mock.foo)
        self.assertEqual(mock.foo.__module__, 'mr.bent.tests.mock')

    def testMkContext(self):
        self.assertEqual(page.render.__module__, 'mr.bent.tests.mock')
        stats, callback = mkcallback()
        mkcontext(page.render, callback)
        self.assertEqual(page.render.__module__, 'mr.bent.monkey')
        self.assertEqual(sample.render(), 'foo bar gay bar ')
        self.assertEqual(stats, [{}])   # 1 (empty) callback was expected
        unwrap(page.render)
        self.assertEqual(page.render.__module__, 'mr.bent.tests.mock')

    def testMkFilter(self):
        self.assertEqual(mock.reindex.__module__, 'mr.bent.tests.mock')
        mkfilter(mock.reindex)
        self.assertEqual(mock.reindex.__module__, 'mr.bent.monkey')
        self.assertEqual(mock.reindex(), 42)
        unwrap(mock.reindex)
        self.assertEqual(mock.reindex.__module__, 'mr.bent.tests.mock')

    def testMkWrapperWithContext(self):
        stats, callback = mkcallback()
        mkcontext(page.render, callback)
        mkwrapper(mock.foo, callcounter, 'foo')
        self.assertEqual(sample.render(), 'foo bar gay bar ')
        self.assertEqual(stats, [{
            (None, 'mr.bent.tests.mock.foo', 'foo'): 7,
        }])
        unwrap(mock.foo)
        unwrap(page.render)

    def testMkWrapperWithContextAndFilter(self):
        stats, callback = mkcallback()
        mkcontext(page.render, callback)
        mkwrapper(mock.foo, callcounter, 'foo')
        mkfilter(mock.reindex)
        self.assertEqual(sample.render(), 'foo bar gay bar ')
        self.assertEqual(stats, [{
            (None, 'mr.bent.tests.mock.foo', 'foo'): 7,
            ('mr.bent.tests.mock.reindex', 'mr.bent.tests.mock.foo', 'foo'): 2,
        }])
        unwrap(mock.reindex)
        unwrap(mock.foo)
        unwrap(page.render)

    def testMkWrapperWithContextAndMultipleFilters(self):
        stats, callback = mkcallback()
        mkcontext(page.render, callback)
        mkwrapper(mock.foo, callcounter, 'foo')
        mkfilter(mock.reindex)
        mkfilter(mock.summary)
        self.assertEqual(sample.render(), 'foo bar gay bar ')
        self.assertEqual(stats, [{
            (None, 'mr.bent.tests.mock.foo', 'foo'): 7,
            ('mr.bent.tests.mock.reindex', 'mr.bent.tests.mock.foo', 'foo'): 2,
            ('mr.bent.tests.mock.summary', 'mr.bent.tests.mock.foo', 'foo'): 4,
        }])
        unwrap(mock.summary)
        unwrap(mock.reindex)
        unwrap(mock.foo)
        unwrap(page.render)

    def testFilteredContext(self):
        stats, callback = mkcallback()
        mkcontext(page.render, callback)
        mkcontext(viewletmanager.render, callback)
        mkwrapper(mock.foo, callcounter, 'foo')
        mkfilter(viewletmanager.render)
        self.assertEqual(sample.render(), 'foo bar gay bar ')
        self.assertEqual(len(stats), 3)     # 3 callbacks were expected
        vm1, vm2, pg = stats
        # stats for the viewletmanagers should be the same...
        for vm in vm1, vm2:
            self.assertEqual(vm.name, 'mr.bent.tests.mock.viewletmanager.render')
            self.assertEqual(vm[(None, 'mr.bent.tests.mock.foo', 'foo')], 3)
            self.assertEqual(vm[('mr.bent.tests.mock.viewletmanager.render', 'mr.bent.tests.mock.foo', 'foo')], 3)
        # page stats also include partial stats for the manager
        self.assertEqual(pg.name, 'mr.bent.tests.mock.page.render')
        self.assertEqual(pg[(None, 'mr.bent.tests.mock.foo', 'foo')], 7)
        self.assertEqual(pg[('mr.bent.tests.mock.viewletmanager.render', 'mr.bent.tests.mock.foo', 'foo')], 6)
        unwrap(mock.foo)
        unwrap(viewletmanager.render)
        unwrap(viewletmanager.render)
        unwrap(page.render)


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

