# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt


def simple_replace(old_names, replace=[], **options):
    names = old_names
    for old, new in replace:
        names = [name.replace(old, new) for name in names]
    return names
