# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

import os
from pprint import pprint
from .press import Press

class Script(object):
    """
    Uses Press to parse the build spec and then constructs
    the internal data structures needed for Scribe.

    This is the equiv. of the component in a interpreter that
    cleans up and analyzes the parse tree so it can be
    acted on to execute it.  In our case the execution
    is done by the Scribe.
    """

    def __init__(self, file, defaults={}):
        """Uses the file and defaults to properly parse."""
        press = Press(file, defaults)
        for key in press.main:
            if hasattr(self, key):
                raise ImportError("You cannot define '%s' in "
                                  "the root of your vellum spec." % key)
        vars(self).update(press.main)
        self.options.update(defaults)
        self._handle_environment()

    def _handle_environment(self):
        # no specified environment in main vel file. Use os.environment
        if not hasattr(self, 'environment'):
            self.environment = os.environ.copy()
            return
        vel_environment = self.environment

        # use the system environment?
        if 'use_system' in vel_environment:
            use_system = vel_environment.pop('use_system')
            if use_system not in ['True','False']:
                raise ImportError('The environment option use_system must be '
                                  'either True or False')
            use_system = eval(use_system)

        else: use_system = True
        if use_system:
            self.environment = os.environ.copy()
            self.environment.update(vel_environment)
        return

    ### @export "resolve_depends"
    def resolve_depends(self, root):
        """
        Recursively resolves the dependencies for the root
        target given and return a list with those followed
        by the root.
        """
        building = []
        if root in self.depends:
            for dep in self.depends[root]:
                if dep in self.depends and not dep in building:
                    building.extend(self.resolve_depends(dep))
                else:
                    building.append(dep)
        building.append(root)
        return building
    ### @end

    def show(self):
        """
        Displays the targets, options, and default target.
        """
        print "OPTIONS:"
        pprint(self.options)

        print "\nTARGETS:"
        # some targets are only in depends
        keys = set(self.targets.keys() + self.depends.keys())
        for target in sorted(keys):
            building = self.resolve_depends(target)
            print "%s:\t%s" % (target, repr(building))
        print "\nDEFAULT: %s" % self.options.get("default", "None")

    ### @export "reducing targets"
    def reduce_targets(self, building):
        """Given a list of targets this removes consecutive dupes."""
        last = building[0]
        reduced = [last]
        for target in building[1:]:
            if target != last:
                reduced.append(target)
                last = target
        return reduced

    ### @export "resolving all targets"
    def resolve_targets(self, to_build=None):
        """
        Given a list of targets to_build this will make
        a new list with all of the dependencies resolved.
        """
        if not to_build:
            if "default" not in self.options:
                raise KeyError("You forgot to specify a default target and didn't give one on the command line.")
            else:
                return self.resolve_depends(self.options["default"])
        else:
            building = []
            for target in to_build:
                building.extend(self.resolve_depends(target))
            return self.reduce_targets(building)

