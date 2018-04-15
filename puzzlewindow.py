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
    import datetime

    # Gtk and related
    from gi import require_version as gi_require_version
    gi_require_version('Gtk', '3.0')
    from gi.repository import Gtk
    from gi.repository import Gdk, GdkPixbuf, GObject

    # Configuration and message boxes
    from auxiliary import SectionConfig, OptionConfig
    from auxiliary import MessageBox

    # Localization
    import locale
    from locale import gettext as _

    from puzzle import Puzzle
    from numberpicker import NumberPicker

except ImportError as eximp:
    import_failed(eximp)

settings = None # Keep window related options
options = None # Keep application wide options in a 'General Options' section
class GeneralApp():
    def __init__(self, name='', localizedname='', domain='', BASE_DIR='', version=VERSIONSTR ):
        self.name = name
        self.localizedname = localizedname
        self.domain = domain
        self.BASE_DIR = BASE_DIR
        self.version = version

class PuzzleWindow(Gtk.Window):
    """ Main window with all components. """

    def __init__(self, app):
        # Set the app
        self.app =  app

        # Basic initializations.
        self.we_can_exit_now = False
        self.return_parameter = (False, "00:00")
        self.picker = None
        self.picker_size = 10.
        self.previous_sel = None
        self.timer_started = None
        self.history_counter = 0
        self.playing_history = False

        #self.strings_to_use = [' ','α','β','γ','δ','ε','ς','ζ','η','θ']
        #self.strings_to_use = [' ','1','2','3','4','5','6','7','8','9']

        # Init the settings module.
        self.dummy_for_settings = SectionConfig(self.app.name, self.__class__.__name__)
        global settings
        settings = self.dummy_for_settings

        self.dummy_for_options = OptionConfig(self.app.name)
        global options
        options = self.dummy_for_options

        Gtk.Window.__init__(self)
        self.set_title(self.app.localizedname)

        # Initializations required before loading glade file.

        # Bind the locale.
        locale.bindtextdomain(self.app.domain, os.path.join(self.app.BASE_DIR, 'locale'))
        locale.textdomain(self.app.domain)

        # Load app and window icon.
        self.set_icon(self.app.icon)

        # Bind message boxes.
        self.MessageBox = MessageBox(self)
        self.msg = self.MessageBox.Message

        # Glade stuff
        # Load Glade file to self
        self.builder = Gtk.Builder()
        try:
            self.builder.add_from_file(os.path.join(self.app.BASE_DIR, 'ui', 'puzzlewindow.glade'))
        except Exception as ex:
            print(str(ex))
            print('\n{}:\n{}\n{}'.format(_('Error loading from Glade file'), os.path.join(self.app.BASE_DIR, 'ui', 'puzzlewindow.glade'), repr(ex)))
            sys.exit(ERROR_INVALID_GLADE_FILE)

        # Get gui objects
        self.MainBox = self.builder.get_object('MainBox')
        self.boxTimer = self.builder.get_object('boxTimer')
        self.boxMenu = self.builder.get_object('boxMenu')
        self.buttonHome = self.builder.get_object('buttonHome')
        self.drawingareaPuzzle = self.builder.get_object('drawingareaPuzzle')
        self.eventboxPuzzle = self.builder.get_object('eventboxPuzzle')
        self.imageClock = self.builder.get_object('imageClock')
        self.labelClock = self.builder.get_object('labelClock')
        self.labelVersion = self.builder.get_object('labelVersion')
        self.listboxPieces = self.builder.get_object('listboxPieces')

        # Connect signals existing in the Glade file
        self.builder.connect_signals(self)

        # Reparent our main container from glader file,
        # this way we have all Gtk.Window functionality using "self"
        thechild = self.builder.get_object('PuzzleWindow').get_child()
        thechild.get_parent().remove(thechild)
        self.add(thechild)

        # Connect generated signals.
        self.buttonHome.connect('clicked', self.on_buttonHome_clicked)
        self.connect('delete-event', self.on_PuzzleWindow_delete_event)
        self.connect('destroy', self.on_PuzzleWindow_destroy)
        self.connect('key-release-event', self.on_PuzzleWindow_key_release_event)
        self.connect('size-allocate', self.on_PuzzleWindow_size_allocate)
        self.connect('window-state-event', self.on_PuzzleWindow_window_state_event)

        # Get any properties of top window.
        # Set the label for labelVersion
        self.labelVersion.set_label(VERSIONSTR)
        self.can_focus = 'False'

        # Load any settings or run extra initializations
        self.post_initialisations()

