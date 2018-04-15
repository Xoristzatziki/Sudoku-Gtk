#!/usr/bin/env python3
#FIXME:
"""
    Copyright (C) , 2018-04-11; ilias iliadis <>

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
    import ast

    import subprocess

    # Gtk and related
    from gi import require_version as gi_require_version
    gi_require_version('Gtk', '3.0')
    from gi.repository import Gtk
    from gi.repository import Gdk, GdkPixbuf

    # Configuration and message boxes
    from auxiliary import SectionConfig, OptionConfig
    from auxiliary import MessageBox

    # Localization
    import locale
    from locale import gettext as _

    from puzzlewindow import PuzzleWindow
    from options import windowOptions, THEDICTS

except ImportError as eximp:
    import_failed(eximp)

settings = None # Keep window related options
options = None #Keep application wide options in a 'General Options' section
class GeneralApp():
    def __init__(self, name='', localizedname='', domain='', BASE_DIR='', version=VERSIONSTR ):
        self.name = name
        self.localizedname = localizedname
        self.domain = domain
        self.BASE_DIR = BASE_DIR
        self.version = version

class windowMain(Gtk.Window):
    """ Main window with all components. """

    def __init__(self,  app):
        # Set the app
        self.app =  app
        self.app.thehistory = None

        # Basic initializations.
        self.we_can_exit_now = False
        self.return_parameter = None

        self.thedicts = THEDICTS

        # Init the settings module.
        self.dummy_for_settings = SectionConfig(self.app.name, self.__class__.__name__)
        global settings
        settings = self.dummy_for_settings

        self.dummy_for_options = OptionConfig(self.app.name)
        global options
        options = self.dummy_for_options

        Gtk.Window.__init__(self)

        # Initializations required before loading glade file.

        # Bind the locale.
        locale.bindtextdomain(self.app.domain, os.path.join(self.app.BASE_DIR, 'locale'))
        locale.textdomain(self.app.domain)

        # Load app and window icon.
        self.set_icon(self.app.icon)

        # Bind message boxes.
        self.MessageBox = MessageBox(self)
        self.msg = self.MessageBox.Message

        # Glade stuff.
        # Load Glade file to self.
        self.builder = Gtk.Builder()
        try:
            self.builder.add_from_file(os.path.join(self.app.BASE_DIR, 'ui', 'sudokugtk.glade'))
        except Exception as ex:
            print(str(ex))
            print('\n{}:\n{}\n{}'.format(_('Error loading from Glade file'), os.path.join(self.app.BASE_DIR, 'ui', 'sudokugtk.glade'), repr(ex)))
            sys.exit(ERROR_INVALID_GLADE_FILE)

        # Get gui objects.
        self.MainBox = self.builder.get_object('MainBox')
        self.boxForFooter = self.builder.get_object('boxForFooter')
        self.buttonAbout = self.builder.get_object('buttonAbout')
        self.buttonContinue = self.builder.get_object('buttonContinue')
        self.buttonExit = self.builder.get_object('buttonExit')
        self.buttonNewPuzzle = self.builder.get_object('buttonNewPuzzle')
        self.buttonOptions = self.builder.get_object('buttonOptions')
        self.dummylabel = self.builder.get_object('dummylabel')
        self.labelInfo = self.builder.get_object('labelInfo')
        self.labelVersion = self.builder.get_object('labelVersion')

        # Connect signals existing in the Glade file
        self.builder.connect_signals(self)

        # Reparent our main container from glader file,
        # this way we have all Gtk.Window functionality using "self".
        thechild = self.builder.get_object('windowMain').get_child()
        thechild.get_parent().remove(thechild)
        self.add(thechild)

        # Connect generated signals.
        self.buttonAbout.connect('clicked', self.on_buttonAbout_clicked)
        self.buttonContinue.connect('clicked', self.on_buttonContinue_clicked)
        self.buttonExit.connect('clicked', self.on_buttonExit_clicked)
        self.buttonNewPuzzle.connect('clicked', self.on_buttonNewPuzzle_clicked)
        self.buttonOptions.connect('clicked', self.on_buttonOptions_clicked)
        self.connect('delete-event', self.on_windowMain_delete_event)
        self.connect('destroy', self.on_windowMain_destroy)
        self.connect('size-allocate', self.on_windowMain_size_allocate)
        self.connect('window-state-event', self.on_windowMain_window_state_event)

        # Get any properties of top window.
        # Set the label for labelVersion
        self.labelVersion.set_label(VERSIONSTR)
        self.can_focus = 'False'

        # Load any settings or run extra initializations.
        self.post_initialisations()

#********* Auto created "class defs" START ************************************************************
#********* Auto created handlers START *********************************
    def on_buttonAbout_clicked(self, widget, *args):
        """ Handler for buttonAbout.clicked. """
        self.MessageBox.AboutBox()

    def on_buttonContinue_clicked(self, widget, *args):
        """ Handler for buttonContinue.clicked. """
        self.msg(_('Experimental'))
        thestr = options.get('last_history','')
        try:
            thehistory = ast.literal_eval(thestr)
        except:
            thehistory = None
        if thehistory:
            self.app.thehistory = thehistory
            tmp = [thehistory[0][x]['num'] for x in thehistory[0]]
            self.app.puzzle_str = ''.join([str(x) if x !=0 else '.' for x in tmp ])
            p = PuzzleWindow(self.app)
            response = p.run()
            self.show()
        else:
            self.msg(_('Not a valid history in conf'))

    def on_buttonExit_clicked(self, widget, *args):
        """ Handler for buttonExit.clicked. """
        self.exit_requested()

    def on_buttonNewPuzzle_clicked(self, widget, *args):
        """ Handler for buttonNewPuzzle.clicked. """
        self.app.thehistory = None
        self.app.puzzle_str = self.get_a_puzzle()
        self.hide()
        p = PuzzleWindow(self.app)
        response = p.run()
        self.show()

    def on_buttonOptions_clicked(self, widget, *args):
        """ Handler for buttonOptions.clicked. """
        p = windowOptions(app = self.app)
        p.set_transient_for(self)
        p.set_modal(True)
        response = p.run()
        #print('options response', response)
        self.reload_options()

    def on_windowMain_delete_event(self, widget, event, *args):
        """ Handler for window1.delete-event. """
        self.set_unhandled_settings()
        return False

    def on_windowMain_destroy(self, widget, *args):
        """ Handler for window1.destroy. """
        self.exit_requested()
        return False

    def on_windowMain_size_allocate(self, widget, allocation, *args):
        """ Handler for window1.size-allocate. """
        self.save_my_size()

    def on_windowMain_window_state_event(self, widget, event, *args):
        """ Handler for window1.window-state-event. """
        settings.set('maximized',
            ((int(event.new_window_state) & Gdk.WindowState.ICONIFIED) != Gdk.WindowState.ICONIFIED) and
            ((int(event.new_window_state) & Gdk.WindowState.MAXIMIZED) == Gdk.WindowState.MAXIMIZED)
            )
        self.save_my_size()


#********* Auto created handlers  END **********************************

    def post_initialisations(self):
        """ Do some extra initializations.

        Display the version if a labelVersion is found.
        Set defaults (try to load them from a configuration file):
            - Window size and state (width, height and if maximized)
        Load saved custom settings.
        """
        # Set previous size and state.
        width = settings.get('width', 350)
        height = settings.get('height', 350)
        self.set_title(self.app.localizedname)
        self.resize(width, height)
        if settings.get_bool('maximized', False):
            self.maximize()
        # Load any other settings here.
        self.reload_options()

    def set_unhandled_settings(self):
        """ Set, before exit, settings not applied during the session.

        Mass set some non critical settings for widgets
        (which where not setted when some widget's state changed).
        """
        #custom settings

    def save_my_size(self):
        """ Save the window size into settings if not maximized. """
        if not settings.get_bool('maximized', False):
            width, height = self.get_size()
            settings.set('width', width)
            settings.set('height', height)

    def exit_requested(self, *args):
        """Set the param in order to exit from "run" method. """
        self.set_transient_for()
        self.set_modal(False)
        self.set_unhandled_settings()
        self.we_can_exit_now = True
        self.destroy()#Will not call Handler for delete-event

    def run(self):
        """Start the main loop.

        WARNING:
            The "destroy" event of the main window
            MUST set the "we_can_exit_now" to True,
            else program will never exit.
        Save settings on exit.
        Return "return_parameter" on exit.

        """
        #now we can show the main window.
        self.show_all()
        #"enable" next line to have some interactive view of potentiallities of GUI
        #self.set_interactive_debugging (True)
        #loop eternaly
        while True:
            #if we want to exit...
            if self.we_can_exit_now:
                #break the loop
                break
            #else... give others a change...
            while Gtk.events_pending():
                Gtk.main_iteration()
        #we can now return to "caller"
        #print(settings)
        settings.save()
        #self.return_parameter = 0 #set return_parameter if needed, last change... to change... it!!!
        #return_parameter should be checked and defined usually before this
        return self.return_parameter

#********* Auto created "class defs" END **************************************************************
    #TODO: get directly from qqwing library.
    def get_a_puzzle(self):
        b = subprocess.run(['qqwing', "--generate", "--difficulty", "easy", "--compact"], stdout=subprocess.PIPE).stdout.decode('utf-8')
        return b.replace('\n','')

    def reload_options(self):
        self.thedicts['custom'] = self.thedicts['standard'].copy()
        tmpcustomdict = options.get('custom_dict', '').split(',')
        if len(tmpcustomdict) == 10 and tmpcustomdict[0].strip() == '':
            self.thedicts['custom'] = ['']
            for x in range (1, 10):
                self.thedicts['custom'].append(tmpcustomdict[x].strip())
        dict_to_use = options.get('dict_to_use', 'standard')
        if dict_to_use in self.thedicts:
            self.app.strings_to_use = self.thedicts[dict_to_use]
        self.app.font_scale = options.get('font_scale', 110)
        self.app.show_simple = options.get('show_simple', False)
        self.app.show_timer = options.get('show_timer', True)
        self.app.show_pieces = options.get('show_pieces', True)
        if self.app.show_simple:
            self.app.show_timer = False
            self.app.show_pieces = False
        if self.app.font_scale < 105 or self.app.font_scale > 250:
            self.app.font_scale = 110
        self.show_info()

    def show_info(self):
        text = 'font_scale:' + str(self.app.font_scale) + '\n'
        text += 'show_simple:' + str(self.app.show_simple) + '\n'
        text += 'show_timer:' + str(self.app.show_timer) + '\n'
        text += 'show_pieces:' + str(self.app.show_pieces) + '\n'
        text += 'strings_to_use:' + str(self.app.strings_to_use)
        self.labelInfo.set_label(text)

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
    app_window = windowMain(app)
    response = app_window.run()
    return response

if __name__ == '__main__':
    #Main entry point if running the program from command line
    # prepare for localization
    tmp = _('standard')
    tmp = _('arabic')
    tmp = _('greek')
    tmp = _('chinese')
    tmp = _('persian')
    tmp = _('tibetan')
    tmp = _('custom')
    tmp = _('Standard')
    tmp = _('Arabic')
    tmp = _('Greek')
    tmp = _('Chinese')
    tmp = _('Persian')
    tmp = _('Tibetan')
    tmp = _('Custom')
    BASE_DIR = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    response = mainAppEntry(BASE_DIR)
    sys.exit(response)

