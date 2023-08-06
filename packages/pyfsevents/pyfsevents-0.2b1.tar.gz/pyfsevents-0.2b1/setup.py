"""
setup.py - Setup script for pyfsevents

Copyright 2009 Nicolas Dumazet <nicdumz@gmail.com>

This library is free software; you can redistribute it and/or
modify it under the terms of the MIT License.
"""
from distutils.core import setup, Extension
from distutils.command.build_ext import build_ext as _build_ext
import os

def read(fname):
    return open(fname).read()

class build_ext(_build_ext):
    "Extend build_ext to add a --noopt option"
    user_options = _build_ext.user_options + [('noopt', None,
                                              'no binary optimization')]
    boolean_options = _build_ext.boolean_options + ['noopt']

    def initialize_options(self):
        self.noopt = None
        _build_ext.initialize_options(self)

    def build_extension(self, ext):
        if self.noopt:
            ext.extra_compile_args.append('-O0')
        _build_ext.build_extension(self, ext)

ext_modules = [
    Extension(name = 'pyfsevents',
              sources = ['pyfsevents.c'],
              extra_link_args = ["-framework","CoreFoundation",
                               "-framework","CoreServices"],
             ),
    ]


setup(name = 'pyfsevents',
      version = "0.2b1",
      description = "Low level interface to FSEvents primitives",
      long_description = read('readme.rst'),
      license = "MIT",
      url = "http://bitbucket.org/nicdumz/fsevents/",
      download_url = "http://bitbucket.org/nicdumz/fsevents/",

      author = "Nicolas Dumazet",
      author_email = "nicdumz@gmail.com",

      cmdclass = dict(build_ext=build_ext),
      ext_modules = ext_modules,

      platforms = ["Mac OS X"],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: C',
        'Programming Language :: Python :: 2.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Filesystems',
      ],
     )