#********* Auto created "class defs" START ************************************************************
#********* Auto created handlers START *********************************

    def on_PuzzleWindow_delete_event(self, widget, event, *args):
        """ Handler for PuzzleWindow.delete-event. """
        self.set_unhandled_settings()
        return False

    def on_PuzzleWindow_destroy(self, widget, *args):
        """ Handler for PuzzleWindow.destroy. """
        if self.picker:
            self.picker.destroy()
        self.exit_requested()
        return False

    def on_PuzzleWindow_key_release_event(self, widget, event, *args):
        """ Handler for PuzzleWindow.key-release-event. """
        #if self.playing_history:
            #return False
        txt = Gdk.keyval_name(event.keyval)
        if type(txt) == type(None):
            return False
        txt = txt.replace('KP_', '')
        try:
            aunichar = chr(Gdk.keyval_to_unicode(event.keyval))
        except:
            aunichar = None
        if txt in ['Up','Down','Left','Right']:
            self.move_selection(['Up','Down','Left','Right'].index(txt))
        elif txt in ['0','1','2','3','4','5','6','7','8','9', 'Delete'] or txt in self.app.strings_to_use[1:]:
            self.set_num_in_selection(txt)
        elif aunichar and aunichar in self.app.strings_to_use[1:]:
            self.set_num_in_selection(aunichar)
        else:
            return False
        return True

    def on_PuzzleWindow_size_allocate(self, widget, allocation, *args):
        """ Handler for PuzzleWindow.size-allocate. """
        self.save_my_size()

    def on_PuzzleWindow_window_state_event(self, widget, event, *args):
        """ Handler for PuzzleWindow.window-state-event. """
        settings.set('maximized',
            ((int(event.new_window_state) & Gdk.WindowState.ICONIFIED) != Gdk.WindowState.ICONIFIED) and
            ((int(event.new_window_state) & Gdk.WindowState.MAXIMIZED) == Gdk.WindowState.MAXIMIZED)
            )
        self.save_my_size()

    def on_buttonHome_clicked(self, widget, *args):
        """ Handler for buttonHome.clicked. """
        self.exit_requested()

    def on_drawingareaPuzzle_draw(self, widget, cr, *args):
        """ Handler for drawingareaPuzzle.draw. """
        w = widget.get_allocated_width()
        h = widget.get_allocated_height()
        b = self.puzzle.draw(cr, w, h)
        self.fill_pieces()

    def on_eventboxPuzzle_button_press_event(self, widget, event, *args):
        """ Handler for eventboxPuzzle.button-press-event. """
        self.picker_hide()

        col, rest = divmod(event.x-self.puzzle.startx , self.puzzle.the_9)
        row, rest = divmod(event.y-self.puzzle.starty , self.puzzle.the_9)

        if col >= 0 and row >=0 and col < 9 and row < 9:
            blah = int(col) * 9 + int(row)
            if self.previous_sel != None:
                self.puzzle.puzzlenums[self.previous_sel]['sel'] = False
            self.puzzle.puzzlenums[blah]['sel'] = True
            self.previous_sel = blah
            self.drawingareaPuzzle.queue_draw()
            if not self.puzzle.puzzlenums[blah]['const']:
                if event.button == 3:
                    self.puzzle.puzzlenums[self.previous_sel]['num'] = 0
                    self.puzzle.append_to_history((self.previous_sel, self.puzzle.puzzlenums[self.previous_sel]['num'], self.labelClock.get_label()))
                elif event.button == 1:
                    left, top = self.get_position()
                    if self.picker_size != self.puzzle.the_9:
                        self.picker_size = self.puzzle.the_9
                        self.picker.resize(self.picker_size, self.picker_size)
                    self.picker.move(left + event.x, top + event.y)
                    response = self.picker.get_number()
                    if response:
                        self.puzzle.puzzlenums[self.previous_sel]['num'] = int(response)
                        self.puzzle.append_to_history((self.previous_sel, self.puzzle.puzzlenums[self.previous_sel]['num'],self.labelClock.get_label()))
                else:
                    return False

            self.puzzle.check_puzzle()
            self.drawingareaPuzzle.queue_draw()
            if self.puzzle.solved:
                self.show_solved()
                return True
        else:
            print('outside')

