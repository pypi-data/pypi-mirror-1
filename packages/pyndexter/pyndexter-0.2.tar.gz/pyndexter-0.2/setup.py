try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Extract version and author from authoritative source in the module
import sys
sys.path.insert(0, '.')
from pyndexter import __version__, __author__

setup(name='pyndexter',
      description="An abstraction layer for full-text indexing engines.",
      long_description=' '.join(open('README').read().split('\n\n')[0].split('\n')),
      url='http://swapoff.org/pyndexter',
      download_url='http://swapoff.org/pyndexter',
      license='BSD',
      platforms=['any'],
      author='Alec Thomas',
      author_email=__author__.split('<')[1][:-1],
      version=__version__,
      test_suite='pyndexter.test.suite',
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Plugins',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Topic :: Software Development :: Libraries'],
      packages=['pyndexter', 'pyndexter.indexers', 'pyndexter.sources',
                'pyndexter.stemmers', 'pyndexter.tests'])
