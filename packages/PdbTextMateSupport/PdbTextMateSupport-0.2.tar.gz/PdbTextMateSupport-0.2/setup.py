#!/usr/bin/env python

from distutils.core import setup

setup(name='PdbTextMateSupport',
      version='0.2',
      description='Display source code in TextMate while debugging with pdb',
      author='Andreas Zeidler',
      author_email='az@zitc.de',
      url='https://svn.zitc.de/trac/pdbtextmatesupport',
      py_modules=['PdbTextMateSupport'],
      scripts=['pdbtmsupport']
)
