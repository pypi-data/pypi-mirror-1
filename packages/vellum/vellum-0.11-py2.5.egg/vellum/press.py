from __future__ import with_statement
from vellum import ImportError
import vellum.parser
import os
from pprint import pprint

class Press(object):
    """
    A Press uses a Parser to read a build spec and then combine it with 
    any given import statements.
    """

    def __init__(self, defaults={}):
        """
        Initializes the press according to the 
        defaults (which come from vellum.bin.parse_sys_argv().
        """
        self.options = defaults
        self.source = "~/.vellum/spec"

    def load(self, file):
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


    def load_file(self, file):
        with open(file) as f:
            results = vellum.parser.parse('input', f.read() + '\0')
            if not results:
                raise ImportError("Parsing failure in %s" % file)
            else:
                if "imports" in results:
                    for imp in results["imports"]:
                        self.coagulate(results, imp.expr["from"], imp.expr.get("as", None))
                return results

    def coagulate(self, spec, name, as_name = None):
        file, name = (name, as_name) if as_name else (name, name)

        if name not in spec["imports"]:
            sub_spec = self.load(file)
            for section in ["options","targets","depends"]:
                if section in sub_spec:
                    for key,val in sub_spec[section].items():
                        spec.setdefault(section, {})
                        spec[section]["%s.%s" % (name,key)] = val


