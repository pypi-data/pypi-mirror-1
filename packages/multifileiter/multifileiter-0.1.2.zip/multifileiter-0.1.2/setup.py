# Copyright (c) 2010 Gabriel A. Genellina
# Licensed under the MIT License. See license.txt for details.

from distutils.core import setup, Extension
import multifileiter

long_description = multifileiter.__doc__
description = long_description.split('\n\n', 1)[0].strip()
assert len(description)>80

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Programming Language :: C",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Text Processing :: Filters",
    "Environment :: Console",
    ]

setup(name="multifileiter",
      version=multifileiter.__version__,
      description=description,
      long_description=long_description,
      author=multifileiter.__author__,
      author_email=multifileiter.__author_email__,
      url='http://code.google.com/p/multifileiter/',
      classifiers = classifiers,
      license="MIT License",
      packages = ['multifileiter'],
      ext_modules=[
         Extension("multifileiter._multifile", ["multifileiter/_multifile.c"]),
         ])
