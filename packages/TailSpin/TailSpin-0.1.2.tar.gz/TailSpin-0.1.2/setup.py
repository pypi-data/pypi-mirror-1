#!/usr/bin/env python

from setuptools import setup
from distutils.extension import Extension

setup(name='TailSpin',
      version='0.1.2',
      description='Efficient Tail Recursion',
      author='Xavid Pretzer',
      author_email='xavid@mit.edu',
      url='http://xavecode.mit.edu/tailspin/',
      classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries :: Python Modules'
    ],
      license = 'MIT',
      keywords = "tail recursion",
      package_dir = {'': 'src'}, 
      packages=['tailspin'],
      extras_require = {
    'lazy': ['lazypy']
    },
      ext_modules = [Extension("tailspin.fast_h",
                               ["src/tailspin/fast_h.c"]),
                     Extension("tailspin.fastlazy_h",
                               ["src/tailspin/fastlazy_h.c"])]
      )
