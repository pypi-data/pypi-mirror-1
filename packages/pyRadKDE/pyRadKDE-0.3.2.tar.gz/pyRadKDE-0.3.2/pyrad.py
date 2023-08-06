#!/usr/bin/env python
# encoding: utf-8

"""pyRadKDE - a wheel type command interface for KDE, inspired by Kommando (KDE 3) and Neverwinternights.
"""

# additional documentation - gets added to the docstring by hand, so I can more easily use it in user output

__install__ = """
installation:

- easy_install pyRadKDE

setup: 

- Add a mouse gesture for "pyrad.py": go into KDE systemsettings -> keyboard shortcuts -> add a gesture with the action "pyrad.py" (you might have to enable gestures in the settings, too - in the shortcuts-window you should find a settings button).
- customize the menu by editing the file "~/.pyradrc" or right-clicking items.

Alternate setup with dbus (much faster but incomplete): 

- Add "/usr/bin/pyrad.py" as script to your autostart (systemsettings->advanced->autostart) TODO: make it not show the GUI
- Add the mouse gesture to call D-Bus: Program: org.kde.pyRad ; Object: /MainApplication ; Function: newInstance
- Alternately set the gesture to call the command "dbus-send --type=method_call --dest=org.kde.pyRad /MainApplication org.kde.KUniqueApplication.newInstance"

"""

__usage__ = """
usage:

- Just use your gesture to call up the command wheel when you want to call one of your included programs.
- Right-click an item to edit it. Middle-click an item to add a new one after it (clockwise).
- Make folders by using the action [("kreversi", None), ("icon", "action"), ("icon2", "action2"), ...].
  Actions are simply the commands you'd use on the commandline.
- call "pyrad.py --quit" to shutdown the process in the background. "pyrad.py --help" shows the usage. "pyrad.py --daemon" starts pyRad without showing the GUI.

"""

__plans__ = """
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
"""
__ideas__ = """
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

PyPI url: http://pypi.python.org/pypi/pyRadKDE
"""

__doc__ += __install__ + __usage__ + __plans__ + __ideas__


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

### Constants ###

#: The PyRad version identifier
__version__ = "0.3.2"

### Commandline handling ###
# we do this here to have the maximum reaction time. 
from sys import argv
if "--help" in argv:
    print __usage__
    exit()

### Imports ###

# First the GUI class and the Data about the program
# we use an import function, so we can easily delay the import.
def importRad():
    """Import the Rad GUI."""
    from rad import Rad
    return Rad

# We also do the other imports in functions to facilitate profiling. 
# Then commandline arguments and handling
from PyKDE4.kdecore import KCmdLineArgs, KCmdLineOptions

# And AboutData - moved here, so we don't need to pull in GUI stuff to check if we're the first instance
from PyKDE4.kdecore import ki18n, KAboutData

# KApplication for basics
from PyKDE4.kdeui import KUniqueApplication

# and exiting.
from sys import exit as exit_

### Class for modifying KUniqueApplication ###

class KUniqueCaller(KUniqueApplication):
    def __init__(self, *args, **kwds):
        """Initialize the App and import all GUI elements.

        This gets only called when there's no already existing instance of the app."""
        super(KUniqueCaller, self).__init__(*args, **kwds)
        # And get and show the GUI
        Rad = importRad()
        self.rad = Rad()

    def newInstance(self):
        """Get a new instance -> in reality only check if there's already an instance and tell the GUI to run."""
        # if we get the quit arg ("pyrad.py --quit"), we close and shutdown
        args = KCmdLineArgs.parsedArgs()
        if args.isSet("quit"):
            self.rad.close()
            self.quit()
            return 0
        elif args.isSet("daemon"): 
            ret = super(KUniqueCaller, self).newInstance()
            return ret
        self.rad.setup()
        self.rad.show()
        self.rad.toForeground() # this cost about 0.07s
        ret = super(KUniqueCaller, self).newInstance()
        #self.rad.close() # uncomment for profiling
        return ret

### Runner ###

### About the Program ###

# This also allows our users to use DrKonqui for crash recovery.

def createAboutData():
    """Create the aboutData for PyRad."""
    appName     = "pyRad"
    catalog     = ""
    programName = ki18n ("Rad")
    version     = __version__
    description = ki18n ("A simple radial command menu - best called with a gesture")
    license     = KAboutData.License_GPL
    copyright   = ki18n ("(c) 2009 Arne Babenhauserheide")
    text        = ki18n ("pyRad is heavily inspired by Kommando, which sadly didn't make it into KDE4. Kommando in turn was inspired by the Neverwinternights menu.")
    homePage    = "draketo.de"
    bugEmail    = "arne_bab@web.de"

    aboutData   = KAboutData (appName, catalog, programName, version, description,
                        license, copyright, text, homePage, bugEmail)
    return aboutData

def initKApp():
    """Initialize the KApplication."""
    # First we need the aboutData
    aboutData = createAboutData()
    # Now we need to compile the commandline args for KDE programs
    KCmdLineArgs.init (argv, aboutData)
    # Add an option to quit the app
    opts = KCmdLineOptions()
    opts.add("quit", ki18n("Shutdown the background program"))
    opts.add("daemon", ki18n("Start the background program without showing the GUI "))
    KCmdLineArgs.addCmdLineOptions(opts)
    # Then do basic initializing
    app = KUniqueCaller()
    # And get and show the GUI
    return app

def run():
    """Start and run the PyRad"""
    # First we need to compile the commandline args for KDE programs
    #KCmdLineArgs.init (argv, aboutData)
    # Then do basic initializing
    #app = KApplication()
    app = initKApp()
    #rad.close()
    # Finally we execute the program - and return the exit code from the program.
    return app.exec_()


### Self Test == Run the Program ###

if __name__ == "__main__":
    exit_(run())
