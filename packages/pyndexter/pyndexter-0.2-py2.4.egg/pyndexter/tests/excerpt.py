import unittest
from pyndexter import *
from pyndexter.tests.corpus import documents, corpus

class ExcerptTestCase(unittest.TestCase):
    def test_excerpt(self):
        terms = Query('lorem ipsum').terms()
        excerpt = Excerpt(documents['mock://3'], terms)
        self.assertEquals(unicode(excerpt), u"""...  Etiam pharetra. Vivamus """ 
            """diam ipsum, luctus et, luctus nec, auctor vel,\ntellus. """
            """Vestibulum lobortis feugiat dolor. Phasellus diam felis, """
            """commodo vitae,\nlaoreet ac, euismod sit amet, nunc. """
            """Vestibulum ut metus. Praesent vel nibh ac\nlibero """
            """convallis imperdiet. Morbi dignis ...""")

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ExcerptTestCase, 'test'))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
