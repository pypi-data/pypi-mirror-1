from __future__ import with_statement
import os
import sys


def sh(scribe, expr):
    """Executes a shell command and first does a % string replace using the scribe's options."""
    if not scribe.option("dry_run"):
        scribe.log("sh: %s" % (expr % scribe.options))
        if os.system(expr % scribe.options) != 0: 
            scribe.die(expr)

def py(scribe, expr):
    """Evaluates the python as a statement.  The scrib's options are considered global variables."""
    try:
        if not scribe.option("dry_run"): 
            scribe.log("py: %s" % (expr % scribe.options))
            exec(expr, scribe.options)
    except Exception, err:
        scribe.die(expr, err)

def log(scribe, expr):
    """Logs some stuff to the user."""
    scribe.log(expr % scribe.options)

def needs(scribe, expr):
    """
    Tells you that this target needs another one to be run at this point.
    Think of it like a "target call" mechanism.
    """
    for target in expr:
        if not scribe.is_target(target):
            scribe.die(target, "target %s isn't in the targets list" % target)
        else:
            scribe.transition(target)

def given(scribe, expr):
    """Evals the given expression, and tells Vellum to stop processing this target
    (moving to the next) if it's False."""
    if scribe.option("force"): return False

    try:
        return not eval(expr % scribe.options)
    except Exception, err:
        scribe.die(expr, err)

def unless(scribe, expr):
    """Inverse of given, where you want things to continue *unless* something
    is true."""
    if scribe.option("force"): return False
    return not given(scribe, expr)

def gen(scribe, expr):
    """Generates a file from another file based on the scribe's options and the expr's."""
    if scribe.option("dry_run"): return

    scribe.log("gen: %r" % expr)

    # we want the scribe options merged into the expr
    expr.update(scribe.options)
    with open(expr["from"]) as fr:
        with open(expr["to"],'w') as to:
            input = fr.read()
            to.write(input % expr)

def install(scribe, expr):
    """Sets up the vellum home directory.  The scribe parameter is ignored."""
    mkdirs(scribe, {"paths": ["~/.vellum/modules"], "mode": 0700})

def mkdirs(scribe, expr):
    """Does an os.makedirs on the given paths (an array of them) but only if that
    directory exists. The scribe param is ignored.  The expr is expected to be
    {"paths": [...], "mode": 0700}.
    """
    assert isinstance(expr["paths"], list), "mkdirs expects a list as the expression"
    paths, mode = expr["paths"], expr.get("mode", 0700)

    for dir in [os.path.expanduser(p) for p in paths]:
        if not os.path.exists(dir):
            os.makedirs(dir, mode=0700)


