# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

import sys
import optparse

import tl.rename.core


class CommandLineError(Exception):
    """Signals that the user wants rename to do something impossible.
    """


class OptionParser(optparse.OptionParser):
    """An option parser specialised for the rename executable.

    This is a class of its own in order to make it reusable.
    """

    def __init__(self, defaults={}, **kwargs):
        optparse.OptionParser.__init__(self, **kwargs)
        self.set_usage("usage: %prog [options] [file paths]")
        self.add_option(
            "-d", "--debug",
            dest="debug", action="store_true", default=False,
            help="debug mode, do not catch Python exceptions")
        self.add_option(
            "-D", "--dry-run",
            dest="dry_run", action="store_true", default=False,
            help="dry-run mode, do not touch the file system")
        self.add_option(
            "-n", "--names-file",
            dest="names_file", default=None,
            help="file with new names, or - for standard input")
        self.add_option(
            "-c", "--case",
            dest="case", default=None,
            type="choice", choices=["upper", "lower", "sentence"],
            help="turn the file name to upper, lower, or sentence case")
        self.add_option(
            "-r", "--replace",
            dest="replace", action="append", default=[], nargs=2,
            metavar="FROM TO",
            help="globally replace first option argument with second,\n"
                 "may be given multiple times")
        self.add_option(
            "-i", "--interactive",
            dest="interactive", action="store_true", default=False,
            help="edit names interactively")

    def process_names_file(self, options):
        if options.names_file == "-":
            if options.interactive:
                raise CommandLineError("Can't read names from standard input "
                                       "in interactive mode.")
            options.names_file = sys.stdin
        elif options.names_file:
            options.names_file = open(options.names_file)

    def grok_args(self):
        options, old_names = self.parse_args()
        self.process_names_file(options)
        return options, old_names


def sys_exit(exception, exit_code):
    sys.stderr.write(
        "%s: %s\n" % (exception.__class__.__name__, str(exception).rstrip()))
    sys.exit(exit_code)


def rename(**defaults):
    try:
        options, old_names = OptionParser(**defaults).grok_args()
        tl.rename.core.run(old_names, **options.__dict__)
    except AssertionError, e:
        sys_exit(e, 3)
    except CommandLineError, e:
        sys_exit(e, 2)
    except Exception, e:
        if options.debug:
            raise
        sys_exit(e, 1)
