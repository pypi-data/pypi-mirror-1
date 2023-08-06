  RunPON
  ======

RunPON is a program useful to establish a network connection
calling the pon/poff scripts.  It will show the connection time and
periodically check if the interface is still up.
It can run as a stand-alone application in a window (plus as a status
icon in the tray), or as a Gnome panel applet.

Modifying its configuration it can be used to run and stop any
command (or even as a dummy timer).


  CONFIGURATION AND FUTURE IMPROVEMENTS
  =====================================

The first time you run it, it will create a ~/.config/runpon/runpon.cfg
configuration file that you can modify accordingly to your needs.
You can find a commented version of the configuration file in
the ./goodies directory.

The "Properties" right-click menu entry will show you a configuration GUI
for this file.
The options should be mostly self-explanatory (see also the tooltips);
you have to keep in mind that the most important option of all is "active",
valid only in the "DEFAULT" section.
It must point to the section that will be actively used (values in the
"DEFAULT" section will be used only as fall-back).
So:
- create your own new section.
- configure it as you like.
- set it as the "active" section, in "DEFAULT".

RunPON is in a "works for me" state; I have many ideas about how
it can be improved, but very little knowledge of Gtk, Gnome, PyGtk
(and I'm shamefully confused about the strange Bonobo beast).

If you want to help growing it into a respectable program,
read the TODO.txt file and contact me (see AUTHOR.txt).


  INSTALLATION
  ============

Requirements:
- Python 2.4 or later.
- python-gtk and python-gnome2 2.16 or later.
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
  so if you use another directory, modify it accordingly.
  After that, you should see RunPON listed amongst your nice Gnome
  applets (maybe you need to restart Gnome, who knows?)
  It can be used in a Xfce panel using the XfApplet helper, and I'm sure
  other environments provide similar adapters (or maybe not, who cares?)


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

