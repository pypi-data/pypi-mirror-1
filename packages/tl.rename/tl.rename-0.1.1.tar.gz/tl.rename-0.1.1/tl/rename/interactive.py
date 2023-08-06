# Copyright (c) 2007-2008 Thomas Lotze
# See also LICENSE.txt

import os
import os.path

import tl.readline


def transform(old_names, interactive=False, **options):
    if not interactive:
        return old_names

    tl.readline.use_completion()

    try:
        return [tl.readline.input("", name,
                                  tl.readline.filename_completions())
                for name in old_names]
    except KeyboardInterrupt:
        print
        raise
