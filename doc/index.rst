bgrep - search for binary strings in binary files
=================================================

bgrep is a utility for searching for occurrences of binary strings
within binary files.
As its name suggests,
its interface and design is modeled after the ubiquitous "grep" command,
used to search for occurrences of text patterns in text files.

Although binary data is not very friendly for mere humans to read,
often there are patterns, especially ASCII 7-bit string sequences,
mixed in between raw binary bytes
and those strings can be of interest.
Therefore, one of the main uses for bgrep
is to search for ASCII character sequences
embedded in binary files.
One could instead open the file in a text editor or hex editor,
but if a quick glance or search is all you want
then bgrep meets that need.

bgrep is written in the Python programming language.
Although Python is often thought of as a "toy" language
or a language only for the web,
it is actually a perfect language for writing such a tool.
At its core, the operations that bgrep performs are high-level,
and "going native" doesn't provide enough of a speed increase
to warrent the maintenance overhead and difficulty
of writing and debugging portable C code.
Well, that's my opinion anyways!

bgrep is written by Denver Coneybeare (denver@sleepydragon.org).
The online documentation is available at http://bgrep.readthedocs.org.
The home page for Sleepy Dragon Software
where official releases are published is http://www.sleepydragon.org.
The source code for bgrep is hosted at GitHub
at https://github.com/sleepydragonsw/bgrep.

Table of Contents
=================

.. toctree::
    :maxdepth: 1

    changes
    todo
    source



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

