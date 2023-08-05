#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyGTK Shell - enhanced traceback module.
"""

# Copyright (C) 2006 - 2007  Felix Rabe <public@felixrabe.textdriven.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import linecache
import sys
from traceback import *
from traceback import _print

def print_tb(tb, limit=None, file=None):
    """Print up to 'limit' stack trace entries from the traceback 'tb'.

    If 'limit' is omitted or None, all entries are printed.  If it is
    negative, that (negated) many stack entries will be omitted.  If
    'file' is omitted or None, the output goes to sys.stderr; otherwise
    'file' should be an open file or file-like object with a write()
    method.
    """
    if file is None:
        file = sys.stderr
    if limit is None:
        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit
    n = 0
    output_chunks = []
    while tb is not None:
        f = tb.tb_frame
        lineno = tb.tb_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        output_chunks.append(
               '  File "%s", line %d, in %s' % (filename,lineno,name))
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno)
        if line: output_chunks[-1] += '\n    ' + line.strip()
        tb = tb.tb_next
        n += 1
    if limit is None:
        limit = n
    if limit < 0:
        output_chunks[:-limit] = []
    else:
        output_chunks[limit:] = []
    for chunk in output_chunks:
        _print(file, chunk)

import traceback
traceback.print_tb = print_tb
