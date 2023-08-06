# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt

import os
import os.path
import unittest
from zope.testing import doctest

import tl.testing.fs


flags = (doctest.ELLIPSIS |
         doctest.INTERPRET_FOOTNOTES |
         doctest.NORMALIZE_WHITESPACE |
         doctest.REPORT_NDIFF)


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(filename,
                             package="tl.rename",
                             setUp=tl.testing.fs.setup_sandboxes,
                             tearDown=tl.testing.fs.teardown_sandboxes,
                             optionflags=flags,
                             )
        for filename in sorted(os.listdir(os.path.dirname(__file__)))
        if filename.endswith(".txt")
        ])
