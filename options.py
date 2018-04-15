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

THEDICTS = {}
THEDICTS['standard'] = [' ','1','2','3','4','5','6','7','8','9']
THEDICTS['arabic'] = [' ','١','٢','٣','٤','٥','٦','٧','٨','٩']
THEDICTS['greek'] = [' ','α','β','γ','δ','ε','ς','ζ','η','θ']
THEDICTS['chinese'] = [' ','一','二','三','四','五','六','七','八','九']
THEDICTS['persian'] = [' ','۱','۲','۳','۴','۵','۶','۷','۸','۹']
THEDICTS['tibetan'] = [ ' ','༡','༢','༣','༤','༥','༦','༧','༨','༩']

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

    # Gtk and related
    from gi import require_version as gi_require_version
    gi_require_version('Gtk', '3.0')
    from gi.repository import Gtk
    from gi.repository import Gdk, GdkPixbuf, Pango
    gi_require_version('PangoCairo', '1.0')
    from gi.repository import PangoCairo
    import cairo

    # Configuration and message boxes
    from auxiliary import SectionConfig, OptionConfig
    from auxiliary import MessageBox

    # Localization
    import locale
    from locale import gettext as _

except ImportError as eximp:
    import_failed(eximp)

settings = None # Keep window related options
options = None #Keep application wide options in a 'General Options' section


class GeneralApp():
    def __init__(self, name='', localizedname='', domain='', BASE_DIR='', version=VERSIONSTR ):
        self.name = name
        self.domain = domain
        self.BASE_DIR = BASE_DIR
        self.version = version
        self.localizedname = ''

class windowOptions(Gtk.Window):
    """ Main window with all components. """

    def __init__(self,  app):
        # Set the app
        self.app =  app

        # Basic initializations.
        self.we_can_exit_now = False
        self.return_parameter = None

        self.fontaspect = 1.85
        self.example_int = 9
        self.example_char = '9'
        self.fontfamily = 'Sans'

        self.thedicts = THEDICTS

        self.current_dict_name = 'standard'

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
            self.builder.add_from_file(os.path.join(self.app.BASE_DIR, 'ui', 'options.glade'))
        except Exception as ex:
            print(str(ex))
            print('\n{}:\n{}\n{}'.format(_('Error loading from Glade file'), os.path.join(self.app.BASE_DIR, 'ui', 'options.glade'), repr(ex)))
            sys.exit(ERROR_INVALID_GLADE_FILE)

        # Get gui objects.
        self.MainBox = self.builder.get_object('MainBox')
        self.adjustment1 = self.builder.get_object('adjustment1')
        self.box1 = self.builder.get_object('box1')
        self.box2 = self.builder.get_object('box2')
        self.box3 = self.builder.get_object('box3')
        self.buttonCancel = self.builder.get_object('buttonCancel')
        self.buttonSave = self.builder.get_object('buttonSave')
        self.checkbuttonShowOnlyBoard = self.builder.get_object('checkbuttonShowOnlyBoard')
        self.checkbuttonShowPieces = self.builder.get_object('checkbuttonShowPieces')
        self.checkbuttonShowTimer = self.builder.get_object('checkbuttonShowTimer')
        self.drawingareaExample = self.builder.get_object('drawingareaExample')
        self.eventbox1 = self.builder.get_object('eventbox1')
        self.eventbox2 = self.builder.get_object('eventbox2')
        self.eventbox3 = self.builder.get_object('eventbox3')
        self.eventbox4 = self.builder.get_object('eventbox4')
        self.eventbox5 = self.builder.get_object('eventbox5')
        self.eventbox6 = self.builder.get_object('eventbox6')
        self.eventbox7 = self.builder.get_object('eventbox7')
        self.eventbox8 = self.builder.get_object('eventbox8')
        self.eventbox9 = self.builder.get_object('eventbox9')
        self.fontbutton1 = self.builder.get_object('fontbutton1')
        self.gridDictionaries = self.builder.get_object('gridDictionaries')
        self.label1 = self.builder.get_object('label1')
        self.label10 = self.builder.get_object('label10')
        self.label2 = self.builder.get_object('label2')
        self.label3 = self.builder.get_object('label3')
        self.label4 = self.builder.get_object('label4')
        self.label5 = self.builder.get_object('label5')
        self.label6 = self.builder.get_object('label6')
        self.label7 = self.builder.get_object('label7')
        self.label8 = self.builder.get_object('label8')
        self.label9 = self.builder.get_object('label9')
        self.labeltest = self.builder.get_object('labeltest')
        self.radiobuttonDict1 = self.builder.get_object('radiobuttonDict1')
        self.scale1 = self.builder.get_object('scale1')
        self.scrolledwindow1 = self.builder.get_object('scrolledwindow1')
        self.viewport1 = self.builder.get_object('viewport1')


        # Connect signals existing in the Glade file
        self.builder.connect_signals(self)

        # Reparent our main container from glader file,
        # this way we have all Gtk.Window functionality using "self".
        thechild = self.builder.get_object('windowOptions').get_child()
        thechild.get_parent().remove(thechild)
        self.add(thechild)

        # Connect generated signals.
        self.buttonCancel.connect('clicked', self.on_buttonCancel_clicked)
        self.buttonSave.connect('clicked', self.on_buttonSave_clicked)
        self.connect('delete-event', self.on_windowOptions_delete_event)
        self.connect('destroy', self.on_windowOptions_destroy)
        self.connect('size-allocate', self.on_windowOptions_size_allocate)
        self.connect('window-state-event', self.on_windowOptions_window_state_event)


        # Get any properties of top window.
        self.can_focus = 'False'

        # Load any settings or run extra initializations.
        self.post_initialisations()

