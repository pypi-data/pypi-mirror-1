#!/usr/bin/env python

from distutils.core import setup

setup(name='surely',
      license='Public Domain',
      description='Pythonic XML Shorthand',
      long_description='''surely is a 
      python script that converts files written
      in a shorthand notation similar to python
      syntax into well-formed XML''',
      author='Moe Aboulkheir',
      version=0.1,
      url='http://surely.sourceforge.net',
      author_email='moe@divmod.com',
      maintainer='Moe Aboulkheir',
      maintainer_email='moe@divmod.com',
      packages=('surely',),
      scripts=('bin/surely',))