#********* Auto created handlers  END **********************************

    def post_initialisations(self):
        """ Do some extra initializations.

        Display the version if a labelVersion is found.
        Set defaults (try to load them from a configuration file):
            - Window size and state (width, height and if maximized)
        Load other saved custom settings.
        """
        # Set previous size and state
        width = settings.get('width', 350)
        height = settings.get('height', 350)
        self.set_title(self.app.localizedname)
        self.resize(width, height)
        if settings.get_bool('maximized', False):
            self.maximize()

        # Load any other settings here.
        if self.app.show_simple:
            self.boxMenu.set_visible(not self.app.show_simple)
            self.boxMenu.set_no_show_all(True)
        if not self.app.show_pieces:
            self.listboxPieces.set_no_show_all(True)
        if not self.app.show_timer:
            self.boxTimer.set_no_show_all(True)
        self.listboxPieces.set_visible(self.app.show_pieces)
        self.imageClock.set_visible(self.app.show_timer)
        self.labelClock.set_visible(self.app.show_timer)
        if self.app.thehistory:# history passed, user wants replay.
            self.set_sensitive(False)
            self.playing_history = True
            self.puzzle = Puzzle(self.app.puzzle_str, self.app.strings_to_use, self.app.font_scale, self.app.thehistory)
        else:
            self.start_puzzle()

    def set_unhandled_settings(self):
        """ Set, before exit, settings not applied during the session.

        Mass set some non critical settings for widgets
        (which where not setted when some widget's state changed).
        """
        #custom settings
        history_str = str(self.puzzle.history)
        #history_str = history_str.replace("'",'"')
        #history_json = json.loads(history_str)
        #history_json_str = json.dump(history_json)
        #history_str = history_json_str
        #print()
        history_str = history_str.replace("}}, ","}},\n ")
        history_str = history_str.replace("), ","),\n ")
        options.set('last_history', history_str)

    def save_my_size(self):
        """ Save the window size into settings if not maximized. """
        if not settings.get_bool('maximized', False):
            width, height = self.get_size()
            settings.set('width', width)
            settings.set('height', height)

    def exit_requested(self, *args):
        """ Set the param in order to exit from "run" method. """
        self.set_transient_for()
        self.set_modal(False)
        self.set_unhandled_settings()
        self.we_can_exit_now = True
        self.destroy()#Will not call Handler for delete-event

    def run(self):
        """ Start the main loop.

        WARNING:
            The "destroy" event of the main window
            MUST set the "we_can_exit_now" to True,
            else program will never exit.
        Save settings on exit.
        Return "return_parameter" on exit.
        """
        #now we can show the main window.
        self.show_all()
        #self.boxMenu.set_visible(not self.app.show_simple)
        #self.set_interactive_debugging (True)
        if self.app.thehistory:
            GObject.timeout_add(1000, self.play_history)
        while True:
            if self.we_can_exit_now:
                break
            while Gtk.events_pending():
                Gtk.main_iteration()
        settings.save()
        return self.return_parameter

