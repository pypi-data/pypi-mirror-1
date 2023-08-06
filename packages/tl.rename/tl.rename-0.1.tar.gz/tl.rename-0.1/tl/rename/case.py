# Copyright (c) 2007-2008 Thomas Lotze
# See also LICENSE.txt

import os.path


def is_roman(word):
    return set(word.upper()).issubset("IVXLCDM")


def sentence_case(name):
    new_name = ""
    first_word = True
    word = ""
    ellipsis = ""

    def transform_word():
        if is_roman(word):
            return word.upper()
        if first_word:
            return word.capitalize()
        return word.lower()

    for c in name:
        if c.isalpha():
            word += c
        else:
            if word:
                new_name += transform_word()
                first_word = False
                word = ""
            new_name += c
            if c == ".":
                ellipsis += c
                if ellipsis == "...":
                    first_word = False
            else:
                ellipsis = ""
    new_name += transform_word()

    return new_name


def sentence_case_path(path):
    new_names = []
    while path:
        path, name = os.path.split(path)
        if name:
            new_names.insert(0, sentence_case(name))
        else:
            new_names.insert(0, path)
            break
    return os.path.join(*new_names)


def transform_uppercase(old_names, **options):
    return [name.upper() for name in old_names]


def transform_lowercase(old_names, **options):
    return [name.lower() for name in old_names]


def transform_sentence_case(old_names, **options):
    return [sentence_case_path(name) for name in old_names]


transformations = dict(
    upper=transform_uppercase,
    lower=transform_lowercase,
    sentence=transform_sentence_case,
    )


def transform(old_names, case=None, **options):
    transform = transformations.get(case)
    if transform:
        return transform(old_names, **options)
    return old_names
