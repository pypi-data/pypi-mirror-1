# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Alec Thomas <alec@swapoff.org>
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import unittest
from pyndexter import *
from pyndexter.sources.mock import MockSource
from pyndexter.indexers.mock import MockIndexer
from pyndexter.indexers.tests import IndexerTestCase


class FrameworkTestCase(IndexerTestCase):
    def setUp(self):
        self.framework = Framework('mock://')
        self.framework.add_source('mock://')

    def tearDown(self):
        pass

    def test_indexer_uri(self):
        self.assertTrue(isinstance(self.framework.indexer, MockIndexer))
        self.assertTrue(isinstance(self.framework.source.sources[0], MockSource))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FrameworkTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
