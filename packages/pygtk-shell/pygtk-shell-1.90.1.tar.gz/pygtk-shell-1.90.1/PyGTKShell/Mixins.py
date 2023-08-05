#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyGTK Shell GObject / GTK Mixin Classes.
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


# Safely remove those classes in 1.91.x or later if they are not necessary.

# class GObjectAutoRegTypeMeta(gobject.GObjectMeta):
#     """
#     Metaclass of GObjectRegTypeMixin.
#     
#     Automatically registers new classes using gobject.type_register(),
#     except the GObjectAutoRegTypeMixin class itself.
#     """
#     
#     def __init__(cls, name, bases, cls_dict):
#         super(GObjectAutoRegTypeMeta, cls).__init__(name, bases, cls_dict)
#         if name == "GObjectAutoRegTypeMixin": return
#         gobject.type_register(cls)
# 
# 
# class GObjectAutoRegTypeMixin(gobject.GObject):
#     """
#     Automatically registers derived classes using gobject.type_register().
#     
#     The simple implementation is in the metaclass, GObjectAutoRegTypeMeta.
#     """
#     
#     __metaclass__ = GObjectAutoRegTypeMeta


class GtkBoxPythonicMixin(gtk.Box):
    """
    Box gets a "pythonic" attribute that represents the Box' children as a
    mutable sequence.
    """
    
    class __PythonicAttribute(object):
        
        def __init__(self, gtk_box):
            self.gtk_box = gtk_box
            self.__gc = self.gtk_box.get_children
        
        def __len__(self):
            return len(self.__gc())
        
        def __getitem__(self, slice_):
            return self.__gc()[slice_]
        
        def __setitem__(self, slice_, item):
            if isinstance(slice_, slice):
                if slice_.step is not None:
                    raise ValueError, "no support for extended slices"
            del self[slice_]
            if not hasattr(item, "__getitem__"): # no sequence
                item = [item]
            for i in item:
                self.append(i)
        
        def __delitem__(self, slice_):
            items = self[slice_]
            if not hasattr(items, "__getitem__"):
                items = [items]
            for x in items:
                self.remove(x)
        
        def __iter__(self):
            return iter(self.__gc())
        
        def __repr__(self):
            return repr(self.__gc())
        
        def __str__(self):
            return str(self.__gc())
        
        def append(self, child, expand = False, fill = False, padding = 0):
            # Defaults are all False because this class is probably used
            # more for list-like Boxes with a larger number of children.
            self.gtk_box.pack_start(child, expand, fill, padding)
            return child
        
        __call__ = append
        
        def __iadd__(self, items):
            for item in items: self.append(item)
        
        extend = __iadd__
        
        def index(self, x, start = None, stop = None):
            if start is None: start = 0
            if stop is None: stop = len(self)
            index = start
            while index < stop:
                if self[index] == x: return index
                index += 1
            raise ValueError, "x not in list"
        
        def insert(self, index, x):
            self.append(x)
            self.gtk_box.reorder_child(x, index)
            return x
        
        def pop(self, i = -1):
            x = self[i]
            del self[i]
            return x
        
        def remove(self, x):
            self.gtk_box.remove(x)
        
        def reverse(self):
            for (i, x) in enumerate(self.__gc()[::-1]):
                self.gtk_box.reorder_child(x, i)
    
    def __init__(self, *a, **kw):
        super(GtkBoxPythonicMixin, self).__init__(*a, **kw)
        self.pythonic = GtkBoxPythonicMixin.__PythonicAttribute(self)


