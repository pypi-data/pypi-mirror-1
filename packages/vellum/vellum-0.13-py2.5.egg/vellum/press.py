# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from __future__ import with_statement
from vellum import ImportError
import vellum.parser
import os
import sys
from pprint import pprint

class Press(object):
    """
    A Press uses a Parser to read a build spec and then combine it
    with any given import statements.  This is the equiv. of the
    component in a interpreter that builds an AST with the parser.

    The next stage in the processing is for the Script to get the
    Press's results to analyze the contents.
    """

    def __init__(self, defaults={}):
        """
        Initializes the press according to the 
        defaults (which come from vellum.bin.parse_sys_argv().
        """
        self.options = defaults
        self.source = "~/.vellum/spec"

    def load(self, file):
        """Takes the name of a vellum file (with or without a .vel)
        and tries to load it returning the results."""
        name, ext = os.path.splitext(file)

        if ext == '.vel':
            # explicit file named, just load it exactly
            return self.load_file(file)
        elif ext == '':
            # import style named, look here, then look in ~/.vellum
            here = "%s.vel" % name
            there = os.path.expanduser("%s/%s" % (self.source, here))
            if os.path.exists(here):
                return self.load_file(here)
            elif os.path.exists(there):
                return self.load_file(there)
            else:
                raise ImportError("Could not find either %s or %s in current directory or %s.  Giving up." % (here, there, self.source))
        else:
            raise ImportError("File name %s is not a valid file (must end in .vel not %s)." % (file, ext))

    def load_module(self, name, as_name=None):
        """
        Appends the ~/.vellum/modules directory to the python
        path temporarily and then loads the module requested
        to get commands/functions inside.  If as_name is given then
        those functions are namespaces with as_name.func_name.
        If it's not given then the functions are just merged into
        this script's all at once.

        This is different from when you load .vel files since those
        are usually more complex and merging them by default would
        cause chaos.

        It only loads functions that don't begin with _.  This means
        that modules you import or classes are not included.  It
        determines that something is a method by looking for the
        __call__ attribute, so you can use functors if you like.
        """
        sys.path.append(os.path.expanduser("~/.vellum/modules"))
        mod = __import__(name, globals(), locals())

        # stupid hack to work around __import__ not really importing
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)

        # now module is the actual module we actually requested
        commands = {}
        for k,func in mod.__dict__.items():
            if not k.startswith("_") and hasattr(func, "__call__"):
                if as_name:
                    commands[as_name + "." + k] = func
                else:
                    commands[k] = func

        sys.path.pop()
        return commands

    def load_file(self, file):
        """
        Loads the given .vel file and does all the imports (recursively)
        and modules that it specifies.  End result is a fully formed
        vellum spec hash that Script can work with.
        """
        with open(file) as f:
            results = vellum.parser.parse('input', f.read() + '\0')
            if not results:
                raise ImportError("Parsing failure in %s" % file)
            else:
                if "imports" in results:
                    for imp in results["imports"]:
                        self.coagulate(results, imp.expr["from"], imp.expr.get("as", None))

                if "modules" in results:
                    results["commands"] = {}
                    for imp in results["modules"]:
                        results["commands"].update(
                                self.load_module(imp.expr["from"],
                                    imp.expr.get("as", None)))
                return results

    def coagulate(self, spec, name, as_name = None):
        """
        Basically does an import and does the name
        merging between the various options, targets, and depends hashes.
        """
        file, name = (name, as_name) if as_name else (name, name)

        if name not in spec["imports"]:
            sub_spec = self.load(file)
            for section in ["options","targets","depends"]:
                if section in sub_spec:
                    for key,val in sub_spec[section].items():
                        spec.setdefault(section, {})
                        spec[section]["%s.%s" % (name,key)] = val


