#!/usr/bin/env python

from distutils.core import setup

setup(name='sr',
      version='0.1.0',
      description='Console utility for search and replace in files',
      author='Grigoriy Petukhov',
      author_email='lorien@lorien.name',
      url='http://bitbucket.org/lorien/sr/',
      scripts=['sr'],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
      )
