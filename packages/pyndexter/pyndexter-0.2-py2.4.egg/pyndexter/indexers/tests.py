import os
import unittest
import tempfile
from pyndexter import *
from pyndexter.tests.corpus import *


class IndexerTestCase(unittest.TestCase):
    def setUp(self):
        self.path = tempfile.mkdtemp()

        try:
            indexer = self.indexer % os.path.join(self.path, 'indexer.db')
        except AttributeError:
            indexer = '%s://%s' % (self.__class__.__name__[:-8].lower(), os.path.join(self.path, 'indexer.db'))

        self.framework = Framework(indexer)
        self.framework.add_source('mock://')

    def tearDown(self):
        self.framework.close()
        self.framework = None
        for path, names, filenames in os.walk(self.path, topdown=False):
            for file in filenames:
                os.unlink(os.path.join(path, file))
            os.rmdir(path)

    def test_indexing(self):
        filtered = []

        def filter(framework, context, stream):
            for transition, uri in stream:
                filtered.append((transition, uri))
                yield transition, uri

        self.framework.update(filter=filter)
        filtered.sort()
        self.assertEquals(filtered, [(1, uri) for uri in mock_uri_list])

        filtered = []
        documents[u'mock://12'].attributes['changed'] += 1
        self.framework.update(filter=filter)
        filtered.sort()
        self.assertEquals(filtered, [(2, URI(u'mock://12'))])

    def test_fetch_via_source(self):
        uri = u'mock://1'
        doc = self.framework.fetch(uri)
        self.assertEquals(doc.quality, 1.0)
        self.assertEquals(doc.content, documents[uri].content)
        self.assertRaises(DocumentNotFound, self.framework.fetch, u'file://foo') 

    def test_indexer_iteration(self):
        self.framework.update()
        self.assertEquals(mock_uri_list, sorted([uri for uri in self.framework.indexer]))

    def test_source_iteration(self):
        self.framework.update()
        self.assertEquals(mock_uri_list, sorted([uri for uri in self.framework.source])) 

    # Search tests
    def test_search_string_simple(self):
        self.framework.update()
        self.assertEquals(simple_hits, sorted([hit.uri for hit in self.framework.search(simple_query)]))

    def test_search_Query_simple(self):
        self.framework.update()
        query = Query(simple_query)
        self.assertEquals(simple_hits, sorted([hit.uri for hit in self.framework.search(query)]))

    def test_search_string_and(self):
        self.framework.update()
        self.assertEquals(and_hits, sorted([hit.uri for hit in self.framework.search(and_query)]))

    def test_search_string_not(self):
        self.framework.update()
        self.assertEquals(not_hits, sorted([hit.uri for hit in self.framework.search(not_query)]))


class BuiltinTestCase(IndexerTestCase):
    pass


class BuiltinCachingTestCase(IndexerTestCase):
    indexer = 'builtin://%s?cache=true'


class BuiltinCompactTestCase(IndexerTestCase):
    indexer = 'builtin://%s?compact=true'


class BuiltinCompactCachingTestCase(IndexerTestCase):
    indexer = 'builtin://%s?cache=true&compact=true'


class XapianTestCase(IndexerTestCase):
    pass


class HypeTestCase(IndexerTestCase):
    pass


class HyperestraierTestCase(IndexerTestCase):
    pass


class PyndexTestCase(IndexerTestCase):
    pass


class LuceneTestCase(IndexerTestCase):
    pass


class LupyTestCase(IndexerTestCase):
    pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BuiltinTestCase))
    suite.addTest(unittest.makeSuite(BuiltinCachingTestCase))
    suite.addTest(unittest.makeSuite(BuiltinCompactTestCase))
    suite.addTest(unittest.makeSuite(BuiltinCompactCachingTestCase))
    suite.addTest(unittest.makeSuite(XapianTestCase))
    suite.addTest(unittest.makeSuite(HypeTestCase))
    suite.addTest(unittest.makeSuite(HyperestraierTestCase))
    suite.addTest(unittest.makeSuite(PyndexTestCase))
    suite.addTest(unittest.makeSuite(LuceneTestCase))
    suite.addTest(unittest.makeSuite(LupyTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
