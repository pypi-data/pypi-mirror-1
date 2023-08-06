#!/usr/bin/python
"""
I/O ToolKit (IOTk)
==================
IOTk is a set of functions that make it easy to display output and get input
from the command line.

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

:author:  LeafStorm/Pacific Science
:license: GNU General Public License
"""

from os.path import isfile, isdir
from re import match


### INPUT VALIDATION ###

def _strval(value, max_length=None):
    if not max_length:
        return None
    else:
        if len(value) > max_length:
            return "Value must be less than " + str(max_length) + "characters"
        else:
            return None
def _strget(value):
    return value


def _intval(value, low=None, high=None):
    try:
        int(value)
        if low is not None:
            if int(value) < low:
                return "Value must be greater than " + str(low)
        if high is not None:
            if int(value) > high:
                return "Value must be less than " + str(high)
        return None
    except ValueError:
        return "Value must be a number"
def _intget(value):
    return int(value)


def _fleval(value):
    if isfile(value):
        return None
    else:
        return "Value must be a filename that exists"


def _fldval(value):
    if isdir(value):
        return None
    else:
        return "Value must be the name of an existing folder"


def _regval(value, regex, cust_msg=None):
    if match(regex, value):
        return None
    else:
        if cust_msg:
            return cust_msg
        else:
            return "Value must match this regular expression: " + regex


_yes = ['yes', 'ye', 'y', 'si', 'ja', 'da', 'sim', 'oui', 'hai', 'hija\'', 'ok']
_no  = ['no', 'n', 'nein', 'nei', 'nyet', 'nao', 'non', 'iie', 'ghobe\'', 'not']

def _y_nval(value):
    if value.lower() in _yes:
        return None
    elif value.lower() in _no:
        return None
    else:
        return "Value must be something like yes or no"
def _y_nget(value):
    if value.lower() in _yes:
        return True
    else:
        return False



def _ask(question, validator, **kwargs):
    while True:
        temp = raw_input(question + " ")
        valid = validator(temp, **kwargs)
        if valid is None:
            return temp
        else:
            print "The value is not acceptable: " + valid


def ask_string(question, max_length=None):
    return _strget(_ask(question, _strval, max_length=max_length))


def ask_int(question, low=None, high=None):
    return _intget(_ask(question, _intval, low=low, high=high))


def ask_filename(question):
    return _strget(_ask(question, _fleval))


def ask_folder(question):
    return _strget(_ask(question, _fldval))


def ask_yes_no(question):
    return _y_nget(_ask(question, _y_nval))


def ask_regex(question, regex, cust_msg=None):
    return _strget(_ask(question, _regval, regex=regex, cust_msg=cust_msg))



### OUTPUT FORMATTING ###

def print_dict(dicti, append="", prepend="", space=1, just='left', fill=" ", sort=False, rev=False):
    """
    This is a function that will print a dictionary for you with lots of shiny
    options. It accepts a dictionary as its first positional argument, followed
    by a bunch of optional arguments that control the way the dictionary is
    printed. By default, it might look something like this::
    
        Python               http://www.python.org
        Python 2.6 Docs      http://docs.python.org
        Python Package Index http://pypi.python.org
    
    However, you can apply the arguments:
    
    ``append``
        This will be inserted after every key in the dictionary when printed.
    ``prepend``
        This will be inserted before every key in the dictionary when printed.
    ``space``
        This is extra space that will be used when aligning the keys.
    ``just``
        You can set this to ``right``/``r`` for right justify, ``center``/``c``
        for centered text, or anything else for left align (the default).
    ``fill``
        This is the character (*only* one) that will fill up extra space.
    ``sort``
        This is False by default, but if True, it will sort the keys.
    ``rev``
        If sort is ``True`` and this is ``True``, then the keys will be reverse-
        sorted.
    """
    length = 0
    keys = dicti.keys()
    if sort:
        if not rev:
            keys.sort()
        elif rev:
            keys.sort(reverse=True)
    for key in keys:
        if len(str(key)) + len(append) + len(prepend) > length:
            length = len(str(key)) + len(append) + len(prepend)
    for key in keys:
        temp_data = prepend + str(key) + append
        if just.lower() == 'right' or just.lower() == 'r':
            print temp_data.rjust(length + space, fill) + str(dicti[key])
        elif just.lower() == 'center' or just.lower() == 'c':
            print temp_data.center(length + space, fill) + str(dicti[key])
        else:
            print temp_data.ljust(length + space, fill) + str(dicti[key])


def print_list(lst, append="", prepend="", space=0, fill=" ", just="left", sort=False, rev=False):
    """
    This function is like ``print_dict``, but it merely prints lists, item by 
    item, line by line. If you leave it alone, its output might look like::
    
        John Cleese
        Eric Idle
        Michael Palin
    
    It takes up to seven arguments:
    
    ``append``
        This will be inserted after every item in the list when printed.
    ``prepend``
        This will be inserted before every item in the item when printed.
    ``space``
        This is extra space that will be used when aligning the items.
    ``just``
        You can set this to ``right``/``r`` for right justify, ``center``/``c``
        for centered text, or anything else for left align (the default).
    ``fill``
        This is the character (*only* one) that will fill up extra space.
    ``sort``
        This is False by default, but if True, it will sort the items.
    ``rev``
        If sort is ``True`` and this is ``True``, then the items will be
        reverse- sorted.
    """
    length = 0
    if sort:
        if rev:
            lst.sort(reverse=True)
        else:
            lst.sort()
    for item in lst:
        if len(str(item)) + len(append) + len(prepend) > length:
            length = len(str(item))
    for item in lst:
        temp_data = prepend + str(item) + append
        if just.lower() == 'right' or just.lower() == 'r':
            print temp_data.rjust(length + space, fill)
        elif just.lower() == 'center' or just.lower() == 'c':
            print temp_data.center(length + space, fill)
        else:
            print temp_data.ljust(length + space, fill)

def wrap_str(strng, cols=80, sep=" "):
    """
    This will word-wrap words to a certain number of columns. It will preserve
    your existing newlines. You can provide a seperator to break words, but only
    one character. It's a space by default.
    """
    current = 0
    lines = list()
    cline = ""
    startlines = strng.splitlines()
    for line in startlines:
        words = line.split(sep)
        for word in words:
            if (len(cline) + len(word)) < cols:
                cline += word
                if (len(cline) + len(sep)) > cols:
                    pass
                else:
                    cline += sep
            else:
                lines.append(cline)
                cline = ""
                cline += word
                if (len(cline) + len(sep)) > cols:
                    pass
                else:
                    cline += sep
        if cline:
            lines.append(cline)
        cline = ""
    return lines

def print_string(strng, cols=80, sep=" ", just="left", fill=" "):
    """
    This is a "thick wrapper" around ``wrap_str``. It will wrap the string to a
    specified number of columns (the ``cols`` and ``sep`` arguments serve the
    same purpose as on ``wrap_str``, and then formats them with these arguments:
    
    ``just``
        If it's "right" or "r", the text is right-justified. If it's "center" or
        "c", the text is center-aligned. Anything else (like "left", the
        default) will produce left-alignment.
    ``fill``
        This will be used to stuff whatever fits in ``cols`` but isn't part of a
        string.
    
    You don't have to *just* use this for long strings that need wrapping - you
    can also use this to center or right-align shorter strings.
    """
    for line in wrap_str(strng, cols, sep):
        if just.lower() == 'right' or just.lower() == 'r':
            print line.rjust(cols, fill)
        if just.lower() == 'center' or just.lower() == 'c':
            print line.center(cols, fill)
        else:
            print line.ljust(cols, fill)
