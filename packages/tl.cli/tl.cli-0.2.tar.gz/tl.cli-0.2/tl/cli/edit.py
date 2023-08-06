# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt

"""Text editing on the command line.
"""

import os
import tempfile
import subprocess


def edit(text, editor=None, file_encoding=None):
    """Let the user edit a text string.

    Runs the user's favourite text editor (or vi) on a temp file containing
    the text string, then reads it back in and returns the edited content.

    The editor is called with the temp file name as its only argument.

    text: str or unicode

    editor: str, path to the executable to run as the editor, or
            None to fall back to $EDITOR or ``vi``

    file_encoding: str, encoding to use for the temp file, or
                   None to fall back to UTF-8
    """
    if not file_encoding and isinstance(text, unicode):
        file_encoding = "utf-8" # XXX detect somehow, with sensible default

    if not editor:
        editor = os.environ.get("EDITOR", "vi") # XXX use configurable default

    if file_encoding:
        text = text.encode(file_encoding)

    os_handle, tmp_name = tempfile.mkstemp()
    tmp = os.fdopen(os_handle, "w")
    tmp.write(text)
    tmp.close()
    subprocess.call([editor, tmp_name])
    text = open(tmp_name).read()
    os.unlink(tmp_name)

    if file_encoding:
        text = text.decode(file_encoding)

    return text
