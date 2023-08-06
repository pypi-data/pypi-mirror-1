# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt

"""Some readline related utilities.

API functions of this module act as no-ops if readline is not present.
"""

import os
import os.path
import functools

try:
    import readline
except ImportError:
    HAVE_READLINE = False
else:
    HAVE_READLINE = True


# History

# We're not embarrassed about using global variables for the history stuff
# since readline's own functionality is process global anyway.

history = {}
current_history = "__main__"

def use_history(name):
    """Switch to using the named readline history.

    Non-existent histories will be created on the fly.
    """
    if not HAVE_READLINE:
        return

    global current_history

    history[current_history] = [
        readline.get_history_item(i)
        for i in xrange(1, readline.get_current_history_length() + 1)]
    try:
        readline.clear_history()
    except AttributeError:
        for i in xrange(readline.get_current_history_length()):
            readline.remove_history_item(0)

    current_history = name
    if name in history:
        for item in history[name]:
            readline.add_history(item)


def with_history(name):
    """Run a function with the named readline history, then switch back.

    name: str

    Returns a function decorator.
    """

    def decorator(func):
        if not HAVE_READLINE:
            return func

        @functools.wraps(func)
        def decorated(*args, **kwargs):
            old_history = current_history
            use_history(name)
            try:
                result = func(*args, **kwargs)
            finally:
                use_history(old_history)
            return result

        return decorated

    return decorator


# Completion

def use_completion():
    """Turn on readline tab completion for the current process.
    """
    if not HAVE_READLINE:
        return

    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims("")


def static_completions(strings):
    """Creates a completer function from a sequence of strings.

    The completer function produces an iterable of completions on a partial
    string based on a static sequence of strings.

    If the partial string itself is the only possible completion, the
    completer returns an empty list in order to stop readline from offering
    that single completion again and again.

    strings: iterable of str

    Returns a function (text: str, *ignored) -> iterable of str.
    """
    strings = list(strings)

    def completions(text, *ignored):
        completions = [s for s in strings if s.startswith(text)]
        return completions if completions != [text] else []

    return completions


def completion_generator(completions):
    """A completion generator as required by readline.

    completions: callable (text: str, line: str, begidx: int, endidx: int)
                          -> iterable of str

    Returns a wrapper function (text: str, state: int) -> str or None,
            text: str, partial string to match,
            state: int, 0 causes matches to be recalculated,
            that returns successive matches, one per call, then None.
    """
    closure = locals()

    @functools.wraps(completions)
    def decorated(text, state):
        if not state:
            line = readline.get_line_buffer()
            begidx = readline.get_begidx()
            endidx = readline.get_endidx()
            closure["matches"] = iter(completions(text, line, begidx, endidx))

        for next in closure["matches"]:
            return next

    return decorated


def input(prompt, default=None, completions=None):
    """Prompts for user input, offering a default value and completion.

    Returns the exact input line except if the user indicates end-of-file
    (e.g. hitting CTRL-D). On EOF, returns the string representation of the
    default value.

    The string representation of the default value (or "" for None) is
    presented to the user. If the readline module is available, it is
    pre-inserted into the input line so it can be edited directly. Otherwise,
    it is displayed in brackets after the prompt.

    Custom readline completion can be used (if available) by passing a
    completer function.

    prompt: str

    default: any Python object

    completions: callable that returns an iterable of str and has signature
                 (text: str, line: str, begidx: int, endidx: int)

    Returns str.
    """
    if not HAVE_READLINE:
        prompt += "[%s] " % default
    else:
        if default is not None:
            def pre_input_hook():
                readline.insert_text(str(default))
                readline.redisplay()

            readline.set_pre_input_hook(pre_input_hook)

        if completions:
            old_completer = readline.get_completer()
            readline.set_completer(completion_generator(completions))

    try:
        result = raw_input(prompt)
    except EOFError:
        print
        result = default
    finally:
        if HAVE_READLINE:
            if default is not None:
                readline.set_pre_input_hook()
            if completions:
                readline.set_completer(old_completer)

    return result


def filename_completions(base_dir=None):
    """Create a completer function on file names from the file system.

    The completer function produces an iterable of completions on a partial
    string based on the listing of the directory found by traversing any but
    the final path element of the text fragment to be completed, starting from
    a base directory.

    If the partial string itself is the only possible completion, the
    completer returns an empty list in order to stop readline from offering
    that single completion again and again.

    base_dir: str, file system path to the base working directory, or
              None: default to the current working directory of the process

    Returns a function (text: str, *ignored) -> iterable of str.
    """
    if base_dir is None:
        base_dir = os.getcwd()

    def completions(text, *ignored):
        dirname, filename = os.path.split(text)
        path = os.path.join(base_dir, dirname)

        completions = [os.path.join(dirname, name)
                       for name in os.listdir(path) if name.startswith(filename)]
        if (completions == [text] and
            os.path.isdir(os.path.join(base_dir, text))):
                completions[0] = os.path.join(completions[0], "")

        completions.sort()
        return completions if completions != [text] else []

    return completions
