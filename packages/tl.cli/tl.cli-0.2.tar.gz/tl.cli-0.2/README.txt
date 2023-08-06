=======================
The tl.cli distribution
=======================

Various command line interface utilities.

This package requires Python 2, at least 2.5.


``tl.readline``: ``readline`` related utilities
===============================================

API functions of this module act as no-ops if readline is not present.


History handling
----------------

:``use_history(name)``:
  Switch between multiple named histories, e.g. when embedding one command
  interpreter inside another one.

:``with_history(name)``:
  Create a function decorator that runs a function with a named readline
  history, maintaining a stack of histories for nested function calls.


Tab completion
--------------

:``use_completion()``:
  Configure readline to use tab completion.

:``static_completions(strings)``:
  Create a completer function usable with readline that completes partial text
  based on a static list of strings. The completer function computes an
  iterable of matches.

:``completion_generator(completions)``:
  A function decorator that takes a completer function and returns a
  completion generator usable with readline. The completion generator returns
  successive matches on partial text based on a state parameter.

:``input(prompt, default=None, completions=None)``:
  A rich version of ``raw_input`` that in the presence of readline, allows for
  commad line editing the default value and using custom tab completion.
  Without readline, it displays the default value after the prompt.

:``filename_completions(base_dir)``:
  Create a completer function usable with readline that completes partial text
  based on file names from the file system. The completer function computes an
  iterable of matches.


``tl.cmd``: an enhanced command shell
=====================================

``tl.cmd.Cmd`` is a command shell based on Python's ``cmd.Cmd`` that adds some
generic usability features, some of them only of interest to developers.

- Exceptions are caught instead of aborting the command loop. The traceback is
  stored for subsequent introspection by the postmortem debugger. The debugger
  is run by the ``postmortem`` command.

- The ``python`` command runs a Python shell to access the command interpreter
  directly.

- End-of-file sent by the terminal quits the command loop.

- Empty input lines are ignored instead of repeating the previous command.

- Commands may be abbreviated as long as abbreviations are unambiguous.

- When using tab completion, the cursor is positioned more conveniently.

- Online help for commands is generated from the docstrings of the ``do_*``
  methods that implement them where no ``help_*`` methods exist.


``tl.cli.edit``: text editing
=============================

:``tl.cli.edit.edit(text, editor=None, file_encoding=None)``:
  Runs the user's favourite text editor (or vi) on a temp file containing the
  text string, then reads it back in and returns the edited content.


``tl.cli.page``: paging through text
====================================

:``tl.cli.page.page(text, pager=None)``:
  Runs the user's favourite pager (or more) on a text string or stream which
  is sent to the pager's standard input.

:``tl.cli.page.page_file(path, pager=None)``:
  Runs the user's favourite pager (or more) on a file whose path is passed to
  the pager as its only argument.


Contact
=======

This package is written by Thomas Lotze. Please contact the author at
<thomas@thomas-lotze.de> to provide feedback, suggestions, or contributions.

See also <http://www.thomas-lotze.de/en/software/>.


.. Local Variables:
.. mode: rst
.. End:
