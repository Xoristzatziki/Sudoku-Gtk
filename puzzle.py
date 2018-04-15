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

#RETURN ERROR CODES
ERROR_IMPORT_LIBRARIES_FAIL = -1
ERROR_INVALID_GLADE_FILE = -2
ERROR_GLADE_FILE_READ = -3

def import_failed(err):
    """ Fail with a friendlier message when imports fail. """
    msglines = (
        'Missing some third-party libraries.',
        'Please install requirements using \'pip\' or your package manager.',
        'The import error was:',
        '    {}'
    )
    print('\n'.join(msglines).format(err))
    sys.exit(ERROR_IMPORT_LIBRARIES_FAIL)

try:
    import os
    import sys
    from copy import deepcopy

    # Gtk and related
    from gi import require_version as gi_require_version
    gi_require_version('Gtk', '3.0')
    from gi.repository import Gtk
    from gi.repository import Gdk, GdkPixbuf
    import cairo

    # Configuration and message boxes
    from auxiliary import SectionConfig, OptionConfig
    from auxiliary import MessageBox

    # Localization
    import locale
    from locale import gettext as _

except ImportError as eximp:
    import_failed(eximp)

ROWS = {}
COLS = {}
SQUARES = {}
for xcounter in range(3):
    col = xcounter * 3
    colindex = col * 9
    rowindex = col
    #print(col, 'colindex', colindex, colindex+9, colindex+18, rowindex)
    COLS[colindex] = [colindex + x for x in range(9)]
    COLS[colindex+9] = [colindex+9 + x for x in range(9) ]
    COLS[colindex+18] = [colindex+18 + x for x in range(9) ]
    ROWS[rowindex] = [rowindex + 9 * x for x in range(9)]
    ROWS[rowindex+1] = [rowindex+1 + 9 * x for x in range(9)]
    ROWS[rowindex+2] = [rowindex+2 + 9 * x for x in range(9)]
    for ycounter in range(3):
        #colindex = col*3 * ycounter
        #print('colindex', colindex,colindex+9,colindex+18)

        row = ycounter * 3

        square = col * 9 + row
        SQUARES[square] = [square, square+1, square+2,
                9+square, 10+square, 11+square,
                18+square, 19+square, 20+square]

