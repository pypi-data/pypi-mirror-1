#!/usr/bin/env python
"""RunPON - runs pon/poff scripts and shows the running time.
    http://erlug.linux.it/~da/soft/runpon/

    Copyright (C) 2009 Davide Alberani <da@erlug.linux.it>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import time
import commands
import ConfigParser
import warnings
from collections import defaultdict

import pygtk
pygtk.require('2.0')
import gtk
import gobject

__version__ = VERSION = '0.4'

HAS_GNOMEAPPLET = True
try:
    import gnomeapplet
except ImportError, e:
    HAS_GNOMEAPPLET = False
    warnings.warn('Unable to import gnomeapplet: %s' % e)


# If True, it doesn't execute any command.
DONT_RUN = False
#DONT_RUN = True

# Where the configuration file resides.  TODO: adjust it for MS Windows?
CONFIG_DIR = os.path.join('~', '.config', 'runpon')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'runpon.cfg')

# Default values for the configuration file.
CONFIG_DEFAULTS = {
    # Commands to be executed.
    'on': 'pon',
    'off': 'poff',
    # Interface to check.
    'check_interface': 'ppp0',
    # Run the 'off' command if the interface is no more with us.
    'run_off_if_fails': 'true',
    # Run the 'off' command at exit, if the timer is still running.
    'run_off_at_exit': 'true',
    # Check the interface every X seconds.
    'check_interval': '10',
    # Don't check the interface for the first X seconds; otherwise, if the
    # check is performed while the interface is not yet up, the 'off' command
    # will be called (only if 'run_off_if_fails' is True).
    # Keep it large enough. :-)
    'check_grace_time': '20',
    # Cumulative time (in seconds) of the connection.
    'cumulative_time': '0',
    # Length, in seconds, of a time slot.
    'cumulative_time_slot': '1'
}

# Default sections created in the configuration file.
_DEFAULT_OPTIONS = {'active': 'runpon'}
_DEFAULT_OPTIONS.update(CONFIG_DEFAULTS)
CONFIG_SECTIONS = {
    'DEFAULT': _DEFAULT_OPTIONS,
    'runpon': CONFIG_DEFAULTS
}

# Update the label every X seconds.
INTERVAL = 1

# Command used to check if the interface is up.  The %s placeholder (mandatory!)
# is replaced with the interface.  The command must return 0 in case of success.
IF_CHECK_CMD = 'ifconfig "%s"'

# Labels for the button.
BTN_ON_LABEL = 'on ' # keep the trailing space. :-)
BTN_OFF_LABEL = 'off'
# Text colors.
LABEL_OK_COL = gtk.gdk.color_parse('black')
LABEL_ERR_COL = gtk.gdk.color_parse('red') # used in case of errors.

PRG_NAME = 'RunPON'
RUNPON_HELP = """%s [%s] - runs pon/poff scripts and shows the running time.
         http://erlug.linux.it/~da/soft/runpon/

    -w (--window)   runs in a plain old window (default).
    -t (--tray)     shows only the status icon on the tray.
    -n (--no-tray)  doesn't show the status icon on the tray.
    -h (--help)     get this help and exits.

    To run it as a Gnome panel applet, see README.txt.

    The configuration settings are stored in %s
