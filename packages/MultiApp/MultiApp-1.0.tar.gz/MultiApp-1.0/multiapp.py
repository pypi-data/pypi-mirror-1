#!/usr/bin/env python
"""
MultiApp
========
MultiApp is a command line tool for allowing single commands to run multiple
functions (like ``svn`` and ``trac-admin``).

You'll need to do these:

1. Create a subclass of ``MultiApp``. Give it the attributes ``name`` (a short,
   friendly name for the app), ``version`` (as a string, the version number of
   the app), and ``shortdesc`` (50 chars or less, a short description). If the
   subclass has a docstring, it is printed when the main help is called - it
   should not be very long, or incorporate description of the subcommands - they
   are included at the bottom by default.
2. For each command you want to run, define a method named ``do_commandname``.
   It should accept positional arguments. You can give them names, and as an
   added bonus, if a TypeError is caught, the usage message will be
   displayed if it is set.
3. This command should have a docstring to be accessed by the built-in ``help``
   command.
4. Give the command usage and description values. Do this with::
    
    do_foo.descr = "A command that will foo."
    do_foo.usage = "[OPTIONS...] BAR"

Other things of note:

- You can add non-command help files by creating a ``topics`` dictionary as an
  attribute of the class.
- If you remap the built-in ``help`` command, set the class's ``help_cmd``
  attribute so the application can print a proper ``For help, type...`` message.
- If you need to access one of the commands, use ``self.getcmd``, because it
  will automatically prefix the "do_" and display a patronizing error message if
  the command doesn't exist.
- Command names can have dashes in them, but the actual methods must have
  underscores where the dashes are typed. They can still have underscores, and
  they won't be converted.
"""

import sys
import os
from os.path import basename
from iotk import *