class DrawPuzzle():
    def __init__(self, thelist=None, thescale = 110):
        self.thelist = thelist
        if not self.thelist:
            self.thelist = [' ','1','2','3','4','5','6','7','8','9']
        self.thescale = thescale / 100
        #print('init DrawPuzzle', thelist, thescale)

    def draw(self,  puzzlenums, cr, w, h):
        #print('DRAW puzzlenums',puzzlenums)
        #self.size = size
        cr.set_line_width(4)
        cr.set_source_rgb(0,0,0)
        size = min(w,h)-10
        xcenter = (w - 5) / 2
        ycenter = (h - 3) / 2
        startx = xcenter - (size/2)
        starty = ycenter - (size/2)
        cr.rectangle(startx , starty, size, size)
        cr.stroke()
        #print(w,h,size, xcenter,ycenter)
        the_9 = size / 9
        cr.set_line_width(1)
        #font_size = the_9 * 1./1.95
        font_size = the_9 * 1./self.thescale
        #print('font_size = the_9 * 1./self.thescale',font_size, the_9, self.thescale)
        cr.select_font_face("Monospace",
            cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(font_size)
        for rowcounter in range(9):
            for colcounter in range(9):
                cr.set_source_rgb(0,0,0)
                num = colcounter * 9 + rowcounter + 1
                the_x = colcounter * the_9
                the_y = rowcounter * the_9
                d_num = puzzlenums[num-1]['num']
                d_const = puzzlenums[num-1]['const']
                d_sel = puzzlenums[num-1]['sel']
                #d_str = str(d_num) if d_num else ' '
                d_str = self.thelist[d_num]
                d_red = puzzlenums[num-1]['red']

                # Rectangle
                if d_sel:
                    cr.set_source_rgba(0,0.5,1,0.10)
                elif d_const:
                    cr.set_source_rgb(0.85,0.85,0.85)
                else:
                    cr.set_source_rgb(1,1,1)
                cr.rectangle(startx + the_x + 1, starty + the_y + 1, the_9-2, the_9-2)
                cr.fill()

                cr.rectangle(startx + the_x , starty + the_y, the_9, the_9)
                cr.set_source_rgb(0,0,0)
                cr.stroke()

                # Digit
                cr.set_source_rgb(0,0,0)
                #if d_str == None:
                    #print()
                x_bearing, y_bearing, d_width, d_height = cr.text_extents(d_str)[:4]
                #print(puzzlenums[str(num-1)], x_bearing, y_bearing, d_width, d_height, the_9)
                d_x = (the_9 - d_width)/2 + startx + the_x - x_bearing
                d_y = (the_9 - d_height)/2 + starty + the_y - y_bearing
                if d_red:
                    cr.set_source_rgb(1,0,0)
                else:
                    cr.set_source_rgb(0,0,0)
                cr.move_to(d_x, d_y)
                cr.show_text(d_str)

        the_3 = size / 3
        cr.set_line_width(3)
        for rowcounter in range(3):
            for colcounter in range(3):
                the_x = colcounter * the_3
                the_y = rowcounter * the_3
                cr.rectangle(startx + the_x , starty + the_y, the_3, the_3)
                cr.stroke()
        return startx, starty, the_9

class Puzzle():
    def __init__(self,  puzzle=None, thelist=None, thescale=110, thehistory=None):
        self.replay = (thehistory != None)
        self.puzzlenums = {}
        self.history = {}
        if self.replay:
            self.history = deepcopy(thehistory)
            self.puzzlenums = deepcopy(thehistory[0])
        else:
            if puzzle:
                p = puzzle
            else:
                p = '83....5....29..6....7..8.39..8....2..4.....569............3...8.83.2..6.7.5...29.'
            for xcounter in range(81):
                n = int(p[xcounter]) if p[xcounter] != '.' else 0
                self.puzzlenums[xcounter] = {'num' : n,
                        'const' : True if n else False,
                        'sel' : False,
                        'red' : False}
            self.history[0] = deepcopy(self.puzzlenums)
        self.w = None
        self.h = None
        self.has_errors = False
        self.solved = False
        self.pieces = {}
        self.drawing = DrawPuzzle(thelist, thescale)

    def draw(self, cr, w, h):
        self.startx, self.starty, self.the_9 = self.drawing.draw(self.puzzlenums, cr, w, h)
        self.pieces = {}
        for x in range(10):
            self.pieces[x] = 0
        for item in self.puzzlenums:
            thenum = self.puzzlenums[item]['num']
            self.pieces[thenum] = self.pieces.get(thenum, 0) + 1

    def get_duplicates(self, oflist):
        response = {}
        for cell_index in oflist[:]:
            cell_num = self.puzzlenums[cell_index]['num']
            if cell_num:
                for others in oflist[:]:
                    if cell_index != others:
                        if self.puzzlenums[others]['num'] == cell_num:
                            response[cell_index] = True
                            response[others] = True
        return response

    def check_puzzle(self):
        dups = {}
        for alist in COLS:
            tmpdups = self.get_duplicates(COLS[alist])
            for d in tmpdups:
                dups[d] = True
        for alist in ROWS:
            tmpdups = self.get_duplicates(ROWS[alist])
            for d in tmpdups:
                dups[d] = True
        for alist in SQUARES:
            tmpdups = self.get_duplicates(SQUARES[alist])
            for d in tmpdups:
                dups[d] = True
        has_zeroes = False
        for xcounter in range(81):
            self.puzzlenums[xcounter]['red'] = xcounter in dups
            if self.puzzlenums[xcounter]['num'] == 0:
                has_zeroes = True
        self.has_errors = len(dups)
        if not self.has_errors and not has_zeroes:
            self.solved = True

    def append_to_history(self, amove):
        self.history[len(self.history)] = amove
