# $Id: fileinput.py 3 2010-01-15 15:53:13Z ggenellina $

import sys
import os
from . import _multifile

class MultiFileIter(_multifile.MultiFileIter):
    "An iterator over all lines of the given files"

    _lineno_at_start = 0

    def __init__(self, files=None, mode="r"):
        if isinstance(files, basestring):
            files = (files,)
        else:
            if files is None:
                files = sys.argv[1:]
            if not files:
                files = ('-',)
            else:
                files = tuple(files)
        if mode not in ('r', 'rU', 'U', 'rb'):
            raise ValueError("FileInput opening mode must be one of "
                             "'r', 'rU', 'U' or 'rb'")
        files = (self._prepare_next_file(fn, mode) for fn in files)
        _multifile.MultiFileIter.__init__(self, files, mode)

    def _prepare_next_file(self, file_or_name, mode):
        self._lineno_at_start = self.lineno()
        if file_or_name == '-':
            return file_or_name
        if isinstance(file_or_name, basestring):
            return self._open_file(file_or_name, mode)
        return file_or_name

    def _open_file(self, filename, mode):
        return open(filename, mode)

    def filelineno(self):
        """Number of the line that has just been read, in the current file."""
        return self.lineno() - self._lineno_at_start

    def isfirstline(self):
        """True if the line that has just been read is the first line in the file, false otherwise."""
        return self.filelineno() == 1


class _delegate_output:
    def __init__(self, fileinput):
        self._fileinput = fileinput
    def __getattr__(self, name):
        return getattr(self._fileinput.output, name)


class FileInput(MultiFileIter):
    """An iterator over all lines of the given files with
    an interface similar to fileinput.FileInput in the
    standard library"""

    _savestdout = None
    _output = None

    def __init__(self, files=None, inplace=0, backup="", bufsize=0,
                 mode="r", openhook=None, replace_stdout=False):
        self.inplace = inplace
        self.backup = backup
        # bufsize is ignored
        if inplace and openhook:
            raise ValueError("FileInput cannot use an opening hook in inplace mode")
        elif openhook and not hasattr(openhook, '__call__'):
            raise ValueError("FileInput openhook must be callable")
        self.openhook = openhook
        if not inplace and replace_stdout:
            raise ValueError("replace_stdout requires inplace=True")
        self.replace_stdout = replace_stdout
        if inplace:
            self.output = sys.stdout
            if replace_stdout:
                self._savestdout = sys.stdout
                sys.stdout = _delegate_output(self)
        return MultiFileIter.__init__(self, files, mode)

    def _open_file(self, filename, mode):
        # Taken from the standard fileinput.py
        if self.inplace:
            backupfilename = filename + (self.backup or os.extsep+"bak")
            try: os.unlink(backupfilename)
            except os.error: pass
            # The next few lines may raise IOError
            os.rename(filename, backupfilename)
            file = open(backupfilename, mode)
            try:
                perm = os.fstat(file.fileno()).st_mode
            except OSError:
                self.output = open(filename, "w")
            else:
                fd = os.open(filename,
                             os.O_CREAT | os.O_WRONLY | os.O_TRUNC,
                             perm)
                self.output = os.fdopen(fd, "w")
                try:
                    if hasattr(os, 'chmod'):
                        os.chmod(filename, perm)
                except OSError:
                    pass
        else:
            # This may raise IOError
            if self.openhook:
                file = self.openhook(filename, mode)
            else:
                file = open(filename, mode)
        return file

    def close(self):
        if self.inplace:
            self.output = None
            if self.replace_stdout:
                sys.stdout = self._savestdout
        MultiFileIter.close(self)

    def _get_output(self):
        return self._output

    def _set_output(self, output):
        if self._output and self._output is not self._savestdout:
            self._output.close()
        self._output = output

    output = property(_get_output, _set_output)


class LegacyFileInput(FileInput):
    """A faster replacement of fileinput.FileInput
    keeping its legacy interface
    """
    def __init__(self, files=None, inplace=0, backup="", bufsize=0,
                 mode="r", openhook=None):
        FileInput.__init__(self, files, inplace=inplace,
            backup=backup, mode=mode,
            openhook=openhook, replace_stdout=inplace)

    def readline(self):
        try: return next(self)
        except StopIteration: return ''

    def __getitem__(self, i):
        if i != self.lineno():
            raise RuntimeError, "accessing lines out of order"
        try:
            return next(self)
        except StopIteration:
            raise IndexError
