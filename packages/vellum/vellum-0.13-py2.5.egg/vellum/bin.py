# Copyright (C) 2008 Zed A. Shaw. Licensed under the terms of the GPLv3.

from optparse import OptionParser
import sys
import vellum
from vellum.press import Press
from vellum.scribe import Scribe
from vellum.script import Script
from pprint import pprint
from vellum.version import VERSION

### These options are wired up by parse_sys_argv.
options = [
    # opt  long       dest          help                                          action default
    ("-f", "--file", "filename", "Python file to read the build recipe from", "store", "build.vel"),
    ("-q", "--quiet",  "verbose",  "Tell Vellum to shut up.",  "store_false",  True),
    ("-d", "--dry-run",  "dry_run",  "Dry run, printing what would happen",  "store_true",  False),
    ("-k", "--keep-going",  "keep_going",  "Don't stop, build no matter what",  "store_true",  False),
    ("-T", "--targets",  "show_targets",  "Display the list of targets and what they depend on",  "store_true",  False),
    ("-F", "--force",  "force",  "Force all given conditions true so everything runs",  "store_true",  False),
    ("-D", "--dump",  "dump",  "Dump the build out to a fully coagulated build.",  "store_true",  False),
    ("-s", "--shell",  "shell",  "Run the vellum shell prompt.",  "store_true",  False),
    ("-I", "--install",  "install",  "Create the ~/.vellum directories.",  "store_true",  False),
    ("-v", "--version",  "show-version",  "Print the version/build number.",  "store_true",  False),
    ("-C", "--commands", "list-commands", "List all commands and their help. Give a name to see just that one.", "store_true", False),
]


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
    return cmd_opts.__dict__, args

def show_targets(options, script):
    """Just shows the target graph for the build."""
    script.show()

def dump(options, script):
    """
    Dumps the build file and all imported files it has
    as a giant Python list.
    """
    spec = Press(options).load(options["filename"])
    pprint(spec)

def install(options, script):
    """
    Installs the ~/.vellum dir and what it needs.
    """
    scribe = Scribe(script)
    scribe.log("Installing .vellum directory to your home directory.")
    scribe.command("install", {})

def commands(options, script, args):
    """
    Simply lists all the commands and their help or
    the ones listed.
    """
    to_list = args if args else script.commands.keys()
    for cmd in to_list:
        func = script.commands[cmd]
        doc = func.__doc__ if func.__doc__ else "\n    Undocumented"
        print "%s:%s" % (cmd, doc)

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

def build(options, script, targets):
    """Builds the targets."""
    scribe = Scribe(script)
    scribe.build(targets)

def run(argv):
    """
    Main entry for the entire program, it parses the command
    line arguments and then runs the other methods in this
    file to make Vellum actually work.
    """
    options, args = parse_sys_argv(argv)

    try:
        script = Script(options["filename"], options)
        opts = script.options
        if opts["show_targets"]: show_targets(options, script)
        elif opts["dump"]: dump(options, script)
        elif opts["install"]: install(options, script)
        elif opts["shell"]: shell(options, script)
        elif opts["show-version"]: print VERSION
        elif opts["list-commands"]: commands(options, script, args)
        else: build(options, script, args)
    except vellum.DieError, err:
        print "ERROR: %s" % err
        print "Exiting (use -k to keep going)"
        sys.exit(1)
    except vellum.ImportError, err:
        print "%s\nFix your script." % err

