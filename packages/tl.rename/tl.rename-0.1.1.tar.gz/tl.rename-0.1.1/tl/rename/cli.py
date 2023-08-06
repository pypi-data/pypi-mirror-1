# Copyright (c) 2007-2008 Thomas Lotze
# See also LICENSE.txt

import sys
import optparse

import tl.rename.core


class CommandLineError(Exception):
    """Signals that the user wants rename to do something impossible.
    """


class Transformation(optparse.Option):
    """An option that defines a file name transformation.

    Stores whether transformations have been specified on the command line.
    """

    def __init__(self, parser, *args, **kwargs):
        optparse.Option.__init__(self, *args, **kwargs)
        self.parser = parser

    def take_action(self, *args, **kwargs):
        self.parser.transformations = True
        return optparse.Option.take_action(self, *args, **kwargs)


class OptionParser(optparse.OptionParser):
    """An option parser specialised for the rename executable.

    This is a class of its own in order to make it reusable.
    """

    transformations = False

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
        self.add_transformation(
            "-n", "--names-file",
            dest="names_file", default=None,
            help="read new names from file where - denotes standard input")
        case_choices = ["upper", "lower", "sentence"]
        self.add_transformation(
            "-c", "--case",
            dest="case", default=None,
            type="choice", choices=case_choices,
            help="case-transform names, possible values are " +
                 ', '.join(case_choices))
        self.add_transformation(
            "-r", "--replace",
            dest="replace", action="append", default=[], nargs=2,
            metavar="FROM TO",
            help="globally replace first option argument with second,\n"
                 "may be given multiple times")
        self.add_transformation(
            "-i", "--interactive",
            dest="interactive", action="store_true", default=False,
            help="edit names interactively "
                 "(assumed if no transformation is explicitly specified)")

    def add_transformation(self, *args, **kwargs):
        return self.add_option(Transformation(self, *args, **kwargs))

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
        if not self.transformations:
            options.interactive = True
        if not old_names:
            raise CommandLineError(
                "You must specify one or more files to rename.")
        self.process_names_file(options)
        return options, old_names


def sys_exit(exception, exit_code):
    sys.stderr.write(exception.__class__.__name__)
    exception_text = str(exception).rstrip()
    if exception_text:
            sys.stderr.write(": " + exception_text)
    sys.stderr.write("\n")
    sys.exit(exit_code)


def rename(**defaults):
    try:
        options, old_names = OptionParser(**defaults).grok_args()
        tl.rename.core.run(old_names, **options.__dict__)
    except AssertionError, e:
        sys_exit(e, 3)
    except CommandLineError, e:
        sys_exit(e, 2)
    except KeyboardInterrupt, e:
        sys_exit(e, 1)
    except Exception, e:
        if options.debug:
            raise
        sys_exit(e, 1)
