#!/usr/bin/python3

################################################################################
#
# bgrep.py - search binary files for substring matches
# By: Denver Coneybeare <denver@sleepydragon.org>
# March 06, 2012
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

import argparse
import glob
import itertools
import logging
import os
import sys

################################################################################

VERSION = "1.0.0"

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_ARGS = 2

################################################################################

def main(prog=None, args=None, stdout=None, stderr=None, stdin=None):
    """
    The main entry point for the bgrep application.

    *prog* must be a string whose value is the name of the program to use; may
    be None (the default) to use sys.argv[0].
    *args* must be an iterable of strings whose values will be used as the
    application's arguments; may be None (the default) to use sys.argv[1:].
    *stdout* must be a file-like object opened in text mode to use as the
    standard output stream; may be None (the default) to use sys.stdout.
    *stderr* must be a file-like object opened in text mode to use as the
    standard error stream; may be None (the default) to use sys.stderr.
    *stdin* must be a file-like object opened in text mode to use as the
    standard input stream; may be None (the default) to use sys.stdin.

    Returns EXIT_SUCCESS if the program completed successfully, EXIT_ERROR if
    the program failed, or EXIT_ARGS if the command-line arguments given in the
    *args* parameter were invalid.
    """

    # assign the default values for arguments that were not explicitly specified
    if prog is None:
        prog = sys.argv[0]
    if args is None:
        args = sys.argv[1:]
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    if stdin is None:
        stdin = sys.stdin

    # make a local copy of args in case we were given an iterator
    args = tuple(args)

    # parse the command-line arguments
    arg_parser = ArgumentParser(prog=prog, stdout=stdout, stderr=stderr,
        stdin=stdin)
    try:
        app = arg_parser.parse_args(args=args)
    except arg_parser.Error as e:
        if e.exit_code == EXIT_SUCCESS:
            if e.args and e.args[0]:
                message = str(e).strip()
                if message:
                    print(message, file=stdout)
        elif e.exit_code == EXIT_ARGS:
            print("ERROR: invalid command-line arguments: {}".format(e),
                file=stderr)
            print("Run with --help for help", file=stderr)
        else:
            print("ERROR: {}".format(e), file=stderr)
        return e.exit_code
    else:
        del arg_parser # free the memory allocated by the argument parser

    # run the application
    try:
        app.run()
    except app.Error as e:
        print("ERROR: {}".format(e), file=stderr)
        return EXIT_ERROR

    return EXIT_SUCCESS

################################################################################

