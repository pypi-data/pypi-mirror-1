#!/usr/bin/env python
# encoding: utf-8

"""pyRadKDE - a wheel type commannd interface for KDE, heavily inspired by Kommando.

installation and setup:

- easy_install pyRadKDE
- go into KDE systemsettings -> keyboard shortcuts
- add a gesture with the action "pyrad.py"
- you might have to enable gestures in the settings, too (in the shortcut-window you should find a settings button).
- customize the menu by editing the file "~/.pyradrc"

usage:

- Just use your gesture to call up the command wheel when you want to call one of your included programs.
- Right-click an item to edit it. Right-click the center to add a new item.
- Make folders by using the action [("kreversi", None), ("icon", "action"), ("icon2", "action2"), ...]
- Actions are simply the commands you'd use on the commandline.

plan:

- Initialize a window at mouse position (QCursor::pos(); QLayoutItem::setGeometry(Qrect)) -done
- Make the window transparent, without background, border and menubar. -done
- Show icons in a circle  -done
- make the icons clickable  -done
- add folder-icons: the action is simply a list with all contained items => starts with [  -done
- store the previous layout (buttons) directly in the name of the central icon => same list format.  -done

- register a global shortcut / gesture in KDE from within the program -> usable as soon as it's installed. -todo


ideas:

- use plasma.
- Add a pyRadEdit script in which people can edit the items in a wheel type layout. Maybe add a button or similar to switch to edit mode. Or edit with right-click (right-click the center to add an item).
- Show the program cathegories from the K-Menu.
- Get the folders and actions from Nepomuk somehow -> favorites or such.
- Option to have an auto-optimizing wheel layout :)

PyPI url: http://pypi.python.org/pypi/pyRadKDE

"""

### Basic Data ###

__copyright__ = """pyRad - a wheel type command menu.

    Copyright (c) 2009 Arne Babenhauserheise
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

### Imports ###

# First the GUI class and the Data about the program
from rad import Rad, aboutData
from rad import version as __version__

# Then commandline arguments and handling
from sys import argv
from PyKDE4.kdecore import KCmdLineArgs

# KApplication for basics
from PyKDE4.kdeui import KApplication

# and exiting.
from sys import exit as exit_

### Self Test == Run the Program ###

if __name__ == "__main__":
    # First we need to compile the commandline args for KDE programs
    KCmdLineArgs.init (argv, aboutData)
    # Then do basic initializing
    app = KApplication()
    # And get and show the GUI
    rad = Rad()
    rad.show()
    # Finally we execute the program - and exit the script with the exit code from the program.
    exit_(app.exec_())
