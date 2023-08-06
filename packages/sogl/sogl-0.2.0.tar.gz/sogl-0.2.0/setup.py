#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-

from setuptools import setup

__id__ = '$Id: setup.py 1881 2006-12-15 14:59:05Z obi $'
__revision__ = '$Revision: 1881 $'

VERSION = '0.2.0'

setup(name='sogl',
      version='%s'%VERSION,
      description='Simplified Object Graph Library',
      author='Klaus Zimmermann',
      author_email='klaus.zimmermann@fmf.uni-freiburg.de',
      url='http://www.fmf.uni-freiburg.de/service/Servicegruppen/sg_wissinfo/Software/Pyphant',
      packages=['sogl'],
      license='wxWindows',
      )
