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

import sys
import time
import commands
import warnings
from collections import defaultdict

import pygtk
pygtk.require('2.0')
import gtk
import gobject

__version__ = VERSION = '0.3'

HAS_GNOMEAPPLET = True
try:
    import gnomeapplet
except ImportError, e:
    HAS_GNOMEAPPLET = False
    warnings.warn('Unable to import gnomeapplet: %s' % e)


# If True, it doesn't execute any command.
DONT_RUN = False
#DONT_RUN = True

# Update the label every X seconds.
INTERVAL = 1
# Check the interface every X seconds.
IF_CHECK_INTERVAL = 10

# Commands to be executed.
ON_CMD = 'pon'
OFF_CMD = 'poff'
# Run the OFF_CMD command if the interface is no more with us.
RUN_POFF_IF_DOWN = True

# Interface to check.
IF_CHECK = 'ppp0'
# Command used to check if the interface is up.  The %s placeholder (mandatory!)
# is replaced with the interface.  The command must return 0 in case of success.
IF_CHECK_CMD = 'ifconfig "%s"'

# Labels for the button.
BTN_ON_LABEL = 'on ' # keep the trailing space. :-)
BTN_OFF_LABEL = 'off'
# Text colors.
LABEL_OK_COL = gtk.gdk.color_parse('black')
LABEL_ERR_COL = gtk.gdk.color_parse('red') # used in case of errors.

# Don't check the interface for the first X seconds; otherwise, if the
# check is performed while the interface is not yet up, OFF_CMD will
# be called (only if RUN_POFF_IF_DOWN is True).  Keep it large enough. :-)
IF_GRACE_TIME = 20

PRG_NAME = 'RunPON'
RUNPON_HELP = """%s [%s] - runs pon/poff scripts and shows the running time.
         http://erlug.linux.it/~da/soft/runpon/

    -w (--window)   runs in a plain old window (default).
    -t (--tray)     shows only the status icon on the tray.
    -n (--no-tray)  doesn't show the status icon on the tray.
    -h (--help)     get this help and exits.

    To run it as a Gnome panel applet, see README.txt.
""" % (PRG_NAME, VERSION)


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


# Schema to build the menus.
menuSchema = ['start', 'stop', None, 'quit']
# Menu icons.
menuIcons = {'start': 'gtk-media-play',
            'stop': 'gtk-media-stop',
            'quit': 'gtk-quit'}


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
        timeObservable.register(self.set_label)
        timeObservable.register(self.set_tooltip_text)
        onOffObservable.register(self.handleOnOff)
        errorObservable.register(self.handleError)
        self.show()

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
    def __init__(self, onOffObservable, *args, **kwds):
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
               'quit': gtk.main_quit}
        for menuItem in menuSchema:
            if menuItem is not None:
                mi = gtk.ImageMenuItem(menuItem)
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
        self.connect('button_press_event', menu.showMenu)
        self.show()


