# Copyright (C) 2008 Zed A. Shaw. Licensed under the terms of the GPLv3.

from optparse import OptionParser
from itertools import chain
import sys
from . import DieError
from .press import Press
from .scribe import Scribe
from .script import Script
from pprint import pprint
from .version import VERSION
import re
from pprint import pformat
import time
import os


### @export "options table"
### These options are wired up by parse_sys_argv.
options = [
 ("-f", "--file", "filename",
  "Build file to read the build recipe from (no .vel)", "store", "build"),
 ("-q", "--quiet",  "verbose",
  "Tell Vellum to shut up.",  "store_false",  True),
 ("-d", "--dry-run",  "dry_run",
  "Dry run, printing what would happen",  "store_true",  False),
 ("-k", "--keep-going",  "keep_going",
  "Don't stop, build no matter what",  "store_true",  False),
 ("-T", "--targets",  "show_targets",
  "Display the search of targets and what they depend on",  "store_true",  False),
 ("-F", "--force",  "force",
  "Force all given conditions true so everything runs",  "store_true",  False),
 ("-D", "--dump",  "dump",
  "Dump the build out to a fully coagulated build.",  "store_true",  False),
 ("-s", "--shell",  "shell",
  "Run the vellum shell prompt.",  "store_true",  False),
 ("-I", "--install",  "install",
  "Create the ~/.vellum directories.",  "store_true",  False),
 ("-v", "--version",  "show_version",
  "Print the version/build number.",  "store_true",  False),
 ("-C", "--directory", "change_directory",
  "Change to DIR before doing anything.", "store", ""),
 ("-L", "--list-commands", "list_commands",
  "List all commands and their help, or one.", "store_true", False),
 ("-S", "--search", "search_commands",
  "Search commands with a regex.", "store_true", False),
 ("-w", "--watch", "watch_file",
  "Watch a file and run the targets whenever it changes.", "store", None),
 ('-o', '--option', 'extra_opts',
  'Options which should be available for interpolation at runtime, and will '
  'override any options set in the script.', 'append', None),
 ('-i', '--ignore-missing', 'ignore_missing',
  'Ignore missing build targets.', 'store_true', False),
]
### @end


### @export "parsing the options table"
def parse_sys_argv(argv):
    """
    Expects the sys.argv[1:] to parse and then returns
    an options hash combined with the args.
    """
    parser = OptionParser()
    for opt, long, dest, help, action, default in options:
        parser.add_option(opt, long,
                dest=dest, help=help,
                action=action, default=default)
    cmd_opts, args = parser.parse_args(argv)
    opts = vars(cmd_opts)
    extra = opts.pop('extra_opts')
    if extra:
        opts.update(dict([a.partition('=')[::2] for a in
            chain(*(b.split(',') for b in extra))]))
    return opts, args
### @end

def show_targets(options, script):
    """Just shows the target graph for the build."""
    script.show()

def dump(options):
    """
    Dumps the build file and all imported files it has
    as a giant Python search.
    """
    print "dump called"
    press = Press(options["filename"], options)
    pprint(press.main)

def install(options, script):
    """
    Installs the ~/.vellum dir and what it needs.
    """
    scribe = Scribe(script)
    scribe.log("Installing .vellum directory to your home directory.")
    scribe.command("install", None)

def commands(options, script, args):
    """
    Simply searchs all the commands and their help or
    the ones searched.
    """
    to_search = args or script.commands.keys()
    for cmd in to_search:
        func = script.commands.get(cmd)
        if func is None:
            doc = 'Unknown'
        elif func.__doc__:
            doc = '\n    '.join([x.strip() for x in func.__doc__.splitlines()])
        else:
            doc = 'Undocumented'
        print "%s:\n    %s" % (cmd, doc)

