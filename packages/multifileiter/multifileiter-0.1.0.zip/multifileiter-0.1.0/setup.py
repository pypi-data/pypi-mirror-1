from distutils.core import setup, Extension
import multifileiter

long_description = multifileiter.__doc__
description = long_description.split('\n\n', 1)[0].strip()
assert len(description)>80

setup(name="multifileiter",
      version=multifileiter.__version__,
      description=description,
      long_description=long_description,
      author=multifileiter.__author__,
      author_email=multifileiter.__author_email__,
      url='http://sleipnir.com.ar/multifileiter/',
      classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: C",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Filters",
        "Environment :: Console",
      ],
      license="Python Software Foundation License",
      packages = ['multifileiter'],
      ext_modules=[
         Extension("multifileiter._multifile", ["multifileiter/_multifile.c"]),
         ])
