#!/usr/bin/python

"""Looks up anagrams for one or more rack(s) of letters.

Finds all anagrams in dictionary. Any letters in
uppercase will be required to be used. Dictionary can be chosen
among existing dictionaries. Minimum numbers of letters for
resulting words can be chosen."""

__author__ = "Joel Burton <joel@joelburton.com>"
__version__ = "1.0"

import sys
import os.path
import glob
import optparse
import shelve
import textwrap

import convert
import lookup
from config import DICTIONARIES_DIR, MINLENGTH_DEFAULT, DEFAULT_DICT


def anagrammer(words, dictfile, minlength, column=False):
    """Anagram words using dictfile and print results.
    
    @param words: words to anagram
    @type  words: iterable

    @param dictfile: path to shelve dictionary file
    @type  dictfile: string

    @param minlength: minimum # of letters for words
    @type  minlength: int

    @param column: print in single column?
    @type  column: boolean

    @returns: Nothing, just prints

    Tests for this function are in tests/anagrammer.txt.
    """

    worddict = shelve.open(dictfile, "r")

    if not column: print   # create top space

    for word in words:
        found = lookup.lookup(word, minlength, worddict)

        if column:
            if found:
                print "\n".join(found)

        else: 
            print word

            # pretty print, grouped by num letters
            if not found:
               print "\nNone found.\n"
               return

            print
            for wlen in range( len(found[0]), 0, -1 ):
                words = [ w for w in found if len(w) == wlen ]
                if words:
                    print "%s = %s" % (wlen, len(words))
                    print textwrap.fill(
                            " ".join(sorted(words)), 
                            initial_indent="  ", 
                            subsequent_indent="  ")
            print


def start():
    """Interactive start of program."""

    dicts = glob.glob("%s/*.anagram" % DICTIONARIES_DIR)
    dicts = [ os.path.splitext( os.path.basename(d) )[0] for d in dicts ]

    if DEFAULT_DICT in dicts:
        default_dict = DEFAULT_DICT
    else:
        default_dict = dicts[0]

    if dicts:
        parser = optparse.OptionParser(
                usage="%prog [options] rack ...", 
                version="%prog " + __version__, 
                description=__doc__
                )
    else:
        parser = optparse.OptionParser(
                usage="%prog [options]", 
                version="%prog " + __version__, 
                description="""Before using this program to find anagrams, you must
create an anagram dictionary with --convert. Once you have done this,
you can then re-rerun the program to find anagrams."""
                )
    parser.add_option(
            "--convert",
            dest="dictpath",
            help="Convert wordlist (plaintext or gzipped) at DICTPATH into anagram file.",
            type="string",
            )
    if dicts:
        if len(dicts) > 1:
            parser.add_option(
                    "-d", "--dict", 
                    dest="dict", 
                    help="Dictionary to use. Choice of (%s). Defaults to %s." % ( "|".join(dicts), default_dict ),
                    default=default_dict,
                    type="choice",
                    choices=dicts,
                    )
        parser.add_option(
                "-c", "--column",
                dest="column",
                help="Display in simple column (for other programs to read).",
                action="store_true",
                )
        parser.add_option(
                "-l","--min-length",
                dest="minlength",
                help="Minimum number of letters for found words (default: %s)." % MINLENGTH_DEFAULT,
                type="int",
                default=MINLENGTH_DEFAULT,
                )

    (options, args) = parser.parse_args()

    if options.dictpath:
        convert.convert(options.dictpath, DICTIONARIES_DIR)
        sys.exit()

    if len(args)<1:   # no word given
        parser.print_help()
        sys.exit(1)

    word = args[0:]
    dictfile = "%s/%s.anagram" % (DICTIONARIES_DIR, getattr(options, "dict", default_dict))

    anagrammer(word, dictfile, options.minlength, options.column)