""" % (PRG_NAME, VERSION, CONFIG_FILE)

# Schema to build the menus.
menuSchema = ['start', 'stop', None, 'preferences', None, 'quit']
# Menu icons.
menuIcons = {'start': 'gtk-media-play',
            'stop': 'gtk-media-stop',
            'preferences': 'gtk-properties',
            'quit': 'gtk-quit'}

# Text used in the tooltips.
TOOLTIP_TXT = '%s (total minutes: %d)'

# bz2-ipped, base64-encoded representation of the configuration
# interface, created with Glade and saved in the runpon-cfg.glade
# file.
CFG_GTKBUILDER = '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\n'
# Read it from a file (to speed-up debugging).
#CFG_GTKBUILDER = open('/home/da//mercurial/runpon/runpon-cfg.glade', 'r').read().encode('bz2').encode('base64')


class RunPONConfigParser(ConfigParser.ConfigParser):
    """Custom configuration parser."""
    def getValue(self, key, converter=None, default=None):
        """Return the value of the specified key, looking first into the
        active section (specified with the 'active' option of the 'DEFAULT'
        section.

        *key*       the key to search for.
        *converter* a callable that will be applied to the return value.
        *default*   the default value to return if the key is not found."""
        if converter is bool and default is None:
            default = False
        try:
            active = self.getActiveSection()
            # Get the value from the active section.
            value = self.get(active, key)
            if not value:
                return default
            if converter:
                try:
                    if converter is bool:
                        value = self._boolean_states[value.lower()]
                    else:
                        value = converter(value)
                except Exception:
                    return default
            return value
        except ConfigParser.Error:
            return default

    def setValue(self, option, value):
        """Set a value in the active section."""
        active = self.getActiveSection()
        self.set(active, option, value)

    def getActiveSection(self):
        """Return the active section (DEFAULT is the fall-back option)."""
        try:
            # First of all, tries to identify the active section; if it's
            # not set, falls back to DEFAULT.
            active = self.get('DEFAULT', 'active')
            if not self.has_section(active):
                active = 'DEFAULT'
        except ConfigParser.Error:
            active = 'DEFAULT'
        return active

    def addSection(self, section):
        """Add a new section, populating it with default values."""
        try:
            self.add_section(section)
        except ConfigParser.DuplicateSectionError:
            return
        for key, value in CONFIG_DEFAULTS.items():
            self.set(section, key, value)


def manageConfigFile():
    """Return a ConfigParser instance, reading values from a file and
    creating it, if it doesn't exist."""
    confFN = os.path.expanduser(CONFIG_FILE)
    _creating = False
    _gotFile = True
    try:
        cfgFile = open(confFN, 'rw')
    except (IOError, OSError):
        # We're trying to create the file.
        _creating = True
        try:
            os.makedirs(os.path.expanduser(CONFIG_DIR))
        except (IOError, OSError):
            pass
        try:
            cfgFile = open(confFN, 'w+')
        except (IOError, OSError):
            # Uh-oh! We can't get a file - go on the the default values.
            _gotFile = False
    config = RunPONConfigParser()
    if _gotFile:
        config.readfp(cfgFile)
    if _creating:
        # Populate the new configuration object.
        for section, options in CONFIG_SECTIONS.items():
            if section != 'DEFAULT':
                config.add_section(section)
            for key, value in options.items():
                config.set(section, key, value)
        if _gotFile:
            config.write(cfgFile)
    return config


def executeCommand(cmdLine, _force=False):
    """Execute the given command line, returning a (status, output) tuple.
    If an exception is caught, status is set to None and output to a string
    representing the exception.  If _force is True the command is executed
    even if DONT_RUN is True."""
    if DONT_RUN and not _force:
        print 'I WOULD RUN', cmdLine
        return 0, ''
    try:
        status, output = commands.getstatusoutput(cmdLine)
    except Exception, e:
        status, output = None, str(e)
    return status, output


class Timer(object):
    """Keep track of the elapsed time."""
    # Today is the first day of... the Epoch.
    _timeZero = time.gmtime(0)

    def __init__(self, initSec=None, running=False, format='%H:%M:%S'):
        """Initialize the Timer instance.

        *initSec*   float representation of time (current time, if None).
        *running*   the timer is running? (False by default).
        *format*    format of the displayed time."""
        self.running = running
        if initSec is None:
            self.reset()
        self.initSec = initSec
        self.format = format

    def getTime(self, format=None):
        """Return the elapsed time in the specified format."""
        if format is None:
            format = self.format
        if self.running:
            diffTime = time.gmtime(float(self))
        else:
            # A nice '00:00:00' or something like that.
            diffTime = self._timeZero
        return time.strftime(format, diffTime)

    def reset(self):
        """Reset the timer."""
        self.initSec = time.time()

    def start(self):
        """Start the timer."""
        self.running = True

    def restart(self):
        """Restart the timer."""
        self.reset()
        self.start()

    def stop(self):
        """Stop the timer."""
        self.running = False

    def setStatus(self, status):
        """Set the running status; it can be 'on' or 'off'."""
        if status == 'on':
            self.restart()
        elif status == 'off':
            self.stop()

    def __str__(self):
        """Return the elapsed time as a string."""
        return self.getTime()

    def __int__(self):
        """Return the elapsed time as an integer."""
        return int(time.time() - self.initSec)

    def __float__(self):
        """Return the elapsed time as a float."""
        return time.time() - self.initSec

    def __cmp__(self, other):
        """Numeric comparisons."""
        _fs = float(self)
        if _fs < other:
            return -1
        if _fs > other:
            return 1
        return 0


class Observable(defaultdict):
    """Event dispatcher.  Not-so-loosely based on:
    http://en.wikipedia.org/wiki/Observer_pattern ."""
    def __init__(self, *args, **kwds):
        """Initialize the instance."""
        # Values are assumed to be Python objects (callables, hopefully).
        super(Observable, self).__init__(object, *args, **kwds)

    def register(self, subscriber):
        """Register a new subscriber to this event."""
        self[subscriber]

    def notify(self, *args, **kwds):
        """Notify every subscriber of the event, storing the result."""
        for subscriber in self:
            # XXX: so far, storing the return is useless.
            #      Catch every exception?
            self[subscriber] = subscriber(*args, **kwds)


class RunPONToggleButton(gtk.ToggleButton):
    """The on/off ToggleButton for RunPON."""
    def __init__(self, onOffObservable, *args, **kwds):
        """Initialize the instance.

        *onOffObservable*   on/off event handler.
        """
        super(RunPONToggleButton, self).__init__(*args, **kwds)
        self._signalsFromOuterSpace = False
        self.set_label(BTN_ON_LABEL)
        onOffObservable.register(self.receiveOnOff)
        self.onOffObservable = onOffObservable
        self.connect('toggled', self.changeStatus)
        self.show()

    def receiveOnOff(self, status):
        """Receive on/off notifications."""
        self._signalsFromOuterSpace = True
        isActive = self.get_active()
        # Notice that the on/off signal can be received both from other
        # sources (the right-click menu, for example) and _ourselves_,
        # so we need to switch the status only if the signal is from an
        # outer source.
        if not ((status == 'on' and isActive) or
                (status == 'off' and not isActive)):
            # set_active triggers the 'toggled' signal.
            self.set_active(not isActive)
        self._signalsFromOuterSpace = False

    def changeStatus(self, data=None):
        """Handler for the 'toggled' signal."""
        # Notice that the on/off signal is _not_ triggered another time,
        # if it was received from another source.
        if not self.get_active():
            if not self._signalsFromOuterSpace:
                self.onOffObservable.notify('off')
            self.set_label(BTN_ON_LABEL)
        else:
            if not self._signalsFromOuterSpace:
                self.onOffObservable.notify('on')
            self.set_label(BTN_OFF_LABEL)


class RunPONTimeLabel(gtk.Label):
    """The Label used by RunPON to display the elapsed time."""
    def __init__(self, timeObservable, onOffObservable, errorObservable,
                 label, *args, **kwds):
        """Initialize the instance.

        *timeObservable*    even handler used to update the displayed time.
        *onOffObservable*   on/off event handler.
        *errorObservable*   handler for error messages.
        *label*             the initial text of this label.
        """
        super(RunPONTimeLabel, self).__init__(*args, **kwds)
        self.changeTextColor(LABEL_OK_COL)
        self.set_label(label)
        timeObservable.register(self.setLabel)
        onOffObservable.register(self.handleOnOff)
        errorObservable.register(self.handleError)
        self.show()

    def setLabel(self, label, cumulative):
        self.set_label(label)
        self.set_tooltip_text(TOOLTIP_TXT % (label, cumulative))

    def handleOnOff(self, status):
        """Handle actions to be taken when the running status is changed."""
        if status == 'on':
            self.changeTextColor(LABEL_OK_COL)

    def handleError(self, error, *args, **kwds):
        """Handle errors."""
        if error == 'if down':
            self.changeTextColor(LABEL_ERR_COL)
            self.set_tooltip_text('%s E' % self.get_tooltip_text())

    def changeTextColor(self, color):
        """Set the color of the text."""
        self.modify_fg(gtk.STATE_NORMAL, color)


class RunPONRightClickMenu(gtk.Menu):
    """A menu shown clicking on the label with the right mouse button."""
    def __init__(self, onOffObservable, miscActionsObservable, *args, **kwds):
        """Initialize the instance.

        *onOffObservable*   on/off event handler.
        """
        super(RunPONRightClickMenu, self).__init__(*args, **kwds)
        # True if the menu is present (will be set to False when running
        # as an applet, since the menu must be integrated with the one
        # provided by the panel).
        self.isPresent = True
        onOffObservable.register(self.modifyMenu)
        # Callbacks for some menu entries.
        _cb = {'start': lambda x: onOffObservable.notify('on'),
               'stop': lambda x: onOffObservable.notify('off'),
               'preferences': lambda x: \
                       miscActionsObservable.notify('show-cfg'),
               'quit': lambda x: miscActionsObservable.notify('destroy')}
        for menuItem in menuSchema:
            if menuItem is not None:
                mi = gtk.ImageMenuItem(menuItem.capitalize())
                icon = menuIcons.get(menuItem)
                if icon:
                    img = gtk.Image()
                    img.set_from_stock(icon, gtk.ICON_SIZE_MENU)
                    mi.set_image(img)
            else:
                mi = gtk.SeparatorMenuItem()
            fCall = _cb.get(menuItem)
            if fCall:
                mi.connect('activate', fCall)
            if menuItem == 'start':
                self.startItem = mi
            elif menuItem == 'stop':
                mi.set_sensitive(False)
                self.stopItem = mi
            self.append(mi)
        self.show_all()

    def modifyMenu(self, status):
        """Set the state of some elements of the menu, accordingly with
        the running status."""
        self.startItem.set_sensitive(True)
        self.stopItem.set_sensitive(True)
        if status == 'on':
            self.startItem.set_sensitive(False)
        elif status == 'off':
            self.stopItem.set_sensitive(False)

    def showMenu(self, widget, event, data=None):
        """Pop-up the menu, if the third mouse button was pressed."""
        if not self.isPresent:
            return False
        if event.button != 3:
            return False
        self.show()
        self.popup(None, None, None, event.button, event.time, None)


class RunPONEventBox(gtk.EventBox):
    """An EvenBox, use to wrap the RunPONTimeLabel instance."""
    def __init__(self, timeLabel, menu, *args, **kwds):
        """Initialize the instance.

        *timeLabel*     the label we're wrapping.
        *menu*          the menu to be shown.
        """
        super(RunPONEventBox, self).__init__(*args, **kwds)
        self.add(timeLabel)
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect('button_press_event', menu.showMenu)
        self.show()


class RunPON(gtk.HBox):
    """The main RunPON element, a HBox wrapping the label (inside an EventBox)
    and the ToggleButton."""

    # Methods to be called getting/setting values from/into the configuration GUI.
    _CFG_MAP_GET_VALUE = {
        gtk.Entry: gtk.Entry.get_text,
        gtk.CheckButton: gtk.CheckButton.get_active,
        gtk.SpinButton: gtk.SpinButton.get_value_as_int,
        gtk.ComboBox: gtk.ComboBox.get_active_text
    }

    _CFG_MAP_SET_VALUE = {
        gtk.Entry: gtk.Entry.set_text,
        gtk.CheckButton: gtk.CheckButton.set_active,
        gtk.SpinButton: gtk.SpinButton.set_value,
        gtk.ComboBox: gtk.ComboBox.set_active,
        gtk.Label: gtk.Label.set_text
    }

    def __init__(self, config, *args, **kwds):
        """Initialize the instance."""
        super(RunPON, self).__init__(*args, **kwds)
        # The configuration.
        self.cfg = config
        # Our beloved timer.
        self.timer = Timer()
        # Event handler expected to be called with a string representing
        # the text to display on the label.
        self.timeObservable = Observable()
        # Event handler expected to be called with a 'on'/'off' string parameter.
        self.onOffObservable = Observable()
        self.onOffObservable.register(self.timer.setStatus)
        self.onOffObservable.register(self.runCommand)
        self.onOffObservable.register(self.updateCumulativeTime)
        # Miscellaneous actions observable.
        self.miscActionsObservable = Observable()
        self.miscActionsObservable.register(self.handleMiscActions)
        # Event handler for errors (called with a string representing the error).
        self.errorObservable = Observable()
        # The label used to display our information.
        self.timeLabel = RunPONTimeLabel(self.timeObservable,
                                         self.onOffObservable,
                                         self.errorObservable,
                                         str(self.timer))
        self.onOffButton = RunPONToggleButton(self.onOffObservable)
        self.menu = RunPONRightClickMenu(self.onOffObservable,
                                         self.miscActionsObservable)
        self.eventBox = RunPONEventBox(self.timeLabel, self.menu)
        self.add(self.eventBox)
        self.add(self.onOffButton)
        # XXX: needed only when running as an applet?
        self.connect('destroy', lambda *x: self.handleMiscActions('destroy'))
        # If True, values in the self.cfg object are not updated; useful to
        # avoid updates triggered by setting in the code (and not in the GUI).
        self._dontSetCfg = False
        self.show()

    def buildCfgWindow(self):
        """Create the configuration window."""
        # Build it from the GTK Builder XML.
        self.builder = gtk.Builder()
        decodeXML = CFG_GTKBUILDER.decode('base64').decode('bz2')
        self.builder.add_from_string(decodeXML)
        self.cfgWindow = self.builder.get_object('window-runpon-cfg')
        # Signals for some events.
        signals = {'setting_changed': self.modifySetting,
                   'section_changed': self.cfgShowValues,
                   'save': lambda *x: \
                           self.miscActionsObservable.notify('save-cfg'),
                    'save_close': lambda *x: \
                           self.miscActionsObservable.notify('save-close'),
                    'reset_cumultime': lambda *x: \
                            self.miscActionsObservable.notify('reset-cumul'),
                    'section_new': lambda *x: \
                            self.miscActionsObservable.notify('section-new'),
                    'section_delete': lambda *x: \
                            self.miscActionsObservable.notify('section-delete')
        }
        self.initCfgWindow()
        self.builder.connect_signals(signals)
        self.cfgShowValues()

    def initCfgWindow(self):
        """Initialize the configuration window."""
        self._dontSetCfg = True
        # Set the list of sections.
        self._cfgCBSection = self.builder.get_object('combobox-section')
        self._cfgLSSection = self.builder.get_object('liststore-section')
        self._cfgLSSection.clear()
        self._cfgLSSection.append(['DEFAULT'])
        for sect in self.cfg.sections():
            self._cfgLSSection.append([sect])
        self._cfgCBSection.set_active(0)
        self._dontSetCfg = False

    def _getActiveSection(self):
        """Return the active section name, or None in case of error."""
        try:
            selected = self._cfgCBSection.get_active()
            if selected == -1:
                return None
            section =   self._cfgLSSection[selected][0]
        except Exception:
            section = None
        return section

    def cfgShowValues(self, *args, **kwds):
        """Set values in the configuration window so that they match the
        current active configuration."""
        self._dontSetCfg = True
        section =  self._getActiveSection()
        if not section:
            self._dontSetCfg = False
            return
        for key, value in self.cfg.items(section):
            widget = self.builder.get_object(key)
            ##print 'SHOW', section, key, value
            widgetClass = widget.__class__
            if widgetClass is gtk.CheckButton:
                if isinstance(value, (str, unicode)) and value.lower() in \
                        self.cfg._boolean_states:
                    value = self.cfg._boolean_states[value.lower()]
                else:
                    value = bool(value)
            elif widgetClass is gtk.SpinButton:
                try:
                    value = float(value)
                except Exception:
                    value = 0.0
            elif widgetClass is gtk.ComboBox and key == 'active':
                if section == 'DEFAULT':
                    lsas = self.builder.get_object('liststore-active-section')
                    lsas.clear()
                    sections = self.cfg.sections()
                    for sect in sections:
                        lsas.append([sect])
                    try:
                        value = sections.index(value)
                    except ValueError:
                        value = -1
                    widget.set_sensitive(True)
                else:
                    value = -1
                    self.builder.get_object('liststore-active-section').clear()
                    widget.set_sensitive(False)
            self._CFG_MAP_SET_VALUE[widgetClass](widget, value)
        self._dontSetCfg = False

    def modifySetting(self, widget, *args, **kwds):
        """Handle events generated when a user is playing with the
        configuration GUI."""
        if self._dontSetCfg:
            return
        option = widget.get_name()
        section =  self._getActiveSection()
        if not section:
            return
        widgetClass = widget.__class__
        if widgetClass is gtk.ComboBox and section != 'DEFAULT':
            return
        value = self._CFG_MAP_GET_VALUE[widgetClass](widget)
        if isinstance(value, float):
            value = int(value)
        ##print 'SET', section, option, value
        self.cfg.set(section, option, str(value))

    def handleMiscActions(self, action, *args, **kwds):
        """Handler for miscellaneous actions."""
        if action == 'show-cfg':
            # XXX: re-create the whole Window - only hide it?
            self.buildCfgWindow()
            #self.initCfgWindow()
            self.cfgWindow.show_all()
        elif action == 'save-cfg':
            try:
                confFN = os.path.expanduser(CONFIG_FILE)
                confFd = open(confFN, 'w')
                self.cfg.write(confFd)
            except (IOError, OSError):
                pass
            finally:
                confFd.close()
        elif action == 'save-close':
            self.handleMiscActions('save-cfg')
            self.cfgWindow.hide()
        elif action == 'reset-cumul':
            section =  self._getActiveSection()
            if section in ('DEFAULT', None):
                return
            cumulTimeLabel = self.builder.get_object('cumulative_time')
            self.cfg.set(section, 'cumulative_time', '0')
            cumulTimeLabel.set_text('0')
        elif action == 'section-delete':
            section = self._getActiveSection()
            if section in ('DEFAULT', None):
                return
            self.cfg.remove_section(section)
            self.handleMiscActions('save-cfg')
            self.initCfgWindow()
            self._dontSetCfg = True
            self._cfgCBSection.set_active(0)
            self._dontSetCfg = False
        elif action == 'section-new':
            entryNewSection = self.builder.get_object('entry-new-section')
            name = entryNewSection.get_text()
            if name:
                name = name.strip()
            if name.lower() in ('default', ''):
                return
            self.cfg.addSection(name)
            self.handleMiscActions('save-cfg')
            entryNewSection.set_text(u'')
            self.initCfgWindow()
            newIdx = [x[0] for x in self._cfgLSSection].index(name)
            self._dontSetCfg = True
            self._cfgCBSection.set_active(newIdx)
            self._dontSetCfg = False
        elif action == 'destroy':
            if self.cfg.getValue('run_off_at_exit', converter=bool) and \
                    self.timer.running:
                self.onOffObservable.notify('off')
            gtk.main_quit()

    def updateTime(self):
        """Update the displayed time (this method is called by
        a gobject timer)."""
        # Remember to always return True.
        if not self.timer.running:
            return True
        cumulTime = self.getCumulativeTime() / 60
        # Notify a label to be displayed and the cumulative time in minutes.
        self.timeObservable.notify(str(self.timer), cumulTime)
        return True

    def checkIF(self):
        """Check if the interface is up, updating the status accordingly (this
        method is called by a gobject timer)."""
        # Remember to always return True.
        graceTime = self.cfg.getValue('check_grace_time', converter=int,
                                      default=0)
        if not self.timer.running or self.timer < graceTime:
            return True
        ifName = self.cfg.getValue('check_interface')
        if not ifName:
            return True
        status, output = executeCommand(IF_CHECK_CMD % ifName, _force=True)
        if status != 0:
            self.errorObservable.notify('if down', status=status,
                                        output=output)
            print 'ERROR on "%s" interface: %s' % (ifName, output)
            if status is not None:
                if self.cfg.getValue('run_off_if_fails', converter=bool):
                    self.onOffObservable.notify('off')
        return True

    def runCommand(self, status):
        """Execute a command, in response to an on/off event."""
        if status == 'on':
            executeCommand(self.cfg.getValue('on'))
        elif status == 'off':
            executeCommand(self.cfg.getValue('off'))

    def getCumulativeTime(self):
        """Return the cumulative connection time in seconds; the value is
        rounded to the upper value, considering slots of time of the
        configured length."""
        curCumulTime = self.cfg.getValue('cumulative_time', converter=int,
                                         default=0)
        curTime = int(self.timer)
        timeSlot = self.cfg.getValue('cumulative_time_slot', converter=int,
                                     default=1)
        if timeSlot < 1:
            timeSlot = 1
        div, mod = divmod(curTime, timeSlot)
        curTime = (div * timeSlot) + (0, timeSlot)[bool(mod)] # Look ma'! ;-)
        curCumulTime += curTime
        return curCumulTime

    def updateCumulativeTime(self, status):
        """Update the cumulative running time, stored in the configuration
        file."""
        if status != 'off' or DONT_RUN:
            return
        curCumulTime = self.getCumulativeTime()
        self.cfg.setValue('cumulative_time', str(curCumulTime))
        self.miscActionsObservable.notify('save-cfg')


class RunPONWindow(gtk.Window):
    """Class used when RunPON is run as a stand-alone application."""
    def __init__(self, content, withTray, hideWindow, *args, **kwds):
        """Initialize the instance.

        *content*   things we have to put inside this window."""
        super(RunPONWindow, self).__init__(*args, **kwds)
        if withTray:
            try:
                self.statusIcon = RunPONTray(content, self.toggleVisibility)
            except Exception, e:
                warnings.warn('Unable to activate status icon: %s' % e)
        self.connect('delete_event', lambda x, y: \
                                content.miscActionsObservable.notify('destroy'))
        content.timeObservable.register(lambda x, y: self.set_title(x))
        content.errorObservable.register(self.handleError)
        self.add(content)
        if not hideWindow:
            self.show()
        else:
            self.hide()

    def toggleVisibility(self):
        """Toggle the visiblity of the main window."""
        if self.get_property('visible'):
            self.hide()
        else:
            self.show()

    def handleError(self, error, *args, **kwds):
        """Handler for errors."""
        if error == 'if down':
            self.set_title('%s E' % self.get_title())


class RunPONTray(gtk.StatusIcon):
    """Class used to show the status icon in the tray."""
    def __init__(self, content, toggleVisibility, *args, **kwds):
        """Initialize the instance.

        *content*           things we have to put inside this window.
        *toggleVisibility*  function to call to toggle visibility of the
                            main window.
        """
        super(RunPONTray, self).__init__(*args, **kwds)
        self._lastTooltip = ''
        content.timeObservable.register(self.handleTooltipUpdate)
        content.errorObservable.register(self.handleError)
        self.content = content
        self.set_from_stock(gtk.STOCK_NETWORK)
        self.connect('button_press_event', self.handleClicks)
        # I don't like it at all: having here a method of RunPONWindow
        # seems wrong.  Use an Observable?
        self.toggleVisibility = toggleVisibility
        self.set_visible(True)

    def handleClicks(self, widget, event, data=None):
        """Handle mouse button events."""
        if event.button == 3:
            self.content.menu.showMenu(widget, event, data)
        elif event.button == 1:
            self.toggleVisibility()

    def handleTooltipUpdate(self, label, cumulative):
        """Update the tooltip, and stores it (useful in case of errors)."""
        self._lastTooltip = label
        self.set_tooltip(TOOLTIP_TXT % (label, cumulative))

    def handleError(self, error, *args, **kwds):
        """Handle errors."""
        self.set_tooltip('%s E' % self._lastTooltip)


def buildXmlMenu(ms, **kwds):
    """Return a XML menu for our gnome panel applet; kwds can be set to
    False if the named entry is supposed to be deactivated."""
    menu = '<popup name="button3">\n    %s\n</popup>'
    mEntry = '<menuitem name="Item %d" verb="%s" label="%s" pixtype="%s" '
    mEntry += 'pixname="%s" />'
    _separator = '<separator />'
    _pixtypes = {}
    items = []
    count = 1
    for mi in ms:
        if mi is None:
            items.append(_separator)
            continue
        if kwds.get(mi) is False:
            # XXX: is there a way to show a non-sensitive item?
            #      Silly XML schema for menus!  Where the hell is it documented?
            continue
        pixtype = _pixtypes.get(mi, 'stock')
        pixname = menuIcons.get(mi, 'gtk-properties')
        items.append(mEntry % (count, mi, mi.capitalize(), pixtype, pixname))
        count += 1
    # Remove duplicated consecutive (and trailing) separators.
    _slimItems = []
    for item in items:
        if item == _separator and _slimItems and _slimItems[-1] == _separator:
            continue
        _slimItems.append(item)
    if _slimItems and _slimItems[-1] == _separator:
        _slimItems = _slimItems[:-1]
    return menu % '\n    '.join(_slimItems)


def makeAppletOnOffCallback(applet, onOffObservable, miscActionsObservable):
    """Build a function that will react to on/off and other events,
    modifying the applet's menu accordingly."""
    def _cb(status):
        """Callback to modify the applet's menu."""
        kwds = {'start': True, 'stop': False, 'preferences': True,
                'quit': False}
        _startCb = lambda x, y: onOffObservable.notify('on')
        _stopCb = lambda x, y: onOffObservable.notify('off')
        _showCfg = lambda x, y: miscActionsObservable.notify('show-cfg')
        _cbList = []
        if status == 'on':
            kwds['start'] = False
            kwds['stop'] = True
            _cbList = [('stop', _stopCb)]
        elif status == 'off':
            _cbList = [('start', _startCb)]
        _cbList += [('preferences', _showCfg)]
        xmlMenu = buildXmlMenu(menuSchema, **kwds)
        applet.setup_menu(xmlMenu, _cbList, None)
    return _cb


def main(containerKind, applet=None, withTray=True, hideWindow=False):
    """Run in the specified environment.

    *containerKind* one of 'window+tray' or 'applet'.
    *applet*        set when called as a panel applet.
    *withTray*      show the status icon in the tray, if True (default: True).
    *hideWindow*    don't show the main window (default: False).
    """
    config = manageConfigFile()
    ifCheckInterval = config.getValue('check_interval', converter=int,
                                      default=10)
    runPON = RunPON(config)
    gobject.timeout_add_seconds(INTERVAL, runPON.updateTime)
    if ifCheckInterval and ifCheckInterval > 0:
        gobject.timeout_add_seconds(ifCheckInterval, runPON.checkIF)
    if containerKind == 'window+tray':
        window = RunPONWindow(runPON, withTray, hideWindow, gtk.WINDOW_TOPLEVEL)
        try:
            gtk.main()
        except KeyboardInterrupt:
            sys.exit(0)
    elif containerKind == 'applet':
        # Turns off the main window menu.
        runPON.menu.isPresent = False
        applet.add(runPON)
        menuCallback = makeAppletOnOffCallback(applet, runPON.onOffObservable,
                                                runPON.miscActionsObservable)
        # Initialize the menu to its default value.
        menuCallback('off')
        runPON.onOffObservable.register(menuCallback)
        applet.show_all()
    return True


def running_as_applet():
    """Return True if it seems that we were executed as an applet."""
    for opt in sys.argv[1:]:
        if 'oaf-activate-iid' in opt or 'sm-client-id' in opt:
            return True
    return False


if HAS_GNOMEAPPLET and running_as_applet():
    # Initialization called when we're executed as a Gnome panel applet.
    gnomeapplet.bonobo_factory("OAFIID:GNOME_RunPON_Factory",
                                gnomeapplet.Applet.__gtype__, PRG_NAME,
                                VERSION, lambda x, y: main('applet', x))


if __name__ == '__main__':
    """Things to do when called by the command line."""
    import getopt
    try:
        optList, args = getopt.getopt(sys.argv[1:], 'wtnh',
                                      ['window', 'tray', 'no-tray', 'help'])
    except getopt.error, e:
        print 'Trouble with the arguments:', e
        print ''
        print RUNPON_HELP
        sys.exit(1)
    containerKind = 'window+tray'
    kwds = {}
    for opt, value in optList:
        if opt in ('-t', '--tray'):
            kwds['hideWindow'] = True
        elif opt in ('-n', '--no-tray'):
            kwds['withTray'] = False
        elif opt in ('-h', '--help'):
            print RUNPON_HELP
            sys.exit(0)
    if kwds.get('hideWindow') is True and kwds.get('withTray') is False:
        print '--tray option is incompatible with --no-tray'
        print ''
        print RUNPON_HELP
        sys.exit(1)
    main(containerKind, **kwds)

