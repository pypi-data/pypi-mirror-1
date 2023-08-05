# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Alec Thomas <alec@swapoff.org>
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

"""
Snowball
--------

`Snowball <http://snowball.tartarus.org/>`_ is a multi-language stemming
library with `Python bindings <http://snowball.tartarus.org/wrappers/PyStemmer-1.0.1.tar.gz>`_.

Usage
~~~~~

::

    snowball://<language>

``<language>``
    Any of the languages supported by Snowball.


Installation
~~~~~~~~~~~~

The Python bindings ship with the Snowball source, so it's an easy (and
recommended) install.

::

    easy_install http://snowball.tartarus.org/wrappers/PyStemmer-1.0.1.tar.gz

"""

import Stemmer
from pyndexter import PluginFactory

class SnowballStemmer(object):
    def __init__(self, language):
        self.stemmer = Stemmer.Stemmer(language)

    def __call__(self, word):
        return self.stemmer.stemWord(word)

stemmer_factory = PluginFactory(SnowballStemmer, host="language")
