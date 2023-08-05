#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The PyGTK Shell provides widgets derived from PyGTK optimized for
interactive programming as well as an interactive, extensible PyGTK console
for the rapid prototyping of GUI applications.  It can be embedded by PyGTK
applications.
"""

# Copyright (C) 2007  Felix Rabe <public@felixrabe.textdriven.com>

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

from PyGTKShell.Core import pygtkshell_version

from distutils.core import setup

setup(
        name = "pygtk-shell",
        version = ".".join(map(str, pygtkshell_version)),
        description = "Framework for interactive GUI programming",
        long_description = __doc__.strip(),
        author = "Felix Rabe",
        author_email = "public@felixrabe.textdriven.com",
        url = "http://felixrabe.textdriven.com/pygtk-shell/",
        packages = [
            "PyGTKShell",
            ],
        scripts = [],
        license = "GNU General Public License (GPL) >= 2",
      )

