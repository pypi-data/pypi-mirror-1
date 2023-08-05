#!/usr/bin/env python

from distutils.core import setup

setup(name='Orchid',
      version='1.0',
      description='Generic Multi Threaded Web Crawler',
      author='Eugene Vahlis',
      author_email='evahlis@cs.toronto.edu',
      url='http://www.cs.toronto.edu/~evahlis',
      modules=['orchid', 'malcontent'],
     )
