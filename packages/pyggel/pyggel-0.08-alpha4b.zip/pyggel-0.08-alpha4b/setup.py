#!/usr/bin/env python
from distutils.core import setup
import sys
sys.argv.append("sdist")
import pyggel
setup(name='pyggel',
      version=pyggel.get_version(),
      description='PYthon Graphical Game Engine and Libraries',
      author='Matt Roe',
      author_email='RoeBros@gmail.com',
      maintainer='Matt Roe',
      maintainer_email='roebros@gmail.com',
      url='http://pyggel.googlecode.com/',
      packages = ['pyggel'],
      #TODO: the demos and 3d files
      #data_files=[('data', ['data/*.png']),
      #            ('data', ['data/*.obj']),
      #            ('data', ['data/*.mtl']),]
      )
