# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt

"""An enhanced command shell based on cmd.Cmd.
"""

import sys
import cmd
import traceback
import code
import pdb

import tl.readline


class Cmd(cmd.Cmd):
    """An enhanced command shell based on cmd.Cmd.

    - catches exceptions
    - provides an interactive Python shell and a postmortem debugger
    - handles EOF
    - ignores empty lines instead of repeating the previous command
    - accepts unique abbreviations for commands
    - adds a space after a fully tab completed command name
    - creates online help from command docstrings where appropriate
    """

    exc_info = None

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.interactive_names = globals().copy()
        self.interactive_names["self"] = self
        self.setup_help()

    def setup_help(self):
        """Create online help from command doc strings.

        Adds help_* attributes which are callables returning the docstring of
        the corresponding do_* command implementation for commands that don't
        have help and do have such a docstring.
        """

        def help_func(doc):
            # we need help_func's closure to store the value of doc
            def generic_help():
                print doc,
            return generic_help

        names = self.get_names()
        for name in names:
            if name.startswith("do_"):
                help_name = "help_" + name[3:]
                doc = getattr(self, name).__doc__
                if (help_name not in names and doc):
                    setattr(self, help_name, help_func(doc))

    def __getattr__(self, name):
        """Expand unique command abbreviations automatically.
        """
        if name.startswith(("do_", "complete_", "help_")):
            matches = set(c for c in self.get_names() if c.startswith(name))
            if len(matches) == 1:
                return getattr(self, matches.pop())
        raise AttributeError

    def onecmd(self, arg):
        """Handle exceptions raised by commands.

        Prevents the command loop from exiting due to exceptions other than
        keyboard interrupts and explicit exiting and stores tracebacks in
        self.exc_info, to be used by the postmortem debugger.
        """
        try:
            return cmd.Cmd.onecmd(self, arg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.exc_info = sys.exc_info()
            traceback.print_exc()
        finally:
            print

    def emptyline(self):
        return

    @tl.readline.with_history("python")
    def do_python(self, arg):
        """Interactive Python shell.

        The namespace consists of tl.cmd's globals plus the interpreter
        instance bound to ``self``.
        """
        code.interact("", local=self.interactive_names)

    @tl.readline.with_history("pdb")
    def do_postmortem(self, arg):
        """Postmortem debugger.

        Debugs the last exception that has occurred in a preceding command.
        """
        if self.exc_info:
            print
            pdb.post_mortem(self.exc_info[2])

    def do_EOF(self, arg):
        """Quit the interpreter when End-of-file is sent by the terminal.
        """
        return True

    def completenames(self, text, *ignored):
        """Add a space after a fully tab completed command name.

        Puts the cursor in a useful place for adding command arguments.
        """
        completions = list(set(cmd.Cmd.completenames(self, text, *ignored)))
        if len(completions) == 1:
            completions[0] += " "
        return completions

    def help_help(self):
        print "Help system."
