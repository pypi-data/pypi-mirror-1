"""User-configurable settings."""

import os.path

# Store dictionaries in your home directory.

DICTIONARIES_DIR = os.path.expanduser("~") + "/.anagrammer"

# Uncomment this for system-wide dictionaries.
# You may need to make this directory writable to
# normal users for them to create dictionaries here.
#
#PATH = "/usr/local/share/games/anagrammer/"

# Change this to the name of the dictionary you want to
# use by default (otherwise, the first one found is the
# default

DEFAULT_DICT = "default"

MINLENGTH_DEFAULT = 5
