.. include:: rststuff.txt

=============
multifileiter
=============

An extension module, written in C, that implements an iterator over all lines 
of the given files. Like module :mod:`fileinput` in the standard library, but faster.


Installation
============

Extract the source distribution in some temporary directory, and execute::

    python setup.py build
    python setup.py install

It uses the very same test suite as the standard :mod:`fileinput` module. To run
the tests::

    cd test
    python test_multifileiter.py


Usage
=====

This package implements a basic multiple file iterator in C, a thin 
wrapper in Python on top of it, and a replacement for the standard 
:class:`fileinput.FileInput` class.

Example::

    from multifileiter.fileinput import FileInput
    
    fi = FileInput(list_of_file_names)
    # iterate over every line in every file
    for line in fi: 
        process_line(line)

If you want to rewrite the input files with new content::

    fi = FileInput(list_of_file_names, inplace=True)
    for line in fi: 
        new_line = process_line(line)
        fi.output.write(new_line)

The :attribute:`output` attribute points to the currently written file. If you
want the legacy :class:`FileInput` behavior (printing or writing to ``sys.stdout`` 
goes to the output file) use *replace_stdout=True*.


Replacing the :mod:`fileinput` standard module 
----------------------------------------------

Class :class:`LegacyFileInput` implements the same interface as the standard library's 
:class:`FileInput`. You may monkey-patch the standard :mod:`fileinput` module 
to gain the speed of the new module without modifying any legacy code. 
Just execute this at the start of your program::

    # monkey-patch stdlib's fileinput 
    import multifileiter.fileinput
    import fileinput
    fileinput.FileInput = multifileiter.fileinput.LegacyFileInput

.. note::

    In addition to the :class:`FileInput` class, the :mod:`fileinput` standard module
    exposes many global functions. Using those global functions with 
    this version of :class:`FileInput` may work, or may not. I don't like its 
    global nature, they were never tested with this module, and using 
    them is not supported. Use at your own risk.


Reference
=========

**class multifileiter.fileinput.MultiFileIter** (files=None, mode="r")

    *files* is any iterable yielding either strings 
    or file-like objects. The iterable is consumed lazily. 
    Strings are considered file names and the corresponding file 
    is opened using the *mode* parameter.  The string ``'-'`` is 
    special-cased and represents ``sys.stdin``.   Other objects are assumed
    to be file-like objects; only their :method:`next()`, :method:`name()` and :method:`close()`
    methods are called (the latter two being optional).

    :class:`MultiFileIter` implements the iterator protocol. :method:`next()` returns
    each line from its input files.


:class:`MultiFileIter` objects have these methods:

:method:`lineno()`
    Cumulative line number of the line that has just been read, or 0 before reading the first line.

:method:`filelineno()`
    Line number of the line that has just been read, in the current file.

:method:`isfirstline()`
    True if the line that has just been read is the first line in the file, false otherwise.

:method:`filename()`
    Name of the file currently being read, or ``None``.

:method:`isstdin()`
    True if the line just read came from stdin, false otherwise.

:method:`fileno()`
    File descriptor of the current file, or -1 when no file is opened.

:method:`nextfile()`
    Closes the current file. The next iteration will read the first line from the next file (if any).

:method:`close()`
    Close the input file, the output file (if any) and exits the whole iteration.


**class multifileiter.fileinput.FileInput** (files=None, inplace=0, backup="", mode="r", openhook=None, replace_stdout=False)

    :class:`FileInput` extends :class:`MultiFileIter`, adding support for
    writing files.

    *files* and *mode* are passed to the base class.

    When *inplace* is true, the input files are renamed,
    and a new file of the same name is created for writting 
    (it may be accessed thru the :attribute:`output` property). In addition, 
    if *replace_stdout* is true, standard output (``sys.stdout``) is 
    redirected to that file too.

    *backup* is the extension added to the original file names; 
    ``'.bak'`` is used if not specified.

    *openhook* is a function used instead of the builtin :function:`open` function
    to open the files; it must take two positional arguments, 
    *filename* and *mode*. 


:class:`FileInput` objects have these attributes:

:attribute:`output`

    The file currently being written (or ``None`` when *inplace* is false)