class BgrepApplication:
    """
    The bgrep application.
    """

    def __init__(self, pattern, paths=None, stdout=None, stdin=None,
            logger=None):
        """
        Initializes a new instance of this class.
        *pattern* must be a byte string whose value to search for.
        *paths* must be an iterable of strings whose values are the paths of the
        files to search; may be None (the default) to read input from *stdin*.
        *stdout* must be a file-like object opened in text mode to use as the
        standard output stream; may be None (the default) to use sys.stdout.
        *stdin* must be a file-like object opened in *binary* mode to use as the
        standard input stream; may be None (the default) to use
        sys.stdin.buffer.
        *logger* must be an instance of logging.Logger to which log messages
        are to be written; may be None (the default) to not emit log messages.
        """
        self.pattern = pattern
        self.paths = paths
        self.stdout = stdout
        self.stdin = stdin
        self.logger = logger


    def run(self):
        """
        Iterates over the paths in self.paths and reports to self.stdout any
        matches of the pattern self.pattern.
        Raises Error if an error occurs.
        """
        class MyFileIterator(FileIterator):
            def on_error(self, path, pattern, error):
                message = "unable to read {}: {}".format(path, error)
                self.log_warning(message)

        files = MyFileIterator(self.paths, self.stdin)
        buffer = None

        for file_info in files:
            f = file_info.f
            path = file_info.path
            pattern = file_info.pattern

            if path is None:
                path = "<standard input>"

            self.log_debug("Searching {}".format(path))
            try:
                buffer = self.search(f, path, buffer=buffer)
            except IOError as e:
                files.on_error(path, pattern, e)


    def search(self, f, path, buffer=None):
        """
        Searches the given file for this object's pattern.
        All matches that are found are reported via on_match_found().

        *f* file be a file object opened for binary read to search for this
        object's pattern.
        *path* must be a string whose value is the path of the given file.
        *buffer* must be a bytearray object that will be used as the read
        buffer; the first invocation of this method should specify None, in
        which case a buffer with a suitable size will be created, used, and
        returned; subsequent invocations should specify the returned buffer
        instead of None so that the existing buffer can be re-used.

        Any exceptions raised from reading from the given file are not caught
        or handled and must be handled by the caller; if the given file is a
        normal file object, then this means that the caller should catch and
        handle IOError.
        """

        # create the buffer if it has not been allocated yet
        # NOTE: don't use a larger buffer size because reading from stdin in
        # Windows will raise IOError if the buffer is too large... ugh
        if buffer is None:
            buffer_size = len(self.pattern) * 2
            if buffer_size < 16384:
                buffer_size = 16384
            buffer = bytearray(buffer_size)

        # read the bytes from the files and search for pattern matches
        size = f.readinto(buffer)
        while size > 0:
            last_match_end = -1

            # search for complete matches inside the chunk of bytes
            index = buffer.find(self.pattern, 0, size)
            while index >= 0:
                # extract the matching text, and some context, from the bytes
                s_end = index + len(self.pattern) + 20
                if s_end > size:
                    s_end = size
                s = buffer[index:s_end]
                self.on_match_found(path, s)

                # see if there are more matches in this line
                index += len(self.pattern)
                last_match_end = index
                index = buffer.find(self.pattern, index, size)

            # check for a partial match at the end of the bytes as the match
            # may span this chunk and the next chunk; if found, copy the
            # potentially-matching bytes to the beginning of the buffer and set
            # up the next read to write into the buffer after the potentially-
            # matching chunk; the last_match_end check is to fix the boundary
            # conditional where the last match detected above was exactly the
            # last chunk of bytes in the buffer
            next_read_buffer = buffer
            size_adjust = 0
            if last_match_end < size:
                check = self.pattern
                while check:
                    if buffer.endswith(check, 0, size):
                        buffer[0:len(check)] = buffer[size - len(check):size]
                        size_adjust = len(check)
                        next_read_buffer = memoryview(buffer)[size_adjust:]
                        break
                    check = check[:-1]

            # read the next chunk of bytes
            size = f.readinto(next_read_buffer)
            size += size_adjust

        # return the buffer so that the caller can re-use it in the future
        return buffer


    def log_warning(self, message):
        """
        Logs a warning message to self.logger.
        If self.logger is None then this method does nothing.
        """
        logger = self.logger
        if logger is not None:
            logger.warning("WARNING: {}".format(message))


    def log_debug(self, message):
        """
        Logs a debug message to self.logger.
        If self.logger is None then this method does nothing.
        """
        logger = self.logger
        if logger is not None:
            logger.debug(message)


    def on_match_found(self, path, s):
        stdout = self.stdout
        if stdout is None:
            stdout = sys.stdout

        # replace non-printable ASCII characters, except those that are part of
        # the pattern
        i = len(s) - 1
        while i >= len(self.pattern):
            if s[i] < 32 or s[i] > 126:
                s[i] = 32 # 32 is the ASCII code for space
            i -= 1

        print(s.decode("US-ASCII", errors="replace"), file=stdout)


    class Error(Exception):
        """
        Exception raised if an error occurs.
        """
        pass

################################################################################

