import unittest
import doctest


def suite():
    import pyndexter, pyndexter.util
    import pyndexter.tests.framework
    import pyndexter.tests.excerpt

    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(pyndexter))
    suite.addTest(doctest.DocTestSuite(pyndexter.util))
    suite.addTest(pyndexter.tests.framework.suite())
    suite.addTest(pyndexter.tests.excerpt.suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
