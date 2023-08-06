# Copyright (c) 2010 Gabriel A. Genellina
# Licensed under the MIT License. See license.txt for details.

"""
An iterator over all lines of the given files. Like module `fileinput` in 
the standard library, but faster, and written in C.

Unlike `fileinput`, input files are *not* completely read into memory;
it can handle files of any size.

In addition, a replacement for the standard fileinput.FileInput 
legacy class is provided.

This package has no external dependencies. It has been tested in Python 2.6;
support for Python 3.1 is still experimental.
"""

__version__ = '0.1.2'
__author__ = 'Gabriel Genellina'
__author_email__ = 'ggenellina@yahoo.com.ar'
