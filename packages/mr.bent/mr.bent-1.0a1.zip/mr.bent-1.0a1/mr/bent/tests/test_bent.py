from unittest import TestCase, defaultTestLoader

from mr.bent.tests import mock
from mr.bent.tests.mock import page, viewletmanager, viewlet
from mr.bent.tests.utils import mkcallback, mkcallbackwithcontext
from mr.bent.wrapper import mkcontext, mkwrapper, mkfilter
from mr.bent.monkey import unwrap
from mr.bent.mavolio import context
from mr.bent.plugins import callvalues, callcounter
from mr.bent.utils import convert


def getfibs():
    result = []
    for n in 3,4,6:
        result.append('fibbonaci(%d) == %d' % (n, mock.fibbonaci(n)))
    return result


def request():
    return page((
        viewletmanager((viewlet('foo'), viewlet('bar'), viewlet('foobar'))),
        viewletmanager((viewlet('hah'), viewlet('heh'), viewlet('huh')))
    )).render()


class PluginTests:

    def setUp(self):
        self.handler = NotImplemented

    def tearDown(self):
        unwrap(mock.foo)
        unwrap(mock.bar)
        unwrap(page.render)
        unwrap(viewletmanager.render)
        unwrap(viewlet.render)

    def basicStats(self):
        stats, callback = mkcallback()
        mkcontext(page.render, callback)
        mkwrapper(mock.foo, self.handler, self.name)
        mkwrapper(mock.bar, self.handler, self.name)
        self.assertEqual(request(), 'foo bar foobar hah heh huh ')
        self.assertEqual(len(stats), 1)     # 1 callback was expected
        return stats

    def nestedStats(self):
        stats, callback = mkcallback()
        mkcontext(page.render, callback)
        mkcontext(viewletmanager.render, callback)
        mkwrapper(mock.foo, self.handler, self.name)
        mkwrapper(mock.bar, self.handler, self.name)
        self.assertEqual(request(), 'foo bar foobar hah heh huh ')
        self.assertEqual(len(stats), 3)     # 3 callbacks were expected
        return stats

    def setupContextsAndWatches(self):
        stats, callback = mkcallback()
        mkcontext(page.render, callback)
        mkcontext(viewletmanager.render, callback)
        mkcontext(viewlet.render, callback)
        mkwrapper(mock.foo, self.handler, self.name)
        mkwrapper(mock.bar, self.handler, self.name)
        return stats

    def doublyNestedStats(self):
        stats = self.setupContextsAndWatches()
        self.assertEqual(request(), 'foo bar foobar hah heh huh ')
        self.assertEqual(len(stats), 9)     # 9 callbacks were expected
        return stats


