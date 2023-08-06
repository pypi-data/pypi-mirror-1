# Get the real implementation from a module whose name isn't readline so it
# can import Python's readline module. Importing readline from here would be
# interpreted as a relative import so this module would shadow Python's.

from tl.cli._readline import *