def shell(options, script, user_input=raw_input):
    """
    Runs a simple shell collecting input from the user.
    user_input is a function that gets called, defaults
    to raw_input, but during testing it is stubbed out.
    """
    scribe = Scribe(script)
    script.show()
    while True:
        print ">>>",
        try:
            targets = user_input()
        except EOFError:
            break
        scribe.build(targets.split(" "))

### @export "changing the current working directory"
def cd_build(directory):
    """Changes the directory then builds the targets."""
    print "Changing to %s." % cdir



### @export "building with Scribe"
def build(options, script, targets):
    """Builds the targets."""
    scribe = Scribe(script)
    scribe.build(targets)

### @export "implementation of -S"
def search(options, script, regex):
    """
    Searches through all available targets for anything that matches the
    given regex(es) in their name or their commands.
    """
    search = re.compile("^.*(" + " ".join(regex) + ").*$")

    commands = [cmd for cmd in script.commands
                if search.match(repr(cmd))]
    imports = ["- %s" % imp for imp in script.imports
                if search.match(repr(imp))]
    depends = ["- %s %r" % dep for dep in script.depends.items()
                if search.match(repr(dep))]
    targets = ["- %s\n\t%s" % (n,pformat(b))
                for n,b in script.targets.items()
                if search.match(repr((n,b)))]

    print "SEARCH FOR: ", regex
    if not (commands or imports or depends or targets):
        print "\tFound nothing."

    if commands: print "COMMANDS:", commands
    if imports:  print "\nIMPORTS:\n", "\n\n".join(imports)
    if depends:  print "\nDEPENDS:\n", "\n\n".join(depends)
    if targets:  print "\nTARGETS:\n", "\n\n".join(targets)
### @end

def watch(options, script, targets, count=None, sleep_time=2):
    """
    Runs in a delayed loop looking at a single file, and then
    runs the targets.  The count parameter is only really
    used in tests.
    """
    watching = options["watch_file"]
    stats = repr(os.stat(watching))
    print "Watching file %r for changes and running %r targets:" % (watching, targets)

    while True:
        try:
            time.sleep(sleep_time)
        except KeyboardInterrupt:
            print "Interrupted:  Hit enter to force a run, CTRL-C again to stop."
            try:
                keep_going = raw_input()
                stats = ""  # makes sure it's different
            except KeyboardInterrupt:
                print "Goodbye."
                sys.exit(0)

        test = repr(os.stat(watching))
        if test != stats:
            print "File %r changed, running targets: %r" % (watching, targets)
            stats = test
            try:
                build(options, script, targets)
            except DieError, err:
                print "ERROR: %s" % err

        # handle where only a set number is requested
        if count:
            count -= 1
            if count <= 0:
                break

### @export "the start of the world"
def run(argv=sys.argv):
    """
    Main entry for the entire program, it parses the command
    line arguments and then runs the other methods in this
    file to make Vellum actually work.
    """
    options, args = parse_sys_argv(argv)

    # change to the requested workdir before searching for scripts
    if options["change_directory"]:
        chdir = options['change_directory']
        print "Requested to chdir to ", chdir
        try:
            os.chdir(os.path.join('.', chdir))
        except OSError, error:
            print "Directory %s cant be accessed: %s"%(chdir, error)
            sys.exit(-1)

    try:
        script = Script(options["filename"], options)
        opts = script.options
        if opts["show_targets"]: show_targets(options, script)
        elif opts["dump"]: dump(options)
        elif opts["install"]: install(options, script)
        elif opts["shell"]: shell(options, script)
        elif opts["show_version"]: print VERSION
        elif opts["list_commands"]: commands(options, script, args)
        elif opts["search_commands"]: search(options, script, args)
        elif opts["watch_file"]: watch(options, script, args)
        else: build(options, script, args)

    except DieError, err:
        print "ERROR: %s" % err
        print "Exiting (use -k to keep going)"
        sys.exit(1)
    except ImportError, err:
        print "%s\nFix your script." % err
### @end
