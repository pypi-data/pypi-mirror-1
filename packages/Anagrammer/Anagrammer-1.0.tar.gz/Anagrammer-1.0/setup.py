#!/usr/bin/env python

from distutils.core import setup
files = ['tests/*']

classifiers = """
Topic :: Text Processing :: General
Topic :: Games/Entertainment
Programming Language :: Python
Operating System :: OS Independent
Natural Language :: English
License :: OSI Approved :: GNU General Public License (GPL)
Intended Audience :: End Users/Desktop
Environment :: Console
Development Status :: 5 - Production/Stable
"""

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
      classifiers=[ c.strip() for c in classifiers.splitlines() if c.strip() ],
     )
