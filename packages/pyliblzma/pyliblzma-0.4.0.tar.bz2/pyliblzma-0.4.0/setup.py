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
version = '0.4.0'
version_define = [('VERSION', '"%s"' % version)]

# FIXME: Probably some nicer way to do this
if 'sdist' in sys.argv:
    os.system('bzr log . > ChangeLog')
modules = ['liblzma']
c_files = ['liblzma.c', 'liblzma_compressobj.c', 'liblzma_decompressobj.c', 'liblzma_file.c', 'liblzma_fileobj.c', 'liblzma_options.c', 'liblzma_util.c']

warnflags = ['-Wall', '-Wextra', '-pedantic']
compile_args = []
if not os.popen4('touch gnu99-test.c; gcc -std=gnu99 -E gnu99-test.c > /dev/null; rm -f gnu99-test.c')[1].read():
    compile_args.append('-std=gnu99')

link_args = ['-llzma']
extens=[Extension('lzma', c_files, extra_compile_args=compile_args, extra_link_args=link_args, define_macros=version_define)]

setup(
    name = "pyliblzma",
    version = version,
    description = descr,
    author = "Per Øyvind Karlsen",
    author_email = "peroyvind@mandriva.org",
    url = "https://launchpad.net/pyliblzma",
    license = 'LGPL 3 ',
    keywords = "lzma compression",
    long_description = long_descr,
    platforms = sys.platform,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: POSIX :: Linux'
    ],
    py_modules = modules,
    ext_modules = extens,
    test_suite = 'tests',
)

sys.exit(0)
