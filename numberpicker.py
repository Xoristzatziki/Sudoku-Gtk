#!/usr/bin/env python3
"""
    Copyright (C) Ηλίας Ηλιάδης, 2018-04-11; ilias iliadis <iliadis@kekbay.gr>

    This file is part of Sudoku-Gtk.

    Sudoku-Gtk is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Sudoku-Gtk is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Sudoku-Gtk.  If not, see <http://www.gnu.org/licenses/>.
"""

#FIXME: correct the version
__version__ = '0.0.22'
VERSIONSTR = 'v. {}'.format(__version__)

# No need to check imports. Should be imported by main window class
import os
import sys
# Gtk and related
from gi import require_version as gi_require_version
gi_require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

class NumberPicker(Gtk.Window):
    def __init__(self, parent= None, thelist=[' ','1','2','3','4','5','6','7','8','9']):
        Gtk.Window.__init__(self,type = Gtk.WindowType.POPUP)
        self.enumobjects = []
        self.thelist = thelist
        self.we_can_exit_now = False
        self.return_parameter = None
        self.number_found = False
        self.destroyed = False
        self.previous_size = 0

        self.connect('configure-event',self.on_NumberPicker_configure_event)
        self.connect('destroy', self.on_NumberPicker_destroy)
        self.connect('hide', self.on_NumberPicker_hide)
        self.connect('key-release-event', self.on_NumberPicker_key_release_event)
        self.post_initialisations()
        self.parent = parent

    def on_NumberPicker_configure_event(self, widget, event, *args):
        newnum = event.height / 6
        if newnum != self.previous_size:
            self.previous_size = newnum
            for obj in self.enumobjects:
                self.set_object_attr(obj, 'font-size','{}px'.format(str(newnum)))
        #TODO: Remove on final version
        if event.height != event.width:
            print('OHOHOHO!!!!!','event.height:', event.height, ': event.width:', event.width)

    def on_NumberPicker_destroy(self, widget, *args):
        """ Handler for NumberPicker.destroy. """
        self.destroyed = True
        self.number_found = True
        return False

    def on_NumberPicker_hide(self, widget, *args):
        """ Handler for NumberPicker.hide. """
        self.number_found = True

    def on_NumberPicker_key_release_event(self, widget, event, *args):
        """ Handler for NumberPicker.key-release-event. """
        txt = Gdk.keyval_name(event.keyval)
        if type(txt) == type(None):
            return
        txt = txt.replace('KP_', '')
        try:
            aunichar = chr(Gdk.keyval_to_unicode(event.keyval))
        except:
            aunichar = None
        if txt in ['0','1','2','3','4','5','6','7','8','9']:
            self.return_parameter = txt
            self.hide()
        elif txt == 'Escape':
            self.return_parameter = None
            self.hide()
        elif txt in ['BackSpace','Delete']:
            self.return_parameter = '0'
            self.hide()
        elif aunichar and aunichar in self.thelist[1:]:
            self.return_parameter = self.thelist.index(aunichar)
            #print(self.return_parameter, self.thelist[1:])
            self.hide()
        else:
            return False

    def on_any_eb_button_press_event(self, widget, event, *args):
        if event.button == 3:
            self.return_parameter = '0'
            self.hide()
            return True
        elif event.button == 1:
            self.return_parameter = widget.get_child().id[1:]
            self.hide()
            return True
        return False

    def post_initialisations(self):
        b = Gdk.Geometry()
        b.min_aspect = b.max_aspect = 1.
        b.min_width = b.min_height = 33
        c = Gdk.WindowHints(Gdk.WindowHints.POS |
                Gdk.WindowHints.USER_POS |
                Gdk.WindowHints.USER_SIZE |
                Gdk.WindowHints.ASPECT |
                Gdk.WindowHints.MIN_SIZE)
        self.set_geometry_hints(self, b, c)
        self.gridMain = Gtk.Grid()
        self.gridMain.set_row_homogeneous(True)
        self.gridMain.set_column_homogeneous(True)
        self.gridMain.set_row_spacing(3)
        self.gridMain.set_column_spacing(3)
        for rowcounter in range(3):
            for colcounter in range(3):
                num = colcounter * 3 + rowcounter + 1
                label = Gtk.Label(self.thelist[num])
                label.id = 'l' + str(num)
                eb = Gtk.EventBox()
                eb.add(label)
                self.set_object_attr(eb, 'background','gray')
                self.set_object_attr(eb, 'color','white')
                eb.connect('button-press-event',
                    self.on_any_eb_button_press_event)
                self.gridMain.attach(eb, rowcounter+1, colcounter+1, 1, 1)
                self.enumobjects.append(label)
        self.add(self.gridMain)

    def set_object_attr(self, theobject, var, val):
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(
            ('''*{''' + var + ''':''' + val + ''';}''').encode('utf-8'))
        context = theobject.get_style_context()
        context.add_provider(style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def exit_requested(self, *args):
        self.destroy()

    def get_number(self):
        self.return_parameter = None
        self.number_found = False
        self.show_all()
        while True:
            if self.number_found:
                break
            while Gtk.events_pending():
                Gtk.main_iteration()
        return self.return_parameter

    def hide_me(self):
        self.number_found = True
