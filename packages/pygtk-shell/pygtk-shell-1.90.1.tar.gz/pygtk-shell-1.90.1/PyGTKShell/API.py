#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyGTK Shell API providing simplified GObject and GTK classes.
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


from PyGTKShell.Core import *
from PyGTKShell.Utilities import *
from PyGTKShell.Mixins import *


### ABSTRACT BASE CLASSES:

class Widget(
        GtkWidgetAutoShowMixin,
        gtk.Widget,
        ): pass

class Container(
        Widget,
        GtkContainerAddByCallingMixin,
        gtk.Container,
        ): pass

class Box(
        Container,
        GtkBoxPythonicMixin,
        gtk.Box,
        ): pass

class Paned(
        Container,
        gtk.Paned,
        ): pass

class ToolItem(
        Container,
        gtk.ToolItem,
        ): pass


### SEMI-ABSTRACT BASE CLASSES:

class Window(
        Container,
        GtkWindowFullScreenKeyMixin,
        GtkWindowLastQuitMixin,
        gtk.Window,
        ): pass

class Dialog(
        # Make sure there is no trace of GtkWidgetAutoShowMixin in here!
        # The dialog should only .show() when it is .run()
        GtkContainerAddByCallingMixin,
        GtkWindowLastQuitMixin,
        GtkDialogRunSimplifiedMixin,
        gtk.Dialog,
        ): pass

class FileChooserDialog(
        Dialog,
        gtk.FileChooserDialog,
        ): pass


### SPECIFIC CLASSES:

class Button(
        Widget,
        gtk.Button,
        ): pass

class CheckButton(
        Widget,
        gtk.CheckButton,
        ): pass

class DrawingArea(
        Widget,
        gtk.DrawingArea,
        ): pass

class Entry(
        Widget,
        GtkEntryActivatesDefaultMixin,
        gtk.Entry,
        ): pass

class EventBox(
        Container,
        gtk.EventBox,
        ): pass

class FileChooserButton(
        Container,
        gtk.FileChooserButton,
        ): pass

class FileChooserDialogStandard(
        FileChooserDialog,
        GtkFileChooserDialogStandardMixin,
        gtk.FileChooserDialog,
        ): pass

class HBox(
        Box,
        gtk.HBox,
        ): pass

class HPaned(
        Paned,
        gtk.HPaned,
        ): pass

class ImageMenuItem(
        Container,
        gtk.ImageMenuItem,
        ): pass

class Label(
        Widget,
        gtk.Label,
        ): pass

class MarkupLabel(
        Widget,
        GtkLabelUsingMarkupMixin,
        gtk.Label,
        ): pass

class Menu(
        Container,
        gtk.Menu,
        ): pass

class MenuBar(
        Container,
        gtk.MenuBar,
        ): pass

class MenuItem(
        Container,
        gtk.MenuItem,
        ): pass

class MessageDialog(
        Dialog,
        gtk.MessageDialog,
        ): pass

class Notebook(
        Container,
        gtk.Notebook,
        ): pass

class RadioButton(
        Widget,
        gtk.RadioButton,
        ): pass

class ScrolledWindow(
        Container,
        GtkScrolledWindowPolicyAutoMixin,
        gtk.ScrolledWindow,
        ): pass

class SeparatorMenuItem(
        Container,
        gtk.SeparatorMenuItem,
        ): pass

class Table(
        Container,
        GtkTableSimplifiedMixin,
        gtk.Table,
        ): pass

class TextBuffer(
        GtkTextBufferCallableMixin,
        gtk.TextBuffer,
        ): pass

class TextView(
        Container,
        GtkTextViewAPITextBufferMixin,
        gtk.TextView,
        ): pass

class TextViewForCode(
        Container,
        GtkTextViewAPITextBufferMixin,
        GtkTextViewForCodeMixin,
        gtk.TextView,
        ): pass

class Toolbar(
        Container,
        gtk.Toolbar,
        ): pass

class ToolButton(
        ToolItem,
        gtk.ToolButton,
        ): pass

class TreeView(
        Container,
        gtk.TreeView,
        ): pass

class VBox(
        Box,
        gtk.VBox,
        ): pass

class VPaned(
        Paned,
        gtk.VPaned,
        ): pass