class GtkContainerAddByCallingMixin(gtk.Container):
    """
    Container adds another Widget when called.
    
    Directly supported base classes:
    - gtk.Box
    - gtk.Container
    - gtk.Paned
    - gtk.Table
    - gtk.ScrolledWindow
    
    See also the __class_to_function_mapping class variable.
    """
    
    def __init__(self, *a, **kw):
        class_to_method_mapping = (
            # Specific widgets need to be specified first.
            (gtk.Dialog,            self.__add_to_Dialog),
            (gtk.MenuShell,         self.__add_to_MenuShell),
            (gtk.Notebook,          self.__add_to_Notebook),
            (gtk.Paned,             self.__add_to_Paned),
            (gtk.ScrolledWindow,    self.__add_to_ScrolledWindow),
            (gtk.Table,             self.__add_to_Table),
            (gtk.Toolbar,           self.__add_to_Toolbar),
            
            (gtk.Box,               self.__add_to_Box),
            
            (gtk.Container,         self.__add_to_Container),
        )
        
        # This is done before super.__init__() so it can __call__().
        for (Cls, method) in class_to_method_mapping:
            if isinstance(self, Cls):
                self.__call_method = method
                break
        else:
            raise Exception, "Illegal subclassing"
        
        super(GtkContainerAddByCallingMixin, self).__init__(*a, **kw)
    
    def __call__(self, child, *a, **kw):
        """
        Adds and returns the given child widget.
        """
        new_child = self.__call_method(child, *a, **kw)
        if new_child is not None:  # child replaced
            child = new_child
        return child
    
    def __add_to_Box(self, child, *a, **kw):
        use_pack_end = kw.pop("pack_end", False)
        pack = self.pack_start
        if use_pack_end: pack = self.pack_end
        pack(child, *a, **kw)
    
    def __add_to_Container(self, child):
        self.add(child)
    
    def __add_to_Dialog(self, child, *a, **kw):
        self.vbox.pack_start(child, *a, **kw)
    
    def __add_to_MenuShell(self, child, activate_callback = None):
        if isinstance(child, basestring):
            menu_item = MenuItem(child)
            child = Menu()
            menu_item.set_submenu(child)
        else:
            menu_item = child
        self.append(menu_item)
        if activate_callback is not None:
            menu_item.connect("activate", activate_callback)
        return child
    
    def __add_to_Notebook(self, child, *a, **kw):
        self.append_page(child, *a, **kw)
    
    def __add_to_Paned(self, child, *a, **kw):
        if self.get_child1() is None:
            pack = self.pack1
        else:
            pack = self.pack2
        pack(child, *a, **kw)
    
    def __add_to_ScrolledWindow(self, child):
        result = child.set_scroll_adjustments(None, None)
        if result == True:  # child is scrollable
            self.add(child)
        else:
            self.add_with_viewport(child)
    
    def __add_to_Table(self, child, *a, **kw):
        self.attach(child, *a, **kw)
    
    def __add_to_Toolbar(self, child, pos = -1):
        self.insert(child, pos)


class GtkDialogRunSimplifiedMixin(gtk.Dialog):
    """
    Dialog with a simpler run() method.
    """
    
    def run(self):
        """
        Present, run, hide, and return response ID.
        """
        self.present()
        response_id = super(GtkDialogRunSimplifiedMixin, self).run()
        self.hide()
        return response_id


class GtkEntryActivatesDefaultMixin(gtk.Entry):
    """
    Entry that activates the default widget.
    """
    
    def __init__(self, *a, **kw):
        super(GtkEntryActivatesDefaultMixin, self).__init__(*a, **kw)
        self.set_activates_default(True)


class GtkFileChooserDialogStandardMixin(gtk.FileChooserDialog):
    """
    Standard file chooser dialog.
    """


    def __init__(self, parent = None,
                       action = gtk.FILE_CHOOSER_ACTION_OPEN):
        title = {
            gtk.FILE_CHOOSER_ACTION_OPEN: "Open File",
            gtk.FILE_CHOOSER_ACTION_SAVE: "Save As",
            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER: "Open Directory",
        }[action]
        
        buttons = {
            gtk.FILE_CHOOSER_ACTION_OPEN:
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                 gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT),
            gtk.FILE_CHOOSER_ACTION_SAVE:
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                 gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT),
            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER:
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                 gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT),
        }[action]
        
        super(GtkFileChooserDialogStandardMixin, self).__init__(
            title, parent, action, buttons
        )

        self.set_default_response(gtk.RESPONSE_ACCEPT)
        self.set_default_size(640, 480)


class GtkLabelUsingMarkupMixin(gtk.Label):
    """
    Label using markup.
    """
    
    def __init__(self, *a, **kw):
        super(GtkLabelUsingMarkupMixin, self).__init__(*a, **kw)
        self.set_use_markup(True)


class GtkScrolledWindowPolicyAutoMixin(gtk.ScrolledWindow):
    """
    ScrolledWindow uses gtk.POLICY_AUTOMATIC for h+v policies.
    """
    
    def __init__(self, *a, **kw):
        super(GtkScrolledWindowPolicyAutoMixin, self).__init__(*a, **kw)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)


