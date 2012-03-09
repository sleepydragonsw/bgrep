bgrep - search binary files for substring matches
By: Denver Coneybeare <denver@sleepydragon.org>
March 06, 2012

===============================================================================
Table Of Contents
===============================================================================

1. Introduction
2. Examples
3. Installation
4. Development
     4.1 Eclipse Setup
     4.2 Eclipse Project Setup

===============================================================================
1. Introduction
===============================================================================

bgrep is a utility for searching for occurrences of binary strings within
binary files.  As its name suggests, its interface and design is modeled after
the ubiquitous "grep" command, used to search for occurrences of text patterns
in text files.

Although binary data is not very friendly for mere humans to read, often there
are patterns, especially ASCII 7-bit string sequences, mixed in between raw
binary bytes and those strings can be of interest.  Therefore, one of the main
uses for bgrep is to search for ASCII character sequences embedded in binary
files.  One could instead open the file in a text editor or hex editor, but if
a quick glance or search is all you want then bgrep meets that need.

bgrep is written in the Python programming language.  Although Python is often
thought of as a "toy" language or a language only for the web, it is actually
a perfect language for writing such a tool, because at its core the operations
are very high-level and "going native" doesn't provide enough of a speed
increase to warrent the maintenance overhead and difficulty of writing and
debugging portable C code.  Well, that's my opinion anyways!

===============================================================================
2. Examples
===============================================================================

2.1 Example: search for occurrences of the ASCII string "hello" in a file
    named data.dat

    bgrep.py hello data.dat

===============================================================================
3. Installation
===============================================================================

The entirety of the bgrep proper is stored in a single Python file, bgrep.py.
So the only requirement to use bgrep is to have Python 3 available on your
system.  Note that Python 2 will not work, as Python 3 has some new language
features that are not available in Python 2.

So if you have Python 3 set up on your computer, it's just a matter of running
bgrep.py just like any other Python 3 program.

===============================================================================
4. Development
===============================================================================

Since bgrep is simply a Python program, all you really need to develop it is
a Python interpreter and a text editor.  That being said, I prefer to develop
using Eclipse as it provides handy features like code completion, code
navigation, and debugging.


4.1 Eclipse Setup

Eclipse by itself knows nothing about Python.  However, there is an amazing
plugin for Eclipse called PyDev, which gives it full functionality for Python
software development.

First, install Eclipse by going to http://eclipse.org and following the
instructions there.  If unsure, just pick the latest "Eclipse Classic" bundle,
extract it, and run the eclipse command and you've got Eclipse setup.

Next, install the PyDev plugin.  To do this, find the update URL at
http://pydev.org, which at the time of writing is http://pydev.org/updates,
and enter it into Eclipse's installation screen to install it.  At the time of
writing, I am using Eclipse 3.7.0 and this is done by opening the "Help" menu,
selecting "Install New Software", clicking the "Add" button, pasting the URL,
clicking OK, then following the rest of the instructions to complete the
installation and restart Eclipse.

When Eclipse restarts, configure your Python installation in Eclipse's
Window -> Preferences -> PyDev -> Interpreter - Python section and clicking
"Auto Config".  If it doesn't automatically find a Python 3 interpreter, click
"New..." and tell PyDev the path to the Python 3 interpreter.


4.2 Eclipse Project Setup

[to be continued...]
