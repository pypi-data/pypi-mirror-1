#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyGTK Shell Utilities.
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


# This is a GTK workaround:

def window_list_toplevels():
    return filter(lambda w: w.get_property("type") == gtk.WINDOW_TOPLEVEL,
                  gtk.window_list_toplevels())


class FunctionWritableFile(object):
    """
    A fake output file class.
    
    Output is sent to the callback function specified upon initialization.
    
    >>> acc = []
    >>> def fn(s): acc.append(s)
    >>> f = FunctionWritableFile(fn)
    >>> f.write("Hello, ")
    >>> f.write("World!\\n")
    >>> f.close()
    >>> acc
    ['Hello, ', 'World!\\n']
    """

    def __init__(self, __func, *__func_args, **__func_kw_args):
        super(FunctionWritableFile, self).__init__()
        self.__func         = __func
        self.__func_args    = __func_args
        self.__fileno       = __func_kw_args.pop("__fileno", -1)
        self.__func_kw_args = __func_kw_args
        self.__last_char    = ""

    def close(self):
        pass  # return None

    def ensure_newline(self):
        if self.__last_char not in ("", "\n"):
            print >>self

    def flush(self):
        pass  # return None
    
    def fileno(self):
        return self.__fileno

    def isatty(self):
        return 0

    def read(self, a):
        return ""

    def readline(self):
        return ""

    def readlines(self):
        return []

    def seek(self, a):
        raise IOError, (29, "Illegal seek")

    def tell(self):
        raise IOError, (29, "Illegal seek")

    def truncate(self, *a, **kw):
        return self.seek(*a, **kw)

    def write(self, s):
        if not s: return None
        self.__func(s, *self.__func_args, **self.__func_kw_args)
        self.__last_char = s[-1]

    def writelines(self, l):
        self.write("".join(l))


class KeyPressEval(object):
    """
    Utility class to be used in key-press-event callbacks:
    
    key = KeyPressEval("CONTROL, (H, h)")   # to test for Ctrl-H
    key.match(event) == True                # or:
    key(event.keyval, event.state) == True
    
    The methods __call__() (last line) and match() (middle line) are
    equivalent.
    
    You can add up alternatives:
    
    keys = KeyPressEval("CONTROL, (E, e)") | KeyPressEval("End")
    # same as:
    # KPE = KeyPressEval
    # keys = KPE((KPE("CONTROL, (E, e)"), KPE("End")))
    # same as:
    # keys = KPE(("CONTROL, (E, e)", "End"))
    keys.match(event) == True
    """
    
    import re
    
    __re_key_parser = re.compile(r"\b(\w+)\b")
    # I'm not sure about that:
    __lock_modifiers = \
        gtk.gdk.LOCK_MASK | \
        gtk.gdk.MOD2_MASK | \
        gtk.gdk.MOD3_MASK | \
        0
    
    def __init__(self, key_expr, ignore_modifiers = False):
        self.__valid_keys_dict = {}
        
        if not isinstance(key_expr, basestring) and \
            hasattr(key_expr, "__getitem__"):
            for kpe in key_expr:
                if isinstance(kpe, basestring):
                    kpe = KeyPressEval(kpe, ignore_modifiers)
                self.__valid_keys_dict.update(kpe.__valid_keys_dict)
            return None
        
        # Parse the key binding expression by converting it to Python code.
        python_expr = "(%s,)" % self.__re_key_parser.sub(
                            "keys._get_key('\g<1>')", key_expr)
        binding_tuple = eval(python_expr, {"keys": self})

        keyval_list = []
        modstate_list = []
        self.__disassemble(binding_tuple, keyval_list, modstate_list)
        
        if not modstate_list: modstate_list = [0]
        
        for kv in keyval_list:
            for ms in modstate_list:
                self.__valid_keys_dict[(kv, ms)] = ignore_modifiers
    
    def __or__(self, other):
        return KeyPressEval((self, other))
    
    def __disassemble(self, thing, kv_list, ms_list):
        if hasattr(thing, "__getitem__"):
            [self.__disassemble(i, kv_list, ms_list) for i in thing]
        elif isinstance(thing, gtk.gdk.ModifierType):
            ms_list.append(int(thing))
        else:
            kv_list.append(int(thing))

    def _get_key(self, name):
        keyval = getattr(gtk.keysyms, name, None)
        if keyval is not None: return keyval
        return getattr(gtk.gdk, name + "_MASK")
    
    def match(self, event_keyval, event_state = 0):
        if isinstance(event_keyval, gtk.gdk.Event):
            event = event_keyval
            event_keyval = event.keyval
            event_state = event.state
        keyval, modstate = [int(x) for x in (event_keyval, event_state)]
        
        if (keyval, modstate) in self.__valid_keys_dict: return True
        # Try again with all *lock* modifiers masked out:
        modstate &= ~self.__lock_modifiers

        if (keyval, modstate) in self.__valid_keys_dict: return True
        # Try again with *all* modifiers masked out:
        modstate &= ~gtk.gdk.MODIFIER_MASK
        
        if (keyval, modstate) not in self.__valid_keys_dict: return False
        
        # Only valid if ignore_modifiers had been specified:
        return self.__valid_keys_dict[(keyval, modstate)]
    
    __call__ = match