class CallValuesTests(PluginTests, TestCase):

    def setUp(self):
        self.handler = callvalues
        self.name = 'values'

    def testRequest(self):
        self.assertEqual(request(), 'foo bar foobar hah heh huh ')

    def testBasicStats(self):
        stats = self.basicStats()[0]
        self.assertEqual(stats.name, 'mr.bent.tests.mock.page.render')
        # foo() gets called 1x per viewlet, 1x per manager and 1x per page
        self.assertEqual(stats[(None, 'mr.bent.tests.mock.foo', 'values')], [42]*9)
        # bar() gets called 1x in each viewlet and 1x for each viewlet
        self.assertEqual(stats[(None, 'mr.bent.tests.mock.bar', 'values')], [42]*12)

    def testNestedStats(self):
        stats1, stats2, stats3 = self.nestedStats()
        # stats for the viewletmanagers should limit the scope...
        self.assertEqual(stats1.name, 'mr.bent.tests.mock.viewletmanager.render')
        self.assertEqual(stats1[(None, 'mr.bent.tests.mock.foo', 'values')], [42]*4)
        self.assertEqual(stats1[(None, 'mr.bent.tests.mock.bar', 'values')], [42]*6)
        self.assertEqual(stats2.name, 'mr.bent.tests.mock.viewletmanager.render')
        self.assertEqual(stats2[(None, 'mr.bent.tests.mock.foo', 'values')], [42]*4)
        self.assertEqual(stats2[(None, 'mr.bent.tests.mock.bar', 'values')], [42]*6)
        # stats for the whole page were "called back" last
        self.assertEqual(stats3.name, 'mr.bent.tests.mock.page.render')
        self.assertEqual(stats3[(None, 'mr.bent.tests.mock.foo', 'values')], [42]*9)
        self.assertEqual(stats3[(None, 'mr.bent.tests.mock.bar', 'values')], [42]*12)

    def testDoublyNestedStats(self):
        v1, v2, v3, vm1, v4, v5, v6, vm2, pg = self.doublyNestedStats()
        # stats for the viewlets should all be the same...
        for v in v1, v2, v3, v4, v5, v6:
            self.assertEqual(v.name, 'mr.bent.tests.mock.viewlet.render')
            self.assertEqual(v[(None, 'mr.bent.tests.mock.foo', 'values')], [42])
            self.assertEqual(v[(None, 'mr.bent.tests.mock.bar', 'values')], [42])
        # the same goes for for the viewletmanagers...
        for vm in vm1, vm2:
            self.assertEqual(vm.name, 'mr.bent.tests.mock.viewletmanager.render')
            self.assertEqual(vm[(None, 'mr.bent.tests.mock.foo', 'values')], [42]*4)
            self.assertEqual(vm[(None, 'mr.bent.tests.mock.bar', 'values')], [42]*6)
        # stats for the whole page were "called back" last
        self.assertEqual(pg.name, 'mr.bent.tests.mock.page.render')
        self.assertEqual(pg[(None, 'mr.bent.tests.mock.foo', 'values')], [42]*9)
        self.assertEqual(pg[(None, 'mr.bent.tests.mock.bar', 'values')], [42]*12)


class CallCounterTests(PluginTests, TestCase):

    def setUp(self):
        self.handler = callcounter
        self.name = 'count'

    def testRequest(self):
        self.assertEqual(request(), 'foo bar foobar hah heh huh ')

    def testBasicStats(self):
        stats = self.basicStats()[0]
        self.assertEqual(stats.name, 'mr.bent.tests.mock.page.render')
        # foo() gets called 1x per viewlet, 1x per manager and 1x per page
        self.assertEqual(stats[(None, 'mr.bent.tests.mock.foo', 'count')], 9)
        # bar() gets called 1x in each viewlet and 1x for each viewlet
        self.assertEqual(stats[(None, 'mr.bent.tests.mock.bar', 'count')], 12)

    def testNestedStats(self):
        stats1, stats2, stats3 = self.nestedStats()
        # stats for the viewletmanagers should limit the scope...
        self.assertEqual(stats1.name, 'mr.bent.tests.mock.viewletmanager.render')
        self.assertEqual(stats1[(None, 'mr.bent.tests.mock.foo', 'count')], 4)
        self.assertEqual(stats1[(None, 'mr.bent.tests.mock.bar', 'count')], 6)
        self.assertEqual(stats2.name, 'mr.bent.tests.mock.viewletmanager.render')
        self.assertEqual(stats2[(None, 'mr.bent.tests.mock.foo', 'count')], 4)
        self.assertEqual(stats2[(None, 'mr.bent.tests.mock.bar', 'count')], 6)
        # stats for the whole page were "called back" last
        self.assertEqual(stats3.name, 'mr.bent.tests.mock.page.render')
        self.assertEqual(stats3[(None, 'mr.bent.tests.mock.foo', 'count')], 9)
        self.assertEqual(stats3[(None, 'mr.bent.tests.mock.bar', 'count')], 12)

    def testDoublyNestedStats(self):
        v1, v2, v3, vm1, v4, v5, v6, vm2, pg = self.doublyNestedStats()
        # stats for the viewlets should all be the same...
        for v in v1, v2, v3, v4, v5, v6:
            self.assertEqual(v.name, 'mr.bent.tests.mock.viewlet.render')
            self.assertEqual(v[(None, 'mr.bent.tests.mock.foo', 'count')], 1)
            self.assertEqual(v[(None, 'mr.bent.tests.mock.bar', 'count')], 1)
        # the same goes for for the viewletmanagers...
        for vm in vm1, vm2:
            self.assertEqual(vm.name, 'mr.bent.tests.mock.viewletmanager.render')
            self.assertEqual(vm[(None, 'mr.bent.tests.mock.foo', 'count')], 4)
            self.assertEqual(vm[(None, 'mr.bent.tests.mock.bar', 'count')], 6)
        # stats for the whole page were "called back" last
        self.assertEqual(pg.name, 'mr.bent.tests.mock.page.render')
        self.assertEqual(pg[(None, 'mr.bent.tests.mock.foo', 'count')], 9)
        self.assertEqual(pg[(None, 'mr.bent.tests.mock.bar', 'count')], 12)