#********* Auto created "class defs" END **************************************************************
    def on_piece_pressed(self, widget, event, *args):
        """ Handler for any piece.button-press-event. """
        print('pressed piece:', args[0])

    def show_solved(self):
        """ Show a message and call exit window. """
        now = datetime.datetime.utcnow()
        print('now,self.timer_started',now,self.timer_started)
        diff = now - self.timer_started
        self.return_parameter = (True, str(diff)[2:7])
        self.msg('{}\n ({}: {})'.format(_('Solved!'), _('time passed'), self.return_parameter[1]))
        self.exit_requested()

    def set_num_in_selection(self, txt):
        """ Pokes the num in the puzzlenums dictionary. """
        self.picker_hide()
        sel = self.puzzle.puzzlenums[self.previous_sel]
        if sel['const']:
            return
        if txt in ['0','1','2','3','4','5','6','7','8','9']:
            sel['num'] = int(txt)
        elif txt in self.app.strings_to_use[1:]:
            sel['num'] = self.app.strings_to_use.index(txt)
        elif txt == 'Delete':
            sel['num'] = 0
        else:
            return
        self.puzzle.append_to_history((self.previous_sel, sel['num'],self.labelClock.get_label()))
        self.puzzle.check_puzzle()
        self.drawingareaPuzzle.queue_draw()
        if self.puzzle.solved:
            self.show_solved()

    def move_selection(self, where):
        """ Move selection to cell based on key pressed. """
        self.picker_hide()
        if self.previous_sel == None:
            self.previous_sel = 0
            self.puzzle.puzzlenums[0]['sel'] = True
            self.drawingareaPuzzle.queue_draw()
        else:
            sel = -1
            if where == 0:
                sel = self.previous_sel - 1
            elif where == 1:
                sel = self.previous_sel + 1
            elif where == 2:
                sel = self.previous_sel - 9
            elif where == 3:
                sel = self.previous_sel + 9
            if sel>=0 and sel <=80:
                self.puzzle.puzzlenums[self.previous_sel]['sel'] = False
                self.previous_sel = sel
                self.puzzle.puzzlenums[self.previous_sel]['sel'] = True
                self.drawingareaPuzzle.queue_draw()

    def picker_hide(self):
        """ Hide the picker, if any. """
        if self.picker:
            self.picker.hide()

    def fill_pieces(self):
        """ Fill label with remaining pieces. """
        if not self.listboxPieces.get_visible():
            return
        thelistbox = self.listboxPieces
        allchildren = thelistbox.get_children()
        for achild in allchildren[:]:
            achild.destroy()
        label = Gtk.Label(_('Remaining:'))
        thelistbox.add(label)
        label.set_visible(True)
        for x in range(9):
            label = Gtk.Label("<" + self.app.strings_to_use[x+1] + '>: ' + str(9-self.puzzle.pieces[x+1]))
            eb = Gtk.EventBox()
            eb.connect("button-press-event", self.on_piece_pressed, x)
            eb.add(label)
            thelistbox.add(eb)
            eb.set_visible(True)
            label.set_visible(True)

        label = Gtk.Label("<.>: " + str(self.puzzle.pieces[0]))
        eb = Gtk.EventBox()
        eb.add(label)
        thelistbox.add(eb)
        eb.set_visible(True)
        label.set_visible(True)

    def start_puzzle(self):
        self.picker = NumberPicker(self, thelist=self.app.strings_to_use)
        self.picker.set_type_hint( Gdk.WindowTypeHint.DIALOG )
        self.puzzle = Puzzle(self.app.puzzle_str, self.app.strings_to_use, self.app.font_scale)
        self.timer_started = datetime.datetime.utcnow()
        GObject.timeout_add(500, self.show_time_passed)

    def play_history(self):
        if self.history_counter >= len(self.app.thehistory)-1:
            # Set to continue
            print('CONTINUE')
            self.playing_history = False
            self.picker = NumberPicker(self, thelist=self.app.strings_to_use)
            self.picker.set_type_hint( Gdk.WindowTypeHint.DIALOG)
            # set the timer
            timestr = self.labelClock.get_label()
            b = datetime.timedelta(seconds= int(timestr[:2])*60 +int(timestr[3:]))
            self.timer_started = datetime.datetime.utcnow() - b
            self.puzzle.check_puzzle()
            if self.puzzle.solved:
                #self.return_parameter = (True, self.labelClock.get_label())
                self.show_solved()
            else:
                self.puzzle.check_puzzle()
                GObject.timeout_add(500, self.show_time_passed)
                self.set_sensitive(True)
            return False
        self.history_counter += 1
        amove = self.app.thehistory[self.history_counter]
        self.puzzle.puzzlenums[amove[0]]['num'] = amove[1]
        self.labelClock.set_label(amove[2])
        self.puzzle.check_puzzle()
        self.drawingareaPuzzle.queue_draw()
        return True

    def show_time_passed(self):
        """ Show time passed.

        Only works if option is enabled.
        """
        if self.playing_history:
            return False
        diff = datetime.datetime.utcnow() - self.timer_started
        tmp = str(diff)[2:7]
        self.return_parameter = (self.return_parameter[0], tmp)
        self.labelClock.set_label(tmp)
        return True and not self.we_can_exit_now

#********* Window class  END***************************************************************************
def mainAppEntry(BASE_DIR):
    appdomain = 'org.kekbay.sudokugtk'
    # Bind the locale
    locale.bindtextdomain(appdomain, os.path.join(BASE_DIR, 'locale'))
    locale.textdomain(appdomain)
    app = GeneralApp('Sudoku-Gtk', _('Sudoku-Gtk'), appdomain, BASE_DIR, __version__)
    # Load app and window icon
    logo = 'logo.png'
    thefile = os.path.join(app.BASE_DIR, logo)
    if not os.path.exists(thefile):
        thefile = os.path.join(app.BASE_DIR, 'icons', logo)
    try:
        app.icon = GdkPixbuf.Pixbuf.new_from_file(thefile)
    except Exception:
        app.icon = None
    app_window = PuzzleWindow(app)
    response = app_window.run()
    return response

