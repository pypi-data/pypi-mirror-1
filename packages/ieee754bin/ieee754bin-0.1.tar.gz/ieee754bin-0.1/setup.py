#!/usr/bin/env python

from distutils.core import setup, Extension
setup(name = "ieee754bin",
      version = "0.1",
      ext_modules=[
        Extension("ieee754bin", ["ieee754bin.c"])
        ],
      
      description = 'Python IEEE 754 binary library',
      long_description =
'''This is a small Python extension which allows you to manipulate the
binary representation of floating-point values in the standard IEEE
754 64-bit format (= C double type or Python float type).

Basically, the module includes methods to print integers and floating
point values in binary format, to convert floating-point values to and
from 64-bit integer representations, and to split/join floating-point
values into (sign, exponent, mantissa) tuples.''',
      author = 'Dan Lenski',
      author_email = 'lenski@umd.edu',
      url = 'http://tonquil.homeip.net/~dlenski/ieee754bin',
      license = 'GPLv3'
)                                                                                                  
