#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyGTK Shell Core.
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


pygtkshell_version = (1,90,1)

import gtk
import gtk.keysyms
import gobject
import pango

import gettext
# "a_" is used instead of plain "_" because Core gets * imported by API
# and API gets * imported by users.  But "_" can't be imported anyway...
a_ = gettext.translation("pygtkshell", fallback = True).gettext

