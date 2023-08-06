=====================
Overview of tl.rename
=====================

tl.rename provides an implementation of the ``rename`` program some form of
which is included with many POSIX operating systems. While those tools usually
do only substring or regular expression replacement, planned file name
transformations in tl.rename include:

- substring replacement as in Gentoo's rename implementation, for example
- regular expression replacement as seen in Debian's rename implementation
- reading the new names from a file or standard input
- various case transformations
- additional regex replacements inserting formatted counters
- interactive renaming using readline, if available
- interactive renaming using an external text editor

Version 0.1 implements reading names from a file or standard input, case
transformations, simple substring replacement and interactive renaming using
readline.

The tl.rename package is readily usable as a library but also installs an
executable script that exercises its functionality.


Usage
=====

``rename [options] [file paths]``

File paths may contain directory paths and be either absolute or relative to
the current working directory. The specified files do not need to exist when
``rename`` is called but will cause it to fail if they do not exist when the
actual renaming is being done.

Options
-------

-h, --help            show this help message and exit
-d, --debug           debug mode, do not catch Python exceptions
-D, --dry-run         dry-run mode, do not touch the file system
-n NAMES_FILE, --names-file=NAMES_FILE
                      read new names from file where - denotes standard input
-c CASE, --case=CASE  case-transform names, possible values are upper, lower,
                      sentence
-r FROM_TO, --replace=FROM_TO
                      where FROM_TO is two distinct arguments (-r FROM TO);
                      globally replace first option argument with second,
                      may be given multiple times
-i, --interactive     edit names interactively (assumed if no transformation
                      is explicitly specified)


How it works
============

tl.rename runs one or more string transformations on a sequence of file names
given as command arguments, then renames the files accordingly.

Transforming file names
-----------------------

Which transformations to apply is determined by command line options. If
multiple transformations are selected, they will be run in the following
order:

#. Read names from file (``--names-file``)
    Read new file names from a file or standard input, one name per line.

#. Case transformation (``--case``)
    Perform a case transformation on the file names:
        * Turn the names into all upper case (``upper``).
        * Turn the names into all lower case (``lower``).
        * Apply a style of mixed case, basically capitalizing the first word
          of a phrase (``sentence``). See the doctest examples for sentence
          case for the complete rules.

#. Replace substrings (``--replace``)
    Replace substrings of the file names where match patterns and replacements
    are given literally as two arguments. Any number of replacements can be
    made in one go.

#. Interactive replacement (``--interactive``)
    Let the user edit each file name in turn using the readline library if
    available. This provides comfortable line editing including a history.

The list of file names must fulfill the following conditions:

- Each old and new name is non-empty and contains no null characters.

- The number of names remains the same during each transformation.

- Names must be unique before and after each transformation. Trailing path
  separators don't make a difference.

Renaming files
--------------

Once all transformations have been performed on the file names, those items
whose names have actually changed will be renamed in the file system (except
if dry-run mode is active). Renaming is subject to the following rules:

- Files and directories to be renamed must exist at this point.

- If a file name contains subdirectory path elements and one of those has
  changed, the item will be moved to the new directory.

- When moving items between directories, directory hierarchies will be created
  as needed and emptied directories are removed. Empty directories themselves
  can be moved.

- Renaming a file to the name of another existing file overwrites that file.

- Renaming a directory to the name of an existing empty directory overwrites
  that directory.

- Directories cannot be renamed to existing populated directories or
  non-directories, nor can non-directories be renamed to existing directories.

- Renaming an item to the name of another item that is renamed in the same run
  does not overwrite that item. In particular, it is possible to interchange
  the names of two items immediately.

- Symbolic links are never followed.


.. Local Variables:
.. mode: rst
.. End:
