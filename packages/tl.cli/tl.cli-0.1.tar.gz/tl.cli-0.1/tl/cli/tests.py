# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt

import os
import os.path
import unittest
import doctest


flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(filename,
                             package="tl.cli",
                             optionflags=flags,
                             )
        for filename in sorted(os.listdir(os.path.dirname(__file__)))
        if filename.endswith(".txt")
        ])
