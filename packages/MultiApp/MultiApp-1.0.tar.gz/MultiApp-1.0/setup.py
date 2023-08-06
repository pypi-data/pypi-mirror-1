#!/usr/bin/env python
from distutils.core import setup

longdescr = r"""
MultiApp is a framework so that you can give your applications a quick and easy
way to have multiple functions at the command line. It's simple to use - you
just create a subclass of MultiApp like this::

    class FileStamper(MultiApp):
        '''
    FileStamper will manipulate logfiles in a special format. It is blah blah
    blah...(more long description)
        '''
        name = "FileStamper"
        version = "1.0"
        shortdesc = "A logging package."

        def do_log(self, file, message):   # User types log at the prompt
            # Add the message to the log...
        do_log.usage = "FILENAME MESSAGE"
        do_log.descr = "Adds a new entry to the log file."

        def do_latest_entry(self, file, number=5): # User types latest-entry
            # Retrieve the latest log message...
        do_latest_entry.usage = "FILENAME [NUMBER]"
        do_latest_entry.descr = "Retrieves the log's latest entry."

MultiApp provides your program with:

- Argument parsing that you can just treat like normal method arguments
- Integrated help system that works out of the box
- Very unobtrusive ways to define functionality
"""

setup(
name="MultiApp",
version="1.0",
author="LeafStorm/Pacific Science",
author_email="leafstormrush@gmail.com",
description="A framework for command-line apps with multiple commands.",
long_description=longdescr,
classifiers=[
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Environment :: Console",
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.5",
],
py_modules=['multiapp'],
provides=['multiapp'],
url="http://pac-sci.homeip.net/index.cgi/swproj/multiapp"
)