class FileIterator:
    """
    Iterates over a list of paths, recursively walking directories and expanding
    glob wildcard patterns.
    """

    def __init__(self, paths=None, default=None):
        """
        Initializes a new instance of FileIterator.
        *paths* must be an iterable of strings whose values are the paths of the
        files and directories to return from the iterator; may be None (the
        default) which is treated exactly like an empty list of paths.
        *default* may be any object and will be returned if the given list of
        paths is either None or empty; if None (the default) then nothing will
        be returned if the given list of paths is None or empty.
        """
        self.paths = paths
        self.default = default


    def __iter__(self):
        """
        Iterates over the paths.
        """
        paths_is_empty = True

        # iterate over the list of paths
        if self.paths is not None:
            for path in self.paths:
                paths_is_empty = False
                for file_info in self._iter_pattern(path):
                    yield file_info

        # if the list of paths was empty then yield the default value, if given
        if paths_is_empty:
            default = self.default
            if default is not None:
                yield self.FileInfo(path=None, f=default, pattern=None)


    def on_error(self, path, pattern, error):
        """
        Invoked during iteration when an error occurs opening one of the paths.
        The default implementation of this method does nothing; subclasses
        may override to provide error reporting.
        *path* must be a string whose value is the path of the file that reading
        failed.
        *pattern* must be a string whose value is the elements of self.paths
        that caused the file with the given path to be read.
        *error* must be an instance of IOError or OSError describing the error
        that occurred.
        """
        pass


    def _iter_pattern(self, pattern):
        """
        Called during iteration to return the FileInfo objects corresponding
        to a given glob pattern.
        *pattern* must be a string whose value will be treated as a glob
        pattern; all matching files and files in all matching directories,
        recursively, will be yielded.
        """
        # perform the glob pattern matching
        glob_matches = glob.iglob(pattern)

        # make sure there is at least one match
        try:
            first_match = next(glob_matches)
        except StopIteration:
            error = IOError("file or directory not found: {}".format(pattern))
            self.on_error(pattern, pattern, error)
            return

        # iterate over each matching path
        for match in itertools.chain([first_match], glob_matches):
            for file_path in self._walk(match):
                try:
                    f = open(file_path, "rb")
                    try:
                        yield self.FileInfo(file_path, f, match)
                    finally:
                        f.close()
                except IOError as e:
                    self.on_error(file_path, match, e)


    def _walk(self, path):
        """
        Similar to os.walk(), except that if the given path is a file then
        only that file is returned; otherwise, the directory is walked using
        os.walk().
        """
        if os.path.isfile(path):
            yield path
        else:
            def walk_onerror(e):
                self.on_error(e.filename, path, e)
            walk_results = os.walk(path, onerror=walk_onerror)
            for (dirpath, dirnames, filenames) in walk_results:
                for filename in filenames:
                    yield os.path.join(dirpath, filename)


    class FileInfo:
        """
        Stores information about a file returned from this iterator.
        """

        def __init__(self, path, f, pattern):
            """
            Initializes a new instance of FileInfo.
            *path* must be a string whose value is the path of the file;
            may be None, which indicates that this file corresponds to the
            default value.
            *f* must be a file object opened in binary read mode that
            corresponds to the given path, or is the default value if path
            is None; the creator of this object is responsible for closing
            this file, unless it is the default value, which will not be closed.
            *pattern* must be a string whose value is the actual value from the
            paths that caused this object to be created; for example, if a
            directory was given in the paths in which this file resides then
            *path* will be the path of the file and *pattern* will be the
            directory that was given in the list of paths; may be None, which
            indicates that this file corresponds to the default value.
            """
            self.path = path
            self.f = f
            self.pattern = pattern

################################################################################

