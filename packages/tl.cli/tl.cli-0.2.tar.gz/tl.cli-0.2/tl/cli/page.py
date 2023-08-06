# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt

"""Sending text to a pager.
"""

import os
import subprocess


def page(text, pager=None):
    """Let the user page through a text string or stream.

    Runs the user's favourite pager (or more) on a text string or stream which
    is sent to the pager's standard input.

    text: str or file-like object

    pager: str, path to the executable to run as the pager, or
           None to fall back to $PAGER or ``more``
    """
    sub = subprocess.Popen([_get_pager(pager)], stdin=subprocess.PIPE)
    if isinstance(text, str):
        sub.communicate(text)
    else:
        while not sub.stdin.closed:
            chunk = text.read(1024)
            if not chunk:
                sub.stdin.close()
                break
            try:
                sub.stdin.write(chunk)
            except IOError, e:
                if e.errno == 32:
                    # Broken pipe
                    break
                raise
        sub.wait()


def page_file(path, pager=None):
    """Let the user page through a file.

    Runs the user's favourite pager (or more) on a file whose path is passed
    to the pager as its only argument.

    path: str, path to a file to be displayed by the pager

    pager: str, path to the executable to run as the pager, or
           None to fall back to $PAGER or ``more``
    """
    subprocess.call([_get_pager(pager), path])


def _get_pager(pager):
    """Helper function that determines the pager to use.
    """
    if not pager:
        pager = os.environ.get("PAGER", "more") # XXX use configurable default
    return pager
