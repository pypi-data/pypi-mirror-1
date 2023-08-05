#!/usr/bin/env python
"""
Runs the HJB demo scenarios from the command line.

"""

import sys
from getopt import getopt

import hjb.demo 

__all__ = [
    "DemoCommand",
]

def find_subclasses(clazz):
    result = []
    def update_subclasses(clazz, result):
        subclasses = clazz.__subclasses__()
        if subclasses:
            result.extend(subclasses)
            [update_subclasses(s, result) for s in subclasses]
    update_subclasses(clazz, result)
    return result

def to_underscore_separated(any_string):
    result = []
    def add_underscores(last_was_upper, text, result):
        if text:
            first_is_upper = text[0].isupper()
            if first_is_upper and not last_was_upper:
                result.append('_')
            result.append(text[0].lower())
            add_underscores(first_is_upper, text[1:], result)
    add_underscores(True, any_string, result)
    return "".join(result)

def get_demo_command_classes():
    return dict([(to_underscore_separated(clazz.__name__), clazz) 
            for clazz in find_subclasses(hjb.demo.Demo)]) 

class DemoCommand(object):
    """I handle an invocation of the demo application from the command line."""

    def __init__(self, scenario, aliases, command=None, args=[], **kw):
        self.aliases = aliases
        self.scenario = scenario
        self.command = command or sys.argv[0]
        self.args = args or sys.argv[1:]
        self.parse_arguments()

    def usage(self, msg=None, exit_with=None):
        if msg:
            print msg
            print "\ntry: %s --help" % (self.command,)
        else:
            print "usage: %s" % (self.command,),
            print usage.strip()
        if exit_with is not None:
            sys.exit(exit_with)

    def parse_arguments(self):
        opts, args = getopt(self.args, 'hD:', ['help'])
        if (0 == len(args)):
            self.usage(exit_with=1)
        keywords = []
        for o, a in opts:
            if o in ('-h', "--help"):
                self.usage(exit_with=0)
            if o.startswith("-D") and not "=" in a:
                print "[IGNORED] '-D' value '%s' is not a keyword assignment" % a 
            if o.startswith("-D") and "=" in a:
                keywords.append(a)
        kw = dict([k.split('=', 1) for k in keywords])
        self._generate_execute(args, **kw)

    def _generate_execute(self, args, **kw):
        """Generate the function called by the execute method.

        Expects that the first argument of `args` will match a class that
        extends hjb.demo.Demo. The generated execute method:

            - tries to create an instance of the class with `self.scenario` and
              `self.aliases` as arguments

            - invokes `configure_logging` on the resulting instance

            - invokes `configure_session` on the resulting instance

            - invokes `run` with the remaining command line arguments

        """
        subcommand = args[0]
        if not subcommand in demo_commands:
            self.usage(
                    "%s is not a recognised subcommand. These available subcommands are: %s"  
                    % (subcommand, demo_commands_as_text), 
                    exit_with=1)

        def make_demo():
            demo_class = demo_commands[subcommand]
            all_init_argnames = set(demo_class.__init__.im_func.func_code.co_varnames)
            restricted_argnames = set(["self", "scenario", "aliases"])
            used_keys = set(kw.keys()).intersection(all_init_argnames - restricted_argnames)
            demo_kw = dict([(k, kw[k]) for k in kw if k in used_keys])
            demo = demo_class(self.scenario, self.aliases, **demo_kw)
            return demo
        def _execute():
            """Create, configure and run the class specified by the demo command"""
            demo = make_demo() 
            demo.configure_logging()
            demo.configure_session()
            last_arg_needed = min(len(args), demo.run.im_func.func_code.co_argcount)
            demo.run(*args[1:last_arg_needed])
        self._execute = _execute

    def execute(self):
        self._execute() 
        
demo_commands = get_demo_command_classes()
demo_commands_as_text = "".join(["\n  " + c for c in demo_commands.keys()])

usage = """ [-Dkey1=value1 ... -DkeyN=valueN] subcommand [subcommand_arg1 ... sub_command_argN]

Run demos showing py.hjb interacting with JMS messaging providers.  Each demo
corresponds to a distinct subcommand.  The supported subcommands are:

%s
""" % (demo_commands_as_text,)

def main():
    pass

if __name__ == '__main__':
    main()
