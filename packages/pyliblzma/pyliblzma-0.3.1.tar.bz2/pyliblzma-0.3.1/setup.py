#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python Bindings for libLZMA
#
# Copyright (c) 2008 Per Øyvind Karlsen <peroyvind@mandriva.org>
# liblzma Copyright (C) 2007-2008  Lasse Collin
# LZMA SDK Copyright (C) 1999-2007 Igor Pavlov
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import sys, os
from warnings import warn
from setuptools import setup, Extension

descr = "Python bindings for liblzma"
long_descr = """PylibLZMA provides a python interface for the liblzma library
to read and write data that has been compressed or can be decompressed
by Lasse Collin's lzma utils."""
version = '0.3.1'
version_define = [('VERSION', '"%s"' % version)]

# FIXME: Probably some nicer way to do this
if 'sdist' in sys.argv:
    os.system('git log . > ChangeLog')
c_files = ['liblzma.c', 'liblzma_compressobj.c', 'liblzma_decompressobj.c', 'liblzma_options.c']
optflags = ['-O3', '-funroll-loops']
# Just for fun..
warnflags = ['-Wall', '-Wextra', '-Wdeclaration-after-statement', '-Wstrict-prototypes', '-pedantic', '-Wformat-y2k', '-Wformat-nonliteral', '-Wformat-security', '-Wformat=2', '-Winit-self', '-Wswitch-enum', '-Wunused-label', '-Wunused-parameter', '-Wunused-variable', '-Wunused', '-Wstrict-overflow=5', '-Wfloat-equal', '-Wunreachable-code', '-Wnested-externs', '-Wvariadic-macros', '-Wdisabled-optimization', '-Wundef', '-Wshadow', '-Wbad-function-cast', '-Wunsafe-loop-optimizations', '-Wunused-macros', '-Wendif-labels', '-Wvolatile-register-var', '-Wlong-long', '-Winvalid-pch', '-Winline', '-Wpacked', '-Wmissing-format-attribute', '-Wmissing-noreturn', '-Wmissing-declarations', '-Wmissing-prototypes', '-Wold-style-definition', '-Waggregate-return', '-Wcast-qual', '-Wcast-align', '-Wc++-compat', '-Wbad-function-cast'] # '-Wconversion']
compile_args = ['-std=c99']
compile_args.extend(warnflags)
compile_args.extend(optflags)
link_args = ['-llzma']
extens=[Extension('liblzma', c_files, extra_compile_args=compile_args, extra_link_args=link_args, define_macros=version_define)]

setup(
    name = "pyliblzma",
    version = version,
    description = descr,
    author = "Per Øyvind Karlsen",
    author_email = "peroyvind@mandriva.org",
    url = "http://lzmautils.sourceforge.net",
    license = 'LGPL 3 ',
    keywords = "lzma compression",
    long_description = long_descr,
    platforms = sys.platform,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL) 3',
        'Operating System :: POSIX :: Linux'
    ],
    ext_modules = extens,
    test_suite = 'tests',
)

sys.exit(0)
