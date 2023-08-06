from vellum import DieError
from vellum.parser import Reference
import vellum.commands
import os
import sys

class Scribe(object):
    """
    Turns a build spec into something that can actually run.
    Scribe is responsible for taking the results from Script 
    and loading the extra commands out of ~/.vellum/modules
    so that you can run it.
    """

    def __init__(self, script):
        self.script = script
        self.options = self.script.options
        self.target = None
        self.line = 1
        self.source = os.path.expanduser("~/.vellum/modules")
        self.load_vellum_modules()

    def load_vellum_modules(self):
        """
        Loads .py modules found in the ~/.vellum/modules directory so that the
        defined functions can become commands.
        """
        if os.path.exists(self.source):
            sys.path.append(self.source)
            os.path.walk(self.source, 
                    self.import_module, self.source)

    def import_module(self, source, dirname, files):
        """
        This weird function loads any python files in ~/.vellum/modules
        using __import__ and then merges their functions into
        this module's __dict__.  This allows those functions to
        be commands.  Any function that starts with _ isn't imported.
        """
        for file in files:
            name, ext = os.path.splitext(file)
            if ext == ".py":
                mod = __import__(name)
                for k,f in mod.__dict__.items():
                    if not k.startswith("_"):
                        vellum.commands.__dict__[name + "." + k] = f

    def option(self, name):
        """Tells if there's an option of this type."""
        return self.options.get(name,None)

    def log(self, msg):
        """Logs a message to the screen, but only if "verbose" option (not quiet)."""
        if self.option("verbose"): print msg

    def die(self, cmd, msg=""):
        """
        Dies with an error message for the given command listing 
        the target and line number in that target.
        """
        if not self.option("keep_going"):
            raise DieError(self.target, self.line, cmd, msg)

    def parse_target(self, target):
        """Given a target it pulls out the string or array and converts to an array of commands."""
        cmds = self.script.targets[target]
        if isinstance(cmds, list):
            return cmds  # lists of stuff are just fine
        elif isinstance(cmds, Reference):
            return [cmds]  # gotta put single references into a list
        elif isinstance(cmds, basestring):
            return cmds.split("\n") # convert big strings into lists of command shells
        else:
            self.die(target, "Definition of target %s isn't a list, command, or string." % target)
            return []  # needed in case -k is given

    def is_target(self, target):
        """
        Determines if this is a real target we can transition to, not a virtual
        one only found in the dependency graph.
        """
        return target in self.script.targets and self.script.targets[target]

    def is_command(self, name):
        """Tells the scribe if this name is an actual command."""
        return callable(vellum.commands.__dict__.get(name, None))

    def command(self, name, expr):
        """
        Returns the command for the given name.  Pulls it out of the
        vellum.command.__dict__ which is *actually* updated dynamically
        with the load_vellum_modules() function.
        """
        return vellum.commands.__dict__[name](self, expr)

    def transition(self, target):
        """
        The main engine of the whole thing, it will transition to the given target
        and then process it's commands listed.  It properly figures out if this is
        a command reference or a plain string to run as a shell.
        """
        if not self.is_target(target): return
        self.line = 0
        self.target = target

        for cmd in self.parse_target(target):
            self.line += 1
            # targets can contain either plain strings as shell commands or Reference objects
            # Reference objects are indications to run some Python command rather than a shell.
            if isinstance(cmd, Reference):
                if self.is_command(cmd.name):
                    result = self.command(cmd.name, cmd.expr)
                    # stop processing when one of them returns True!
                    if result: 
                        scribe.log("<-- %s" % cmd)
                        return
                else:
                    self.die(cmd, "Invalid command reference: %s with argument %r" % (cmd.name, cmd.expr))
            else:
                # it's just shell
                cmd = cmd.strip()
                if cmd: # skip blanks
                    vellum.commands.sh(self, cmd)

    def build(self, to_build):
        """
        Main entry point that resolves the main targets for
        those listed in to_build and then runs the results in order.
        """
        building = self.script.resolve_targets(to_build)
        self.log("BUILDING: %s" % building)
        for target in building:
            self.log("-->: %s" % target)
            self.transition(target)