class GtkTableSimplifiedMixin(gtk.Table):
    """
    Simplified Table class with many convenience methods.
    """
    
    def __init__(self):
        super(GtkTableSimplifiedMixin, self).__init__()
        self.__cursor = [0, 0]  # row, col
        self.__is_spanning_rows = []
        self.__is_spanning_columns = []
        self.connect("notify::n-rows", self.__n_rows_changed_cb)
        self.connect("notify::n-columns", self.__n_columns_changed_cb)
    
    def __n_rows_changed_cb(self, *a):
        rows = self.get_property("n-rows")
        for child in self.__is_spanning_rows:
            self.child_set_property(child, "bottom-attach", rows)
    
    def __n_columns_changed_cb(self, *a):
        columns = self.get_property("n-columns")
        for child in self.__is_spanning_columns:
            self.child_set_property(child, "right-attach", columns)
    
    def clear(self):
        for child in self.get_children():
            self.remove(child)
        self.set_cursor(0, 0)
        self.resize(1, 1)
    
    def remove(self, child):
        value = super(GtkTableSimplifiedMixin, self).remove(child)
        while child in self.__is_spanning_columns:
            self.__is_spanning_columns.remove(child)
        while child in self.__is_spanning_rows:
            self.__is_spanning_rows.remove(child)
        return value
    
    def get_cursor(self):
        return self.__cursor
    
    def set_cursor(self, row, col):
        # Advance col to next free spot or last column in the current row:
        n_columns = self.get_property("n-columns")
        children = []
        for child in self.get_children():
            left = self.child_get_property(child, "left-attach")
            right = self.child_get_property(child, "right-attach")
            top = self.child_get_property(child, "top-attach")
            bottom = self.child_get_property(child, "bottom-attach")
            if top > row or bottom <= row: continue
            if right <= col: continue
            children.append((left, right))
        while col < n_columns:
            free = True
            for left, right in children:
                if left <= col < right:
                    col = right
                    free = False
            if free: break
                
        self.__cursor = [row, col]
    
    def attach_cell(self, child, xsize = 1, ysize = 1, **kw):
        """
        Attach a widget as a (xsize x ysize) cell in the current row.
        """
        row, col = self.get_cursor()
        left = col
        right = col + xsize
        top = row
        bottom = row + ysize
        
        # Resize table if necessary.
        if right > self.get_property("n-columns"):
            self.set_property("n-columns", right)
        
        # Attach child.
        self.attach(child, left, right, top, bottom, **kw)
        
        # Set cursor to col += xsize.
        col += xsize
        self.set_cursor(row, col)
        return child
    
    def attach_row(self, child, ysize = 1, **kw):
        """
        Attach a widget as a (SPANNING x ysize) cell in the current row.
        
        The current row should be empty.  The cursor will point to the next
        row.
        """
        row, col = self.get_cursor()
        left = 0
        right = self.get_property("n-columns")
        top = row
        bottom = row + ysize
        
        # Attach child.
        self.attach(child, left, right, top, bottom, **kw)
        self.__is_spanning_columns.append(child)
        
        # Set cursor to row += ysize, col = 0.
        row += ysize
        col = 0
        self.set_cursor(row, col)
        return child
    
    def attach_column(self, child, xsize = 1, **kw):
        """
        Attach a widget as a (xsize x SPANNING) cell in the current column.
        
        The current column should be empty.  The cursor will point to the
        next column.
        """
        row, col = self.get_cursor()
        left = col
        right = col + xsize
        top = 0
        bottom = self.get_property("n-rows")
        
        # Attach child.
        self.attach(child, left, right, top, bottom, **kw)
        self.__is_spanning_rows.append(child)
        
        # Set cursor to row = 0, col += xsize.
        row = 0
        col += xsize
        self.set_cursor(row, col)
        return child
    
    def add_rows(self, ysize = 1, resize_current_row = False):
        """
        Append empty rows (default: one row) after the current row.
        
        The cursor will point to the last of the added rows.
        """
        row, col = self.get_cursor()
        
        # Resize table.
        rows = self.get_property("n-rows")
        self.set_property("n-rows", rows + 1)
        
        # Set cursor to row += ysize, col = 0.
        row_old = row
        row += ysize
        col = 0
        self.set_cursor(row, col)
        
        # Resize affected children.
        for child in self.get_children():
            top = self.child_get_property(child, "top-attach")
            bottom = self.child_get_property(child, "bottom-attach")
            if top >= row_old + 1: top += ysize
            if bottom > row_old + 1: bottom += ysize
            if bottom == row_old + 1:
                if resize_current_row: bottom += ysize
                elif child in self.__is_spanning_rows: bottom += ysize
            self.child_set_property(child, "top-attach", top)
            self.child_set_property(child, "bottom-attach", bottom)
        
        return None