class MoreCounterTests(PluginTests, TestCase):

    def setUp(self):
        self.handler = callcounter
        self.name = 'xy'

    def tearDown(self):
        super(MoreCounterTests, self).tearDown()
        unwrap(mock.summary)
        unwrap(mock.reindex)
        unwrap(mock.fibbonaci)
        unwrap(getfibs)

    def testFilteredStats(self):
        stats = self.setupContextsAndWatches()
        # set up additional filters
        mkfilter(mock.summary)
        mkfilter(mock.reindex)
        self.assertEqual(request(), 'foo bar foobar hah heh huh ')
        self.assertEqual(len(stats), 9)     # 9 callbacks were expected
        v1, v2, v3, vm1, v4, v5, v6, vm2, pg = stats
        # stats for the viewlets should all be the same...
        for v in v1, v2, v3, v4, v5, v6:
            self.assertEqual(v.name, 'mr.bent.tests.mock.viewlet.render')
            self.assertEqual(v[(None, 'mr.bent.tests.mock.foo', 'xy')], 1)
            self.assertEqual(v[(None, 'mr.bent.tests.mock.bar', 'xy')], 1)
            self.assertEqual(v[('mr.bent.tests.mock.summary', 'mr.bent.tests.mock.foo', 'xy')], 1)
            self.assertEqual(v[('mr.bent.tests.mock.summary', 'mr.bent.tests.mock.bar', 'xy')], 1)
        # the same goes for for the viewletmanagers...
        for vm in vm1, vm2:
            self.assertEqual(vm.name, 'mr.bent.tests.mock.viewletmanager.render')
            self.assertEqual(vm[(None, 'mr.bent.tests.mock.foo', 'xy')], 4)
            self.assertEqual(vm[(None, 'mr.bent.tests.mock.bar', 'xy')], 6)
            self.assertEqual(vm[('mr.bent.tests.mock.reindex', 'mr.bent.tests.mock.foo', 'xy')], 1)
            self.assertEqual(vm[('mr.bent.tests.mock.summary', 'mr.bent.tests.mock.foo', 'xy')], 3)
            self.assertEqual(vm[('mr.bent.tests.mock.summary', 'mr.bent.tests.mock.bar', 'xy')], 3)
        # stats for the whole page were "called back" last
        self.assertEqual(pg.name, 'mr.bent.tests.mock.page.render')
        self.assertEqual(pg[(None, 'mr.bent.tests.mock.foo', 'xy')], 9)
        self.assertEqual(pg[(None, 'mr.bent.tests.mock.bar', 'xy')], 12)
        self.assertEqual(pg[('mr.bent.tests.mock.reindex', 'mr.bent.tests.mock.foo', 'xy')], 2)
        self.assertEqual(pg[('mr.bent.tests.mock.summary', 'mr.bent.tests.mock.foo', 'xy')], 6)
        self.assertEqual(pg[('mr.bent.tests.mock.summary', 'mr.bent.tests.mock.bar', 'xy')], 6)

    def testConvertFilteredStats(self):
        stats = self.setupContextsAndWatches()
        # set up additional filters
        mkfilter(mock.summary)
        mkfilter(mock.reindex)
        self.assertEqual(request(), 'foo bar foobar hah heh huh ')
        self.assertEqual(len(stats), 9)     # 9 callbacks were expected
        pg = convert(stats[-1])             # page stats are last...
        self.assertEqual(pg, {
            'name': 'mr.bent.tests.mock.page.render',
            None: {
                'mr.bent.tests.mock.foo': {'xy': 9},
                'mr.bent.tests.mock.bar': {'xy': 12}},
            'mr.bent.tests.mock.reindex': {
                'mr.bent.tests.mock.foo': {'xy': 2}},
            'mr.bent.tests.mock.summary': {
                'mr.bent.tests.mock.foo': {'xy': 6},
                'mr.bent.tests.mock.bar': {'xy': 6}}
        })

    def testCallbackContext(self):
        stats, callback = mkcallbackwithcontext()
        mkcontext(page.render, callback)
        mkwrapper(mock.foo, self.handler, self.name)
        self.assertEqual(request(), 'foo bar foobar hah heh huh ')
        self.assertEqual(len(stats), 1)     # 1 callback was expected
        obj, stats = stats[0]
        self.failUnless(isinstance(obj, page))
        self.assertEqual(stats.name, 'mr.bent.tests.mock.page.render')
        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[(None, 'mr.bent.tests.mock.foo', 'xy')], 9)

    def testAlterationDuringCallback(self):
        stats, callback = mkcallbackwithcontext('!!')
        mkcontext(page.render, callback)
        mkwrapper(mock.foo, self.handler, self.name)
        # output was altered by the callback...
        self.assertEqual(request(), 'foo bar foobar hah heh huh !!')
        self.assertEqual(len(stats), 1)     # 1 callback was expected
        obj, stats = stats[0]
        self.failUnless(isinstance(obj, page))
        self.assertEqual(stats.name, 'mr.bent.tests.mock.page.render')
        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[(None, 'mr.bent.tests.mock.foo', 'xy')], 9)

    def testNamedFilter(self):
        mkfilter(mock.summary, 'filter1')
        stats = self.basicStats()[0]
        self.assertEqual(stats.name, 'mr.bent.tests.mock.page.render')
        self.assertEqual(stats, {
            (None, 'mr.bent.tests.mock.bar', 'xy'): 12,
            (None, 'mr.bent.tests.mock.foo', 'xy'): 9,
            ('filter1', 'mr.bent.tests.mock.bar', 'xy'): 6,
            ('filter1', 'mr.bent.tests.mock.foo', 'xy'): 6,
        })

    def testRecursiveStats(self):
        stats, callback = mkcallback()
        mkcontext(getfibs, callback)
        mkwrapper(mock.fibbonaci, callcounter, 'foo')
        getfibs()
        self.assertEqual(len(stats), 1)     # 1 callback was expected
        self.assertEqual(stats[0][(None, 'mr.bent.tests.mock.fibbonaci', 'foo')], 39)


class ContextTests(TestCase):

    def testMerging(self):
        cntxt = context('info')

        stats = context('stats')
        stats[('foo', 'count')] = [1]
        cntxt.propagate(stats)
        self.assertEqual(len(cntxt), 1)
        self.assertEqual(cntxt[('foo', 'count')], [1])

        stats2 = context('stats2')
        stats2[('bar', 'count')] = [2]
        cntxt.propagate(stats2)
        self.assertEqual(len(cntxt), 2)
        self.assertEqual(cntxt[('foo', 'count')], [1])
        self.assertEqual(cntxt[('bar', 'count')], [2])

        wrap = context('wrap')
        wrap[('blubb', 'count')] = [3]
        wrap.propagate(cntxt)
        self.assertEqual(len(wrap), 3)
        self.assertEqual(wrap[('foo', 'count')], [1])
        self.assertEqual(wrap[('bar', 'count')], [2])
        self.assertEqual(wrap[('blubb', 'count')], [3])


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

