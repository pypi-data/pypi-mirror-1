#!/usr/bin/env python

from distutils.core import setup

documentation = """
IOTk, also known as the Input/Output Toolkit, is a set of functions to get valid
input from and write stylish output to the command line.

Input Functions
---------------
``ask_string``
    Gets a string value from the user.
``ask_int``
    Asks the user for a value and makes sure that it's an integer.
``ask_yes_no``
    Checks for "yes" or "no" against 8 languages, plus plain old "y" and "n".
``ask_filename``
    Asks the user for a filename, then verifies that it exists.
``ask_folder``
    Asks the user for a folder name, then verifies that it exists.
``ask_regex``
    Gets a string from the user and verifies it against a regular expression.
    It can be supplied a custom invalidation message so the user doesn't see
    "Must match the regular expression: " followed by a bunch of apparently
    random characters and stop using your program out of frustration.


Output Functions
----------------
``print_dict``
    Prints the keys and values in a dictionary, with incredibly flexible
    formatting options.
``print_list``
    Prints the items in a list, with the same formatting options as
    ``print_dict``.
``wrap_str``
    A powerful word-wrapping function that will wrap words to a certain number
    of columns.
``print_string``
    A thick wrapper around ``wrap_str`` that provides alignment and fill
    options.
"""

setup(name="IOTk",
      version='1.0',
      author="LeafStorm/Pacific Science",
      author_email="pacsciadmin@gmail.com",
      url="http://pac-sci.homeip.net/index.cgi/swproj/iotk",
      description="A set of input and output functions for the command line.",
      long_description=documentation,
      py_modules=['iotk'],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.5',
                   'Topic :: Software Development :: User Interfaces'],
      provides=['iotk'])
