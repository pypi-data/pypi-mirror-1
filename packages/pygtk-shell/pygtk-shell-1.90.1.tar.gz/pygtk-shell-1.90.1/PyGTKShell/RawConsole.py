#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyGTK Shell minimal Raw Console.
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

from PyGTKShell.API import *


class CodeView(
        GtkTextViewUserExecMixin,
        TextViewForCode,
        ): pass

class OutputView(
        TextViewForCode,
        ): pass


class RawConsole(VPaned):
    """
    Raw console for interactively executing Python code.
    """

    def __init__(self, *a, **kw):
        super(RawConsole, self).__init__(*a, **kw)
        self.code_view = self(ScrolledWindow())(CodeView())
        self.output_view = self(ScrolledWindow())(OutputView())
        self.output_view.set_editable(False) # to avoid potential confusion
        self.code_view.textview_userexec_namespace["console"] = self


class RawConsoleCenterInit(RawConsole):
    """
    Raw console whose initial VPaned position is in the middle.
    """

    def __init__(self, *a, **kw):
        super(RawConsoleCenterInit, self).__init__(*a, **kw)
        def f(self):
            self.set_position(self.get_allocation().height / 2)
            return False
        gobject.idle_add(f, self, priority = gobject.PRIORITY_LOW)


class RawConsoleWithIntro(RawConsoleCenterInit):
    """
    Raw console running an example script on initialization.
    """

    def __init__(self, *a, **kw):
        super(RawConsoleWithIntro, self).__init__(*a, **kw)
        buf = self.code_view.get_buffer()
        msg = a_("Press F5 or Ctrl+E to execute this code.")
        buf('# -*- coding: utf-8 -*-\n' +
            '# %s\n' % msg +
            'from PyGTKShell.API import *\n' +
            'o = console.output_view.get_buffer()\n'
            'o(str(dir()))\n')
        self.code_view.do_userexec()
        buf.select_range(*buf.get_bounds())

