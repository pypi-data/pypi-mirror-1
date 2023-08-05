#!/usr/bin/python

"""Functions for looking up anagrams."""

__author__ = "Joel Burton <joel@joelburton.com>"
__version__ = "1.0"

import combinations

def lookup(word, minlength, worddict):
    """Given word, find anagrams in dictionary of length <=wordlen and >=minlength.
       
    @param word: word to anagram

    @param minlength: minimum # of letters for words
    @type  minlength: int

    @param worddict: mapping of pre-calculated, pre-sorted anagrams
    @type  worddict: dict or mapping

    @returns: List of words

    For example:

      >>> wd = { 'act': ['cat','act'], 'at': ['at'], 'dgo': ['dog' ] }

      >>> lookup("cat", 2, wd)
      ['cat', 'act', 'at']

      >>> lookup("cat", 3, wd)
      ['cat', 'act']

      >>> lookup("dog", 2, wd)
      ['dog']

      >>> lookup("cat", 10, wd)
      []

      >>> lookup("qxw", 2, wd)
      []

    """ 

    # Get letters, grab uppercase (must-use), then lowercase letters for matching
    mustuse = [ l.lower() for l in word if l.isupper() ]
    letters = [ l for l in word if l.islower() ]

    found = []
    searchmax, searchmin = len(letters), (minlength-1)-len(mustuse)
    for wlen in range(searchmax, searchmin, -1):
        for combo in combinations.uniqSortedCombinations(letters, wlen):
            key = ''.join(sorted(list(combo) + mustuse))
            found.extend(worddict.get(key, []))

    return found