#********* Auto created "class defs" START ************************************************************
#********* Auto created handlers START *********************************
    def on_adjustment1_changed(self, widget, *args):
        """ Handler for adjustment1.changed. """
        print(widget.value)

    def on_buttonCancel_clicked(self, widget, *args):
        """ Handler for buttonCancel.clicked. """
        self.exit_requested()

    def on_buttonSave_clicked(self, widget, *args):
        """ Handler for buttonSave.clicked. """
        self.set_unhandled_settings()
        self.exit_requested()

    def on_checkbuttonShowOnlyBoard_toggled(self, widget, *args):
        """ Handler for checkbuttonShowOnlyBoard.toggled. """
        boolval = self.checkbuttonShowOnlyBoard.get_active()
        self.checkbuttonShowPieces.set_sensitive(not boolval)
        self.checkbuttonShowTimer.set_sensitive(not boolval)

    def on_drawingareaExample_draw(self, widget, cr, *args):
        """ Handler for drawingareaExample.draw. """
        self.draw_example(cr)

    def on_fontbutton1_font_set(self, widget, *args):
        """ Handler for fontbutton1.font-set. """
        self.fontfamily = self.fontbutton1.get_font_name()
        print(self.fontfamily)
        self.drawingareaExample.queue_draw()

    def on_NUM_button_press_event(self, widget, event, *args):
        """ Handler for eventbox8.button-press-event. """
        self.example_int = int(widget.get_child().get_label())
        self.drawingareaExample.queue_draw()

    def on_radiobuttonDict1_toggled(self, widget, *args):
        """ Handler for any button in group radiobuttonDict1.toggled. """
        if widget.get_active():
            self.current_dict_name = widget.tag
            self.drawingareaExample.queue_draw()

    def on_scale1_change_value(self, widget, scroll, new_value, *args):
        """ Handler for scale1.change-value. """

        val = new_value# (new_value /100 ) * 1.45
        if val > 2.5:
            val = 2.5
        elif val < 1.:
            val = 1.
        self.fontaspect = val
        self.drawingareaExample.queue_draw()

    def on_windowOptions_delete_event(self, widget, event, *args):
        """ Handler for windowOptions.delete-event. """
        return False

    def on_windowOptions_destroy(self, widget, *args):
        """ Handler for windowOptions.destroy. """
        self.exit_requested()
        return False

    def on_windowOptions_size_allocate(self, widget, allocation, *args):
        """ Handler for windowOptions.size-allocate. """
        self.save_my_size()

    def on_windowOptions_window_state_event(self, widget, event, *args):
        """ Handler for windowOptions.window-state-event. """
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
        # Load a saved or empty custom dict
        self.thedicts['custom'] = self.thedicts['standard'].copy()
        tmpcustomdict = options.get('custom_dict', '').split(',')
        if len(tmpcustomdict) == 10 and tmpcustomdict[0].strip() == '':
            self.thedicts['custom'] = ['']
            for x in range (1, 10):
                self.thedicts['custom'].append(tmpcustomdict[x].strip())
        self.show_dicts()
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#228b22"))#forest green

        simple = options.get('show_simple', False )
        self.checkbuttonShowPieces.set_active(not simple and options.get('show_pieces', False))
        self.checkbuttonShowTimer.set_active(not simple and options.get('show_timer', True))
        self.checkbuttonShowOnlyBoard.set_active(simple)
        scale = options.get('font_scale', 100)
        self.adjustment1.set_value(scale / 100)
        self.fontaspect = self.adjustment1.get_value()

        digits_dict = options.get('dict_to_use', 'standard')
        for b in self.gridDictionaries.get_children():
            if hasattr(b, 'tag') and b.tag == digits_dict:
                b.set_active(True)
                break

    def set_unhandled_settings(self):
        """ Set, before exit, settings not applied during the session.

        Mass set some non critical settings for widgets
        (which where not setted when some widget's state changed).
        """
        #custom settings
        options.set('dict_to_use', self.current_dict_name)
        #print(','.join(self.thedicts['custom']))
        options.set('custom_dict', ','.join(self.thedicts['custom']))
        scale = self.adjustment1.get_value()
        options.set('font_scale', int(scale * 100))
        boolval = self.checkbuttonShowOnlyBoard.get_active()
        options.set('show_simple', boolval )
        options.set('show_pieces', (not boolval) and self.checkbuttonShowPieces.get_active())
        options.set('show_timer', (not boolval) and self.checkbuttonShowTimer.get_active())

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
    def on_any_custom_changed(self, widget, *args):
        index = widget.entry_tag
        char = widget.get_text()
        self.thedicts['custom'].pop(index)
        self.thedicts['custom'].insert(index,char)

    def show_dicts(self):
        """ Load and show the dictionaries.

        Load all from self.thedicts except 'standard' and 'custom'.
        """
        thegrid = self.gridDictionaries
        ycounter = 1
        self.radiobuttonDict1.tag = 'standard'
        for adict in sorted(self.thedicts, key=sorting):
            if adict != 'standard':
                theoption = Gtk.RadioButton(_(adict.title()))
                theoption.join_group(self.radiobuttonDict1)
                theoption.connect('toggled', self.on_radiobuttonDict1_toggled, theoption)
                #theoption.connect('toggled', self.on_radiobuttonDict1_toggled)
                theoption.tag = adict
                thegrid.attach(theoption,0,ycounter,1,1)
                xcounter = 1
                if adict == 'custom':
                    for x in range(9):
                        w = Gtk.Entry()
                        w.set_text(self.thedicts[adict][x+1])
                        w.set_width_chars(1)
                        w.set_max_width_chars(1)
                        w.entry_tag = x+1
                        w.connect('changed', self.on_any_custom_changed)
                        thegrid.attach(w,xcounter,ycounter,1,1)
                        xcounter += 1
                else:
                    for x in range(9):
                        label = Gtk.Label(self.thedicts[adict][x+1])
                        thegrid.attach(label,xcounter,ycounter,1,1)
                        xcounter += 1
                ycounter += 1

    def draw_example(self, cr):
        #thedict = self.thedicts[self.current_dict_name]
        #self.example_char = thedict[self.example_int]

        size = self.drawingareaExample.get_allocated_height()/2
        startx = 0
        starty = 0
        cr.set_line_width(2)
        for colcounter in range(2):
            for rowcounter in range(2):
                num = colcounter * 2 + rowcounter
                if num == 0:
                    cr.set_source_rgba(0,0.5,1,0.10)
                elif num == 1:
                    cr.set_source_rgb(0.85,0.85,0.85)
                else:
                    cr.set_source_rgb(1,1,1)
                cr.rectangle(colcounter * size , rowcounter * size, size, size)
                cr.fill()
                cr.rectangle(colcounter * size , rowcounter * size, size, size)
                cr.set_source_rgb(0,0,0)
                cr.stroke()

        #samplechar = str(self.example_int)
        samplechar = ['1','8','7','9']
        samplechar2 = '8'
        font_size = size * 1./self.fontaspect
        cr.select_font_face("Monospace",
            cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(font_size)
        for colcounter in range(2):
            for rowcounter in range(2):
                num = colcounter * 2 + rowcounter
                the_x = colcounter * size
                the_y = rowcounter * size

                x_bearing, y_bearing, d_width, d_height = cr.text_extents(samplechar[num])[:4]
                d_x = (size - d_width)/2 + startx + the_x - x_bearing
                d_y = (size - d_height)/2 + starty + the_y - y_bearing
                cr.move_to(d_x, d_y)
                cr.show_text(samplechar[num])

#********* Window class  END***************************************************************************
def sorting(akey):
    return _(akey)
