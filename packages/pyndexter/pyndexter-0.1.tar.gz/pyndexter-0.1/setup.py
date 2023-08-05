from setuptools import setup, Extension

setup(name='pyndexter',
      description="A full-text indexing abstraction layer for Python",
      long_description="Pyndexter (pronounced 'poindexter') is an abstraction "
                       "layer for full-text indexing engines. In addition to "
                       "adapters for Hyperestraier and Xapian, Pyndexter "
                       "includes a native Python indexer.",
      url='http://swapoff.org/pyndexter',
      download_url='http://swapoff.org/pyndexter',
      license='BSD',
      platforms=['any'],
      author='Alec Thomas',
      author_email='alec@swapoff.org',
      version='0.1',
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Plugins',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Topic :: Software Development :: Libraries'],
      extras_require={'hype': ['hype>=0.1'],
                      'Xapwrap': ['Xapwrap>=0.3']},
      packages=['pyndexter'])