class GtkTextBufferCallableMixin(gtk.TextBuffer):
    """
    TextBuffer that can be called to get or set text.
    """
    
    def __call__(self, text = None):
        if text is None:    return self.get_text()
        else:               return self.set_text(text)


class GtkTextViewAPITextBufferMixin(gtk.TextView):
    """
    TextView using an API.TextBuffer instead of a gtk.TextBuffer.
    """
    
    def __init__(self, *a, **kw):
        super(GtkTextViewAPITextBufferMixin, self).__init__(*a, **kw)
        from PyGTKShell.API import TextBuffer
        self.set_buffer(TextBuffer())


class GtkTextViewForCodeMixin(gtk.TextView):
    """
    TextView that uses a monospace font and gtk.WORD_WRAP.
    """
    
    def __init__(self, *a, **kw):
        super(GtkTextViewForCodeMixin, self).__init__(*a, **kw)
        self.modify_font(pango.FontDescription("monospace"))
        self.set_wrap_mode(gtk.WRAP_WORD)


class GtkTextViewUserExecMixin(GtkTextViewForCodeMixin):
    """
    TextView reacting to F5 and Ctrl+E by executing text as Python code.
    """
    
    def __init__(self, *a, **kw):
        super(GtkTextViewUserExecMixin, self).__init__(*a, **kw)
        self.textview_userexec_namespace = {}
        self.connect("key-press-event", self.__cb_key_press_event)
    
    def __cb_key_press_event(self, window, event):
        if (KeyPressEval("F5") | KeyPressEval("CONTROL, (E, e)"))(event):
            self.do_userexec()
            return True
        return False
    
    def do_userexec(self):
        import copy
        b = self.get_buffer()
        code = b.get_text(*b.get_bounds())
        namespace = copy.copy(self.textview_userexec_namespace)
        exec code in namespace


class GtkWidgetAutoShowMixin(gtk.Widget):
    """
    Widget shows automatically.
    """

    def __init__(self, *a, **kw):
        super(GtkWidgetAutoShowMixin, self).__init__(*a, **kw)
        show_priority = gobject.PRIORITY_DEFAULT_IDLE
        if not isinstance(self, gtk.Window):  # non-Window widget
            # Show a window with a lower priority than other widgets so
            # that they get show()n before the window does:
            show_priority = gobject.PRIORITY_HIGH_IDLE
        self.__auto_show_id = \
            gobject.idle_add(self.show, priority = show_priority)
        self.connect_after("destroy", self.__cb_after_destroy)

    def __cb_after_destroy(self, widget):
        gobject.source_remove(self.__auto_show_id)


class GtkWindowFullScreenKeyMixin(gtk.Window):
    """
    Causes the <F11> key to toggle fullscreen mode.
    """
    
    def __init__(self, *a, **kw):
        super(GtkWindowFullScreenKeyMixin, self).__init__(*a, **kw)
        self.__is_fullscreen = False
        self.connect("key-press-event", self.__cb_key_press_event)
        self.connect("window-state-event", self.__cb_window_state_event)
    
    def __cb_key_press_event(self, window, event):
        if KeyPressEval("F11")(event):
            return self.__cb_toggle_fullscreen()
        return False
    
    def __cb_window_state_event(self, window, event):
        if event.changed_mask & gtk.gdk.WINDOW_STATE_FULLSCREEN:
            self.__is_fullscreen = bool(event.new_window_state &
                                        gtk.gdk.WINDOW_STATE_FULLSCREEN)
        return False
    
    def __cb_toggle_fullscreen(self):
        if self.__is_fullscreen:    self.unfullscreen()
        else:                       self.fullscreen()
        return True


class GtkWindowLastQuitMixin(gtk.Window):
    """
    Makes the last visible Window that gets closed cause the main loop to
    quit.
    """
    
    def __init__(self, *a, **kw):
        super(GtkWindowLastQuitMixin, self).__init__(*a, **kw)
        self.connect_after("destroy", self.__cb_after_destroy)

    def __cb_after_destroy(self, widget):
        all_toplevel_windows = window_list_toplevels()
        all_toplevel_windows = filter(lambda w: w.get_property("visible"),
                                      all_toplevel_windows)
        if not all_toplevel_windows:
            # No visible toplevel windows are left
            gtk.main_quit()

