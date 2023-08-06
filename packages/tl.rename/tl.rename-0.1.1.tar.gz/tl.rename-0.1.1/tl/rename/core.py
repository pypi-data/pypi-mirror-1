# Copyright (c) 2007-2008 Thomas Lotze
# See also LICENSE.txt

import os
import os.path
import tempfile

import tl.rename.case
import tl.rename.replace
import tl.rename.interactive


def read_names_from_file(old_names, names_file=None, **options):
    if names_file is None:
        return old_names
    else:
        return names_file.read().splitlines()


transformations = [
    read_names_from_file,
    tl.rename.case.transform,
    tl.rename.replace.simple_replace,
    tl.rename.interactive.transform,
    ]


def assert_valid(names, error_msg):
    for name in names:
        if not name or '\x00' in name:
            raise AssertionError(error_msg % name)


def assert_unique(names, error_msg):
    if len(names) != len(set(os.path.abspath(name) for name in names)):
        raise AssertionError(error_msg)


def transform(old_names, **options):
    assert_unique(old_names, "Original names are not unique.")
    new_names = old_names[:]
    for t in transformations:
        t_repr = "<%s.%s>" % (t.__module__, t.__name__)
        new_names = t(new_names, **options)
        if len(new_names) != len(old_names):
            raise AssertionError(
                "Transformation %s changed number of names." % t_repr)
        assert_unique(new_names,
                      "Result of transformation %s is not unique." % t_repr)
    return new_names


def rename(old_names, new_names, dry_run=False):
    old_abspaths = set(os.path.abspath(old) for old in old_names)
    aside = []
    for old, new in zip(old_names, new_names):
        if old == new:
            continue

        if dry_run:
            print old, "->", new
            continue

        old = os.path.abspath(old)
        new = os.path.abspath(new)

        # Overwrite existing files similarly to os.rename (and existing
        # implementations of the rename shell command), but don't overwrite
        # files yet to be renamed by this process.
        if new in old_abspaths:
            temp_dir = tempfile.mkdtemp(prefix="tl.rename-",
                                        dir=os.path.dirname(old))
            temp = os.path.join(temp_dir, os.path.basename(old))
            aside.append((temp, new))
            os.renames(old, temp)
        else:
            os.renames(old, new)

    for temp, new in aside:
        os.renames(temp, new)


def run(old_names, dry_run=False, **options):
    assert_valid(old_names, "Invalid old file name: %r")
    new_names = transform(old_names, **options)
    assert_valid(new_names, "Invalid new file name: %r")
    rename(old_names, new_names, dry_run)