class ArgumentParser(argparse.ArgumentParser):
    """
    Parses the command-line arguments for the bgrep application.
    """

    USAGE = "%(prog)s [options] <pattern> [path [path ...]]"

    def __init__(self, prog=None, stdout=None, stderr=None, stdin=None):
        """
        Initializes a new instance of MyArgumentParser.
        *prog* must be a string whose value is the name of the program to
        present to the user; may be None (the default) to have the superclass
        choose an appropriate default.
        *stdout* must be a file-like object opened in text mode to use as the
        standard output stream; may be None (the default) to use a stream chosen
        by each use, which is usually sys.stdout.
        *stderr* must be a file-like object opened in text mode to use as the
        standard output stream; may be None (the default) to use a stream chosen
        by each use, which is usually sys.stderr.
        *stdin* must be a file-like object opened in text mode to use as the
        standard input stream; may be None (the default) to use a stream chosen
        by each use, which is usually sys.stdin.
        """
        super().__init__(prog=prog, usage=self.USAGE)
        self.stdout = stdout
        self.stderr = stderr
        self.stdin = stdin
        self.default_log_level = logging.INFO
        self._add_arguments()


    def _add_arguments(self):
        """
        Adds the arguments to this object.
        """

        self.add_argument("pattern",
            help="""The string to search for. This string will be converted to
            bytes using ASCII encoding and the resulting byte string will be
            searched for in the given paths."""
        )

        self.add_argument("paths",
            nargs="*",
            help="""The paths of the files and/or directories to search.
            Unix glob patterns, such as "*", "?", and "[...]", are recognized.
            Directories will be searched, recursively.
            If no paths are specified then standard input is used.
            """
        )

        self.add_argument("--version",
            action="version",
            version=VERSION,
            help="""Print the version of this application and exit."""
        )

        log_group = self.add_argument_group("Logging Options")

        arg_log_level_verbose = log_group.add_argument("-v", "--verbose",
            dest="log_level",
            action="store_const",
            const=logging.DEBUG,
            help="""Set the log level to "verbose", which causes a great deal
            of extra information to be logged to standard error."""
        )

        arg_log_level_quiet = log_group.add_argument("-q", "--quiet",
            dest="log_level",
            action="store_const",
            const=logging.WARNING,
            help="""Set the log level to "warning", which causes only warning
            messages to be logged to standard error."""
        )

        other_log_levels = []
        for option in (arg_log_level_verbose, arg_log_level_quiet):
            other_log_levels.extend(option.option_strings)
        other_log_levels_str = ", ".join(other_log_levels)

        arg_log_level_normal = log_group.add_argument("--log-level-normal",
            dest="log_level",
            action="store_const",
            const=self.default_log_level,
            help="""Set the log level to "default"; the primary purpose of this
            argument is to override any previous specification of {}."""
            .format(other_log_levels_str)
        )


    def parse_args(self, args):
        """
        Parses the given line arguments.
        *args* must be an iterable of strings whose values are the arguments
        to parse; may be None (the default) to use the default value chosen by
        the superclass.
        Returns a newly-created instance of BgrepApplication that, when run,
        will behave in the manner described by the given arguments.
        Raises Error if parsing the given arguments fails.
        """
        if args is not None:
            args = tuple(args) # create a local copy
        namespace = self.Namespace()
        super().parse_args(args=args, namespace=namespace)
        app = namespace.create_application(parser=self)
        return app


    def exit(self, status=EXIT_SUCCESS, message=None):
        """
        Overrides the exit behaviour defined in the superclass to instead raise
        Error using the given *message* and *status* as the *message* and
        *exit_code* parameters to the exception's initializer, respectively.
        """
        raise self.Error(message=message, exit_code=status)


    def error(self, message):
        """
        Overrides the error behaviour defined in the superclass to instead
        invoke exit() with status=EXIT_ARGS and the given message, which will
        raise Error with these values.
        """
        self.exit(status=EXIT_ARGS, message=message)


    def print_help(self):
        """
        Overrides the print_help behaviour defined in the superclass to print
        to the stdout stream given to __init__() instead of sys.stdout.
        """
        super().print_help(file=self.stdout)


    class Namespace(argparse.Namespace):
        """
        The custom Namespace used when parsing arguments.
        """

        def create_application(self, parser):
            """
            Creates and returns a new instance of BgrepApplication based on the
            given arguments.
            *parser* must be an instance of ArgumentParser, whose attributes
            may be used when creating the application.
            """
            pattern = self.pattern.encode("US-ASCII", errors="ignore")
            paths = self.paths
            log_level = self.log_level
            if log_level is None:
                log_level = parser.default_log_level
            stdout = parser.stdout
            stdin = parser.stdin
            if stdin is not None:
                stdin = stdin.buffer # use the underlying binary stream

            logger = logging.getLogger()
            logger.setLevel(log_level)

            return BgrepApplication(
                pattern=pattern,
                paths=paths,
                stdout=stdout,
                stdin=stdin,
                logger=logger,
            )


    class Error(Exception):
        """
        Exception raised when parsing the arguments fails.
        """

        def __init__(self, message, exit_code):
            """
            Initializes a new instance of this class.
            *message* must be a string whose value is a message for this object.
            *exit_code* must be an integer equal to one of EXIT_SUCCESS,
            EXIT_ERROR, or EXIT_ARGS, and will be stored in the *exit_code*
            attribute of this object.
            """
            super().__init__(message)
            self.exit_code = exit_code

################################################################################

if __name__ == "__main__":
    try:
        exit_code = main(prog="bgrep")
    except KeyboardInterrupt:
        print("ERROR: application terminated by keyboard interrupt",
            file=sys.stderr)
        exit_code = 1
    sys.exit(exit_code)
