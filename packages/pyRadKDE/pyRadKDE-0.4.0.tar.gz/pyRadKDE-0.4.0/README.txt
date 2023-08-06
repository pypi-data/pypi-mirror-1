#pyRad

pyRadKDE - a wheel type command interface for KDE, inspired by Kommando (KDE 3) and Neverwinternights.

installation:

- easy_install pyRadKDE

setup: 

- Add a mouse gesture for "pyrad.py": go into KDE systemsettings -> keyboard shortcuts -> add a gesture with the action "pyrad.py" (you might have to enable gestures in the settings, too - in the shortcuts-window you should find a settings button).
- customize the menu by editing the file "~/.pyradrc" or right-clicking items.

Alternate setup with dbus (much faster but incomplete): 

- Add "/usr/bin/pyrad.py" as script to your autostart (systemsettings->advanced->autostart) TODO: make it not show the GUI
- Add the mouse gesture to call D-Bus: Program: org.kde.pyRad ; Object: /MainApplication ; Function: newInstance
- Alternately set the gesture to call the command "dbus-send --type=method_call --dest=org.kde.pyRad /MainApplication org.kde.KUniqueApplication.newInstance"


usage:

- Just use your gesture to call up the command wheel when you want to call one of your included programs.
- Left-click the program to start it. You can also press the key shown in the programs tooltip for the same effect. 
- Right-click an item to edit it. Middle-click an item to add a new one after it (clockwise).
- Make folders by using the action [("kreversi", None), ("icon", "action"), ("icon2", "action2"), ...].
  Actions are simply the commands you'd use on the commandline (no shell scripting though).
- call "pyrad.py --quit" to shutdown the process in the background. "pyrad.py --help" shows the usage. "pyrad.py --daemon" starts pyRad if without showing the GUI.


plan:

- new command scheme: right-click always edits, middle-click adds a new item. -done
- items arranged clockwise. -done
- right-click on center opens a general config dialog. -todo
- a general config dialog. -todo
- first run of new version shows image as usage guide. -todo
- Edit dialog should show the icon graphically. A click on the item should show the edit dialog we have when editing the K-Menu. -todo
- Edit dialog should have a radio button for the action: "create folder". -todo
- register a global shortcut / gesture in KDE from within the program -> usable as soon as it's installed. -todo
- make it show faster. -todo
- add option --only-daemon to only start the daemon without showing the GUI

ideas:

- use plasma.
- Show the program cathegories from the K-Menu.
- Get the folders and actions from Nepomuk somehow -> favorites or such.
- Option to have an auto-optimizing wheel layout :)
- adjust icon size to the number of icons in the circle.
- Adjust circle radius to the number of icons. 
- Show the icons inside a folder over/around the folder icon. 
- Add a CLI fallback, so people can also access their actions via the shell. 
- Talk to DBus directly (for higher performance). -> dbus-send --type=method_call --dest=org.kde.pyRad /MainApplication org.kde.KUniqueApplication.newInstance
  (from http://www.staerk.de/thorsten/index.php/Hacking_KDE)
- Keyboard shortcuts (1, 2, 3, ... for the wheel items -> click paths to programs)
- Check if an app is already open. If it is, simply switch to it (dbus -> get winID, forceActivateWindow(winID)?). 
  Sample DBus calls: dbus-send --dest=org.freedesktop.DBus --type=method_call --print-reply / org.freedesktop.DBus.ListNames ; dbus-send --dest=org.kde.konqueror-14040 --type=method_call --print-reply /konqueror/MainWindow_1 org.kde.KMainWindow.winId; dbus-send --dest=org.freedesktop.DBus --type=method_call --print-reply / org.freedesktop.DBus.NameHasOwner string:"org.kde.pyRad"
  To bring a background app to foreground, hide its main window, then show it again.
  -> /konqueror com.trolltech.Qt.QWidget.hide + ...show + hide pyRad
  PID stuff: http://code.google.com/p/psutil/

PyPI url: http://pypi.python.org/pypi/pyRadKDE
