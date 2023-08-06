#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(name='TailSpin',
      version='0.1',
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
      setup_requires=['Cython'],
      extras_require = {
    'lazy': ['lazypy']
    },
      cmdclass = {'build_ext': build_ext},
      ext_modules = [Extension("tailspin.fast_h",
                               ["src/tailspin/fast_h.pyx"]),
                     Extension("tailspin.fastlazy_h",
                               ["src/tailspin/fastlazy_h.pyx"])]
      )
