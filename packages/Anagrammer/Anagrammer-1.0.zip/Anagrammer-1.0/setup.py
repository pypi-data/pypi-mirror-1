#!/usr/bin/env python

from distutils.core import setup
files = ['tests/*']

setup(name='Anagrammer',
      version='1.0',
      description='Anagramming tools.',
      author='Joel Burton',
      author_email='joel@joelburton.com',
      url='http://www.joelburton.com',
      packages=['anagrammer','anagrammer.tests'],
      package_dir={'anagrammer':'src/anagrammer'},
      package_data={'anagrammer': files },
      scripts=['anagrammer'],
      long_description='Program to anagram word(s). Useful for deciding moves in word games.',
      platforms=['All'],
      license='GPL',
     )
