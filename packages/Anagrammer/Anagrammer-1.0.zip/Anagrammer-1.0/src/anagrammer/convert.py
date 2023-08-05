#!/usr/bin/python

"""Functions for creating anagram dictionaries."""

__author__ = "Joel Burton <joel@joelburton.com>"
__version__ = "1.0"

import os.path
import gzip
import shelve

def alphaword(w):
    """foobar -> abfoor
    
    @param w: word to convert

    @returns: word with letters in alpha order

    For example:

      >>> alphaword("foobar")
      'abfoor'

      >>> alphaword("")
      ''

    """

    return ''.join(sorted(list(w)))



def convert(wordlist, path):
    """Convert a word list into an anagram dictionary.
       
    @param wordlist: path to word list (plaintext or gzipped)
    
    @param path: directory to store resulting file in

    @returns: None, but creates resulting file as side-effect.

    To demonstrate, let's set up a fake word list:

      >>> PATH="/tmp"
      >>> f = open("%s/doctest.lst" % PATH, 'w')
      >>> print >>f, "cat"
      >>> print >>f, "act"
      >>> print >>f, "dog"
      >>> f.close()
      
    Now convert it and test it:

      >>> convert("%s/doctest.lst" % PATH, PATH)

      >>> d = shelve.open("%s/doctest.anagram" % PATH)

      >>> d['act']
      ['cat', 'act']

      >>> d['dgo']
      ['dog']

      >>> d['pig']
      Traceback (most recent call last):
      ...
      KeyError: 'pig'

    And clean up:

      >>> os.unlink("%s/doctest.lst" % PATH)
      >>> os.unlink("%s/doctest.anagram" % PATH)
    """

    if not os.path.isdir(path):
        if os.path.exists(path):
            raise "FileExists", "A file exists at %s, which should be a path for our dictionaries." % path
        os.mkdir(path)

    name = os.path.splitext(os.path.basename(wordlist))[0]
    d = shelve.open("%s/%s.anagram" % (path, name), "n")

    if wordlist.endswith('.gz'):
        opener = gzip.GzipFile
    else:
        opener = file

    for word in opener(wordlist):
        word = word.strip().lower()
        letters = alphaword(word)

        # Shelve doesn't support "x in list" or "list.setdefault" and doesn't
        # notice values mutating, so we have do this very verbosely:

        if d.has_key(letters):
            d[letters] = d[letters] + [word]
        else:
            d[letters] = [word]
    d.close()

