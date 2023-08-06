  RunPON
  ======

RunPON is a program useful to establish a network connection
calling the pon/poff scripts.  It will show the connection time and
periodically check if the interface is still up.
It can run as a stand-alone application in a window (plus as a status
icon in the tray), or as a Gnome panel applet.

Modifying the configuration it can be used to run and stop any
command (or even as a dummy timer).


  CONFIGURATION AND FUTURE IMPROVEMENTS
  =====================================

Right now the configuration is hardcoded in the runpon.py script;
you MUST edit it to suit your needs.

RunPON is in a "works for me" state; I have many ideas about how
it can be improved, but very little knowledge of Gtk, Gnome, PyGtk
(and I'm shamefully confused about the whole Bonobo thing).

If you want to help growing it into a respectable program,
read the TODO.txt file and contact me (see AUTHOR.txt).


  INSTALLATION
  ============

Requirements:
- Python 2.4 or later.
- python-gtk 2.0 or later.
- python-gobject.
- python-gnomeapplet (optional: only to run as a Gnome panel applet).

So far, there's no automatic installation.
You must copy the 'runpon.py' script to /usr/local/bin/

After that, it depends on how you intend to use it:
- as a normal application, you're done: simply run 'runpon.py'
  Maybe you can use the ./goodies/runpon.desktop file to integrate
  it in your desktop environment (if you it in ~/.config/autostart
  it will be executed automatically every login, or you can copy
  in your ~/Desktop directory).

- as a Gnome panel applet, copy the 'GNOME_RunPON.server' file into
  the /usr/lib/bonobo/servers/ directory (or wherever the Bonobo
  servers are listed).
  Keep in mind that /usr/local/bin/ is hardcoded in GNOME_RunPON.server,
  so if you use another directory, modify it accordingly (if you're
  After that, you should see RunPON listed amongst your nice Gnome
  applets (maybe you need to restart Gnome, who knows?)  It can be used in
  a Xfce panel using the XfApplet helper, and I'm sure other
  environments provide similar adapters (or maybe not, who cares?)


  WINDOW AND STATUS ICON ON THE TRAY
  ==================================

By default, both the main window and the status icon on the tray
are shown.
If you want only the window, use the '-n' (or '--no-tray') command
line option.
If you want only the status icon, use the '-t' (or '--tray') option,
keeping in mind that you can always show/hide the main window with
a left-button click of the mouse on the icon.


  USAGE
  =====

Well... there's just a single button, and I'm pretty sure you have
already hit it, by now. :-)
Anyway, once you press it, the 'pon' (by default) command will be
executed and the timer will run.
Once you hit the button again, the 'poff' command will be called.
Notice that, periodically, it will run a command to check if a given
network interface is still up.  If it's not, by default the 'poff'
command will be called and the timer stopped (and the text will
turn all red, to its and your shame).  That's all.

The same actions (start/stop) are present in the right-click menu,
especially useful if you're using it from the tray.
Keep in mind that in the tray a simple icon is always shown; information
about the running time can be seen as a tooltip.

If you're testing it, keep in mind to set the DONT_RUN variable to True,
so that you will not spend all your money on tests. :-)


  LICENSE
  =======

RunPON is released under the terms of the GNU GPL 3 (or later) license.

