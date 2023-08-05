#!/usr/bin/python

"""Functions for finding statistical combinations."""

__author__ = "Joel Burton <joel@joelburton.com>"
__version__ = "1.0"


def combinations(items, n):
    """Return all combinations of items that are n in length.

    @param items: Items to combine
    @type  items: iterable

    @param n: Length of combinations to return
    @type  n: int

    @returns: Iterable of combinations; each combination is a list.

    aabc,3 => aab aac abc abc  (last twice because of different a's)

      >>> list(combinations("aabc", 3))
      [['a', 'a', 'b'], ['a', 'a', 'c'], ['a', 'b', 'c'], ['a', 'b', 'c']]

      >>> list(combinations("abc", 0))
      [[]]
    """

    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for cc in combinations(items[i+1:],n-1):
                yield [items[i]]+cc

def uniqSortedCombinations(items, n):
    """Return all alpha-unique combinations once sorted.

    @param items: Items to combine
    @type  items: iterable

    @param n: Length of combinations to return
    @type  n: int

    @returns: Iterable of unique (once-sorted) combinations; each combination is a tuple.

    aabc,3 => aab aac abc

        >>> list(uniqSortedCombinations("aabc", 3))
        [('a', 'a', 'b'), ('a', 'a', 'c'), ('a', 'b', 'c')]
    """

    seen = {}
    for c in combinations(items, n):
        c = tuple(sorted(c))
        if c in seen: 
            continue
        seen[c] = 1
        yield c

    # more consise:
    # return [list(x) for x in sets.Set(tuple(sorted(x)) for x in a)]


