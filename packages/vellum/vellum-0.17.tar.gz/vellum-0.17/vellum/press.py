# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from __future__ import with_statement
import os
import sys
import itertools
from pprint import pprint

from .parser import parse
from . import LoadError
from . import commands

### @export "class Press"
class Press(object):
    """
    A Press uses a Parser to read a build spec and then combine it
    with any given import statements.  This is the equiv. of the
    component in a interpreter that builds an AST with the parser.

    The next stage in the processing is for the Script to get the
    Press's results to analyze the contents.
    """

    def __init__(self, main, defaults={}):
        """
        Initializes the press according to the
        defaults (which come from vellum.bin.parse_sys_argv().
        """
        self.options = defaults
        self.module_source = os.path.expanduser("~/.vellum/modules")
        self.recipe_source =  os.path.expanduser("~/.vellum/recipes")
        self.recipes = {}
        self.modules = {}
        self.main = self.load_recipe(self.resolve_vel_file(main))
        self.main["commands"] = {}
        # we always need these commands
        self.load('module', commands.__name__)
        self.imports(self.main)

    ### @export "resolve_vel_file"
    def resolve_vel_file(self, name):
        """
        Tries to find a file with
        the name by first trying in the local directory
        and then in the ~/.vellum/recipes directory.

        It will also try the name with .vel appended if one isn't given already.
        """
        if name == '-':
            return name

        velnames = [name]

        if not name.endswith(".vel"):
            velnames.append(name + ".vel")

        # allow absolute paths as well.
        if os.path.isabs(name):
            prefixes = ['']
        else:
            prefixes = ["./", self.recipe_source]

        for n in velnames:
            for t in (os.path.join(p, n) for p in prefixes):
                if os.path.exists(t) and os.path.isfile(t):
                    return t
        else:
            raise LoadError("Did not find file named %s at any of: %r." %
                (name, prefixes))

    ### @export "load"
    def load(self, kind, file, as_name=None):
        """
        Given a kind of 'recipe' or 'module' this figures out
        how to load the spec or python module.  It will do
        this recursively until it has loaded everything, and
        do it without causing loops.
        """
        if kind == "recipe":
            file = self.resolve_vel_file(file)
            if file not in self.recipes:
                spec = self.load_recipe(file)
                self.join(spec, self.main, file, as_name)
                self.imports(spec)
        elif kind == "module":
            if file not in self.modules:
                cmds = self.load_module(file)
                self.merge(cmds, self.main["commands"],
                           as_name=as_name)
        else:
            raise ImportError("Invalid kind of import %s, "
                            "use only 'recipe(...)' or "
                            "'module(...)'")

        return self.main

    ### @export "load_recipe"
    def load_recipe(self, file):
        """
        Loads a recipe and then calls self.load to get any
        imports that are defined.
        """
        # a function to do the actual loading. since its in a closure, its
        # all good as is.
        # this is to allow - as the "filename" for -f to be sys.std in
        def fload(fd):
            spec = parse('input', fd.read())
            if not spec:
                raise ImportError("Parser error in file: %s" % file)
            else:
                return spec
        # end func
        if file in self.recipes:
            return self.recipes[file]
        elif file == '-':
            return fload(sys.stdin)
        else:
            with open(file) as f:
                return fload(f)

    ### @export "load_module"
    def load_module(self, name):
        """
        Loads a python module and extracts all of the
        methods that are usable as Vellum commands.
        It returns a dict with the commands.
        """
        if name in self.modules: return self.modules[name]

        sys.path.append(self.module_source)
        mod = __import__(name, fromlist=['*'])

        # now module is the actual module we actually requested
        commands = {}
        for k,func in vars(mod).items():
            if not k.startswith("_") and hasattr(func, "__call__"):
                commands[k] = func

        sys.path.pop()
        return commands

    ### @export "scope_name"
    def scope_name(self, key, name=None, as_name=None):
        """Does the common name scopings used."""
        name = as_name if as_name else name
        return "%s.%s" % (name, key) if name else key


    ### @export "merge"
    def merge(self, source, target, named=None, as_name=None):
        """
        Takes the source and target dicts and merges
        their keys according to the way scope_name does
        it.  Source is untouched.
        """
        for key,val in source.items():
            target[self.scope_name(key,named,as_name)] = val

    ### @export "join"
    def join(self, source, target, named=None, as_name=None):
        """
        Takes two specs and properly joins them
        using the self.merge() function on all
        of the stanzas.
        """
        # first merge the common dict style stanzas
        for section in ["targets", "options", "depends"]:
            if section in source:
                target.setdefault(section, {})
                self.merge(source[section],
                           target[section], named, as_name)

    ### @export "imports"
    def imports(self, import_from):
        """
        Goes through the imports listed in import_from
        and then merges them into self.main.
        """
        if not "imports" in import_from: return

        for imp in import_from["imports"]:
            args = imp.expr
            if '%' in args['from']:
                try:
                    args['from'] %= self.options
                except KeyError:
                    try:
                        args['from'] %= import_from['options']
                    except KeyError:
                        pass
            self.load(imp.name, args["from"], args.get("as"))

