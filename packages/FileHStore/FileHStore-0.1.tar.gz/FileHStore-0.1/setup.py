#!/usr/bin/env python

# $Id: setup.py 53 2007-04-15 20:57:47Z adulau $

from distutils.core import setup

setup(name='FileHStore',
      version='0.1',
      description='Extension to store files on a filesystem using a very simple hash-based storage',
      author='Alexandre Dulaunoy',
      author_email='a@foo.be',
      url='http://www.foo.be/hstore/',
      packages=['FileHStore'],
      long_description = 'Extension to store files on a filesystem using a very simple hash-based storage',
      classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: Console',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License (GPL)',
      'Operating System :: POSIX',
      'Programming Language :: Python',
      'Topic :: Software Development :: Libraries'
      ] 
     )