class RunPON(gtk.HBox):
    """The main RunPON element, a HBox wrapping the label (inside an EventBox)
    and the ToggleButton."""
    def __init__(self, *args, **kwds):
        """Initialize the instance."""
        super(RunPON, self).__init__(*args, **kwds)
        # Our beloved timer.
        self.timer = Timer()
        # Event handler expected to be called with a string representing
        # the text to display on the label.
        self.timeObservable = Observable()
        # Event handler expected to be called with a 'on'/'off' string parameter.
        self.onOffObservable = Observable()
        self.onOffObservable.register(self.timer.setStatus)
        self.onOffObservable.register(self.runCommand)
        # Event handler for errors (called with a string representing the error).
        self.errorObservable = Observable()
        # The label used to display our information.
        self.timeLabel = RunPONTimeLabel(self.timeObservable,
                                         self.onOffObservable,
                                         self.errorObservable,
                                         str(self.timer))
        self.onOffButton = RunPONToggleButton(self.onOffObservable)
        self.menu = RunPONRightClickMenu(self.onOffObservable)
        self.eventBox = RunPONEventBox(self.timeLabel, self.menu)
        self.add(self.eventBox)
        self.add(self.onOffButton)
        self.show()

    def updateTime(self):
        """Update the displayed time (this method is called by
        a gobject timer)."""
        # Remember to always return True.
        if not self.timer.running:
            return True
        self.timeObservable.notify(str(self.timer))
        return True

    def checkIF(self):
        """Check if the interface is up, updating the status accordingly (this
        method is called by a gobject timer)."""
        # Remember to always return True.
        if not self.timer.running or self.timer < IF_GRACE_TIME:
            return True
        status, output = executeCommand(IF_CHECK_CMD % IF_CHECK, _force=True)
        if status != 0:
            self.errorObservable.notify('if down', status=status,
                                        output=output)
            print 'ERROR on "%s" interface: %s' % (IF_CHECK, output)
            if status is not None:
                if RUN_POFF_IF_DOWN:
                    self.onOffObservable.notify('off')
        return True

    def runCommand(self, status):
        """Execute a command, in response to an on/off event."""
        if status == 'on':
            executeCommand(ON_CMD)
        elif status == 'off':
            executeCommand(OFF_CMD)


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
        self.connect('delete_event', gtk.main_quit, None)
        content.timeObservable.register(self.set_title)
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
        # seems wrong.
        self.toggleVisibility = toggleVisibility
        self.set_visible(True)

    def handleClicks(self, widget, event, data=None):
        """Handle mouse button events."""
        if event.button == 3:
            self.content.menu.showMenu(widget, event, data)
        elif event.button == 1:
            self.toggleVisibility()

    def handleTooltipUpdate(self, tooltip):
        """Update the tooltip, and stores it (useful in case of errors)."""
        self._lastTooltip = tooltip
        self.set_tooltip(tooltip)

    def handleError(self, error, *args, **kwds):
        """Handle errors."""
        self.set_tooltip('%s E' % self._lastTooltip)


def buildXmlMenu(ms, **kwds):
    """Return an XML menu for our gnome panel applet; kwds can be set to
    False if the named entry is supposed to be deactivated."""
    menu = '<popup name="button3">\n    %s\n</popup>'
    mEntry = '<menuitem name="Item %d" verb="%s" label="%s" pixtype="%s" '
    mEntry += 'pixname="%s" />'
    _pixtypes = {}
    items = []
    count = 1
    for mi in ms:
        if mi is None:
            # XXX: how to introduce a separator?
            continue
        if kwds.get(mi) is False:
            # XXX: is there a way to show a non-sensitive item?
            #      Silly XML schema for menus!  Where is it documented?
            continue
        pixtype = _pixtypes.get(mi, 'stock')
        pixname = menuIcons.get(mi, 'gtk-properties')
        items.append(mEntry % (count, mi, mi, pixtype, pixname))
        count += 1
    return menu % '\n    '.join(items)


def makeAppletOnOffCallback(applet, observable):
    """Build a function that will react to on/off events, modifying the
    applet's menu accordingly."""
    def _cb(status):
        """Callback to modify the applet's menu."""
        kwds = {'start': True, 'stop': False, 'quit': False}
        _startCb = lambda x, y: observable.notify('on')
        _stopCb = lambda x, y: observable.notify('off')
        _cbList = []
        if status == 'on':
            kwds['start'] = False
            kwds['stop'] = True
            _cbList = [('stop', _stopCb)]
        elif status == 'off':
            _cbList = [('start', _startCb)]
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
    runPON = RunPON()
    gobject.timeout_add_seconds(INTERVAL, runPON.updateTime)
    gobject.timeout_add_seconds(IF_CHECK_INTERVAL, runPON.checkIF)
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
        menuCallback = makeAppletOnOffCallback(applet, runPON.onOffObservable)
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