class MultiApp:
    """
    This is a base class for MultiApp. You can populate it with commands by
    creating, documenting, and providing certain attributes to methods of a
    subclass of MultiApp.
    """
    name = "<<MultiApp>>"
    version = "2008.12.2"
    shortdesc = "This is the base class for command-line apps"
    
    topics = dict()
    commands = dict()
    help_cmd = "help"
    
    def cmd_list(self):
        """
        This will hunt down every command, even those in base classes. Code
        lovingly ripped off from ``cmd.Cmd`` in the Standard Library.
        """
        names = []
        classes = [self.__class__]
        while classes:
            aclass = classes.pop(0)
            if aclass.__bases__:
                classes = classes + list(aclass.__bases__)
            names = names + dir(aclass)
        return [attrib for attrib in names if attrib.startswith("do_")]
    
    def run(self, args=sys.argv):
        self.ename = basename(args[0])
        if len(args) < 2:
            self.default()
            return
        cmdname = args[1]
        if len(args) > 2:
            arguments = args[2:]
        else:
            arguments = []
        if self.cmd_to_fn(cmdname) in self.cmd_list():
            command = self.getcmd(cmdname)
            try:
                command(*arguments)
            except TypeError:
                if hasattr(command, "usage"):
                    print self.gen_usage(cmdname, command.usage)
                else:
                    print "Wrong parameters supplied."
                print "Type '" + self.gen_help() + "' for help topics"
        else:
            self.notfound(cmdname)
    
    def gen_usage(self, name, usage):
        return "USAGE: " + self.ename + " " + name + " " + usage
    
    def cmd_to_fn(self, name):
        return "do_" + name.replace("-", "_")
    
    def fn_to_cmd(self, name):
        return name[3:].replace("_", "-")
    
    def gen_help(self):
        return self.ename + " " + self.help_cmd
    
    def notfound(self, cmdname):
        print "Command", cmdname, "does not exist."
        print "Type '" + self.gen_help() + "' for help topics'"
    
    def default(self):
        header = self.name + " " + self.version
        print_header(header)
        print self.shortdesc
        print
        print "USAGE: " + self.ename + " [subcommand] [arguments]"
        print "Type '" + self.gen_help() + "' for help topics"
    
    def do_help(self, *args):
        """
        This is the online help system. It displays information about commands
        and assorted other help topics defined by the application. Simply
        typing "help" will list all help topics, while typing "help something"
        will display the full command.
        """
        if not args:
            self.help_index()
        else:
            self.help_topic(args[0])
    do_help.usage = "[COMMAND-OR-TOPIC]"
    do_help.descr = "Get info on commands and other functions."
    
    def gen_descrs(self):
        descrs = dict()
        for comname in self.cmd_list():
            command = getattr(self, comname)
            if hasattr(command, "descr"):
                descrs[self.fn_to_cmd(comname)] = command.descr
            else:
                descrs[self.fn_to_cmd(comname)] = "---"
        return descrs
            
    def help_index(self):
        print_header(self.name + " Help Topics")
        if self.__doc__:
            print trim_docstring(self.__doc__)
        print
        if self.topics:
            print_header("Topics", underline="-", just="left")
            print_list(self.topics.keys(), sort=True)
            print
        if self.cmd_list():
            print_header("Commands", underline="-", just="left")
            print_dict(self.gen_descrs(), space=2, sort=True)
            print
    
    def help_topic(self, lookup):
        if self.cmd_to_fn(lookup) in self.cmd_list():
            self.cmd_help(lookup)
        elif lookup in self.topics:
            self.topic_help(lookup)
        else:
            print "There's not a help topic named that."
            print "Type '" + self.gen_help() + "' for help topics"
            return

    def cmd_help(self, cmdname):
        command = self.getcmd(cmdname)
        print
        print_header(self.name + ": Help for command '" + cmdname + "'")
        if hasattr(command, "usage"):
            print self.gen_usage(cmdname, command.usage)
        if command.__doc__:
            print
            print trim_docstring(command.__doc__)
        else:
            if hasattr(command, "descr"):
                print
                print command.descr
            else:
                print
                print "Sorry, no help for this command."
        print
    
    def topic_help(self, lookup):
        print
        print_header(self.name + ": Help on topic '" + lookup + "'")
        print self.topics[lookup]
        print
    
    def getcmd(self, something):
        cmdname = self.cmd_to_fn(something)
        if hasattr(self, cmdname):
            return getattr(self, cmdname)
        else:
            print "Horrible Error: Command", cmdname, "not found."


if __name__ == "__main__":
    class TestApp(MultiApp):
        """
        This is just a simple test application. You can use this to get an idea
        of how to use MultiApp.
        """
        name = "MultiApp Test"
        version = "0.0"
        shortdesc = "This is an app designed to test out MultiApp."
        
        topics = {'dummy-topic': "This is just a dummy help topic. Disregard it."}

        
        def do_alpha(self, *args):
            """
            Prints the arguments passed to it. Note that this does not include
            the program's name and ``alpha`` itself, just everything after that.
            """
            print "Arguments: "
            for arg in args:
                print arg
        do_alpha.usage = "[ARGUMENTS...]"
        do_alpha.descr = "Lists all of the arguments passed to it."
        
        def do_bravo(self, name):
            """
            Says "Hello, NAME!" Intended to test out argument-error-catching
            facilities.
            """
            print "Hello, " + name + "!"
        do_bravo.usage = "NAME"
        do_bravo.descr = "Says Hello, NAME!"
        
        def do_charlie_delta(self, *args):
            """
            Prints the arguments passed to it. It's just like ``alpha``, but it
            has a hyphen to test out the concept of hyphenated commands.
            """
            print "Arguments: "
            for arg in args:
                print arg
        do_charlie_delta.usage = "[ARGUMENTS...]"
        do_charlie_delta.descr = "Does the same thing as alpha, but " \
        "with a hyphen in the name and a longer description."
        
        def do_echo(self, *args):
            # Completely undocumented.
            print "Arguments: "
            for arg in args:
                print arg
    
    
    app = TestApp()
    app.run()
