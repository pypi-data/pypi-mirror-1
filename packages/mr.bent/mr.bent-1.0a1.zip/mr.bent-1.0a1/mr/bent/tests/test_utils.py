from unittest import TestCase, defaultTestLoader

from mr.bent.utils import convert


class ConverterTests(TestCase):

    def testConvertLiteral(self):
        self.assertEqual(convert(
            {'foo': 23}),
            {'foo': 23})
        self.assertEqual(convert(
            {'foo': 23, 'bar': [42]}),
            {'foo': 23, 'bar': [42]})

    def testConvertTuple(self):
        self.assertEqual(convert(
            {('foo', 'bar'): 23}),
            {'foo': {'bar': 23}})
        self.assertEqual(convert(
            {('foo', 'bar'): 23, ('gay', 'bar'): [42]}),
            {'foo': {'bar': 23}, 'gay': {'bar': [42]}})
        self.assertEqual(convert(
            {('foo', 'bar'): 23, ('foo', 'gay'): [42]}),
            {'foo': {'bar': 23, 'gay': [42]}})

    def testConvertTriple(self):
        self.assertEqual(convert(
            {('foo', 'bar', 'foobar'): 23}),
            {'foo': {'bar': {'foobar': 23}}})
        self.assertEqual(convert(
            {('foo', 'bar', 'foobar'): 23, ('gay', 'bar', 'gaybar'): [42]}),
            {'foo': {'bar': {'foobar': 23}}, 'gay': {'bar': {'gaybar': [42]}}})
        self.assertEqual(convert(
            {('foo', 'bar', 'foobar'): 23, ('foo', 'bar', 'gaybar'): [42]}),
            {'foo': {'bar': {'foobar': 23, 'gaybar': [42]}}})
        self.assertEqual(convert(
            {('foo', 'bar', 'foobar'): 23,
             ('foo', 'bar', 'gaybar'): 42,
             ('foo', 'foo', 'foobar'): 28,
             ('foo', 'foo', 'gaybar'): 64}),
            {'foo': {'bar': {'foobar': 23, 'gaybar': 42},
                     'foo': {'foobar': 28, 'gaybar': 64}}})


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

