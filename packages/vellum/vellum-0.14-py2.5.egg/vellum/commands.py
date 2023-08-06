# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

import os
import sys
import re
import fnmatch

def sh(scribe, expr):
    """
    Runs the given list of strings or string as a shell
    command, aborting if the command exits with 0.

    Usage: sh 'echo "test"'
    """
    if not scribe.option("dry_run"):
        formatted = scribe.interpolate("sh", "".join(expr))
        scribe.log("sh: %s" % formatted)
        if os.system(formatted) != 0: 
            scribe.die(expr)

def py(scribe, expr):
    """
    Runs the given list of strings or string as a python
    statements.  It doesn't stop, but if you raise an
    exception this will obviously stop the processing.
    You have access to all the options as globals.

    Usage: py 'print "hi"'
    """
    if not scribe.option("dry_run"): 
        formatted = scribe.interpolate("py", "".join(expr))
        scribe.log("py: %s" % formatted)
        exec(formatted, scribe.options)

def log(scribe, expr):
    """
    Logs the string to the user.

    Usage: log "hi there user"
    """
    scribe.log(scribe.interpolate("log", expr))

def needs(scribe, expr):
    """
    Indicates that before this target should continue,
    vellum needs to run the targets in the given list.
    If dependencies for a target don't fit in the main
    listing then use needs to put them in the target.

    Usage: needs ['clean', 'build', 'dist']
    """
    for target in expr:
        if not scribe.is_target(target):
            scribe.die(target, "target %s isn't in the targets list" % target)
        else:
            scribe.transition(target)

def given(scribe, expr):
    """
    Evaluates the list of strings or string as a Python
    expression (not statement) and if that expression is
    False stops processing this target.  Read it as:
      given X is True continue.

    Usage: given 'os.path.exists("/etc/passwd")'
    """
    if scribe.option("force"): return False

    try:
        return not eval(
                scribe.interpolate("given", "".join(expr))
                )
    except Exception, err:
        scribe.die(expr, err)

def unless(scribe, expr):
    """
    The inverse of given, this stops processing
    if the expression is True.  Reads as:
      unless X is False continue.

    Usage: unless 'not os.path.exists("/etc/passwd")'
    """
    if scribe.option("force"): return False
    return not given(scribe, expr)

def gen(scribe, expr):
    """
    Used to do simple code generation tasks.  It
    expects a "from" and "to" argument in a dict
    then it loads from, string interpolates the
    whole thing against the expr merged with the
    options, and finally writes the results to "to".

    Usage:  gen("from" somefile.txt "to" outfile.txt also "this")
    """
    if scribe.option("dry_run"): return
    scribe.log("gen: %r" % expr)
    expr.update(scribe.options)
    input = open(expr["from"]).read()
    open(expr["to"],'w').write(input % expr)

def install(scribe, expr):
    """
    Simple command that installs Vellum's ~/.vellum 
    directory for you.  You can also just use: vellum -I.
    WARNING: This might get replaced with something more
    like the install command.

    Usage: install
    """
    mkdirs(scribe, {"paths": ["~/.vellum/modules"], "mode": 0700})

def mkdirs(scribe, expr):
    """
    Takes a dict with "paths" and "mode" and then creates all of those
    paths each with the given mode.  It will also expand user paths
    on each one so you can use the ~ shortcut.

    Usage:  mkdirs(paths ["path1","path2"] mode 0700)
    """
    assert isinstance(expr["paths"], list), "mkdirs expects a list as the expression"
    paths, mode = expr["paths"], expr.get("mode", 0700)

    for dir in [os.path.expanduser(p) for p in paths]:
        if not os.path.exists(dir):
            os.makedirs(dir, mode=0700)

def forall(scribe, args):
    """
    Iterates the commands in a do block over all the files
    matching a given regex recursively.  You can put anything
    you'd put in a normal target in the do block to be executed,
    and when it is executed the 'as' variable is set to the
    full path of each file.  This will also be in each task
    you transition to with the 'needs' command.

    Usage: forall(files ".*.py$" as "file" do [ ... ])
    """
    files, name, commands = args["files"], args["as"], args["do"]
    top = args.get("in", ".")

    matches = []
    for path, dirs, fnames in os.walk(top):
        matches.extend(os.path.join(path, f) 
                        for f in fnmatch.filter(fnames, files))

    for f in matches:
        scribe.push_scope({name: f, "files": matches, "as": name})
        scribe.execute(commands)
        scribe.pop_scope()
