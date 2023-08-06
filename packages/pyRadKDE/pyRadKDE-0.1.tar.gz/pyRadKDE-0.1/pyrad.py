#!/usr/bin/env python
# encoding: utf-8

"""pyRadKDE - a wheel type commannd interface for KDE, heavily inspired by Kommando.


plan: 

- Initialize a window at mouse position (QCursor::pos(); QLayoutItem::setGeometry(Qrect)) -done
- Make the window transparent, without background, border and menubar. -done
- Show icons in a circle  -done
- make the icons clickable  -done
- add folder-icons: the action is simply a list with all contained items => starts with [  -done
- store the previous layout (buttons) directly in the name of the central icon => same list format.  -done

- register a global shortcut / gesture in KDE from within the program -> usable as soon as it's installed. 


ideas: 

- use plasma. 
- Show the program cathegories from the K-Menu.
- Get the folders and actions from Nepomuk somehow -> favorites or such.
- Option to have an auto-optimizing wheel layout :) 

"""

### Basic Data ###

__version__ = "0.1"
__copyright__ = "GPLv3 or later" # TODO: Proper copyright info

### Imports ### 

# basic graphical stuff
from PyQt4.QtGui import QWidget, QCursor, QApplication, QIcon, QLabel
# basic definitions and datatypes
from PyQt4.QtCore import Qt, QPointF
# Basics for KDE integration
from PyKDE4.kdecore import ki18n, KAboutData, KCmdLineArgs
from PyKDE4.kdeui import KApplication, KIconLoader
# Commandline arguments 
from sys import argv
# and exiting
from sys import exit as exit_
# For circles
from math import sin, cos, pi
# And for starting programs
from subprocess import Popen
# Finally some path tools for loading a config file
from os.path import join, isfile
# and system independent home folder location
from user import home

### Constants ###

WINDOW_WIDTH = 250
WINDOW_HEIGHT = 250
CIRCLE_RADIUS = 80
PROGRAM_ICON = "kreversi"
CENTER_ICON = "kreversi"
CONFIG_FILE_NAME = ".pyradrc"

# If there's no config, we use standard items
if not isfile(join(home, CONFIG_FILE_NAME)): 
    #: The items the menu should show in top-level (via folders this contains the whole of the wheel menu). 
    ITEMS = [(CENTER_ICON, None), # the center item
                 ("kate","kate"), ("kmail","kmail"), ("kmix","kmix"), ("wesnoth","wesnoth"), # normal items
                 ("krita","[('" + CENTER_ICON + "', None), ('gimp','gimp')]") # a folder with the center icon and only one real item
                 ]
else:
    # if a config file is present, we load the items from there.
    f = open(join(home, CONFIG_FILE_NAME))
    ITEMS = eval(f.read())
    f.close()
    del f


### About the Program ###

# This also allows our users to use DrKonqui for crash recovery.

appName     = "pyRad"
catalog     = ""
programName = ki18n ("Rad")
version     = "1.0"
description = ki18n ("A simple radial command menu - best called with a gesture")
license     = KAboutData.License_GPL
copyright   = ki18n ("(c) 2009 Arne Babenhauserheide")
text        = ki18n ("pyRad is heavily inspired by Kommando, which sadly didn't make it into KDE4. Kommando in turn was inspired by the Neverwinternights menu.")
homePage    = "draketo.de"
bugEmail    = "arne_bab@web.de"

aboutData   = KAboutData (appName, catalog, programName, version, description,
                        license, copyright, text, homePage, bugEmail)

### Window ###

# The first step is just using the example from TechBase
# http://techbase.kde.org/Development/Tutorials/Plasma/Python/GettingStarted

class Rad(QWidget):
    def __init__(self, parent=None, f=Qt.FramelessWindowHint):
        """Create the Window."""
        QWidget.__init__(self, parent, f)
        # Quit when this window gets closed
        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_TranslucentBackground)
	
	# resize
	self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
	
	# Move below the cursor
        self.move_to_cursor()
        self.setWindowTitle(appName)

	# Make sure we get focus events
        self.setFocusPolicy(Qt.StrongFocus)
	
	# Add an icon
	self.iconloader = KIconLoader()
	icon = QIcon(self.iconloader.loadIcon(PROGRAM_ICON, 0))
	self.setWindowIcon(icon)
	
        # Add a circle-list for all items
	self.circle = []

        # And arrange them in a circle
     	self.arrange_in_circle(ITEMS)
	

    def focusOutEvent(self, event):
        """Close when we lose the focus."""
        self.close()

    def mouseReleaseEvent(self, event):
        """Close when we get a mouse release on a final item."""
        # Get the position
        pos = event.pos()
                
        for i in self.circle[:]: 
	    if self.isInside(pos, i):
                if i.action is not None and i.action[0] == "[":
                    # then it's a folder!
                    # get its contents
                    items = eval(i.action)
                    # and store the current items in the new center.
                    # as long as the user didn't click the center
                    if not i == self.circle[0]: 
                        items[0] = ( CENTER_ICON , str([(i.icon, i.action) for i in self.circle]) )
                    self.arrange_in_circle(items)
                    # We don't do anything else in that case. 
                    return None
                # if it's no folder and not None, we start the program
                # if this fails, the code ends here 
                # and the circle stays visible.
                if i.action is not None: 
                    Popen(i.action)

                # Otherwise we can close the pyRad
                for label in self.circle: 
                    label.destroy()
                self.close()


    def isInside(self, point, thing):
	"""Check, if the point is inside the thing."""
	if point.x() > thing.x() and point.x() < thing.x() + thing.width() and point.y() > thing.y() and point.y() < thing.y() + thing.height():
            return True
        else:
            return False

    def move_to_cursor(self):
        """Move the Window to the position of the mouse cursor."""
        # We set the position to the Cursor
        pos = QPointF(QCursor.pos())
        # center on the cursor (reduce by half window width and height)
        x = pos.x() - 0.5*self.size().width()
        y = pos.y() - 0.5*self.size().height()
	self.move(x, y)

    def arrange_in_circle(self, items): 
	"""Arrange all icons in a circle, with the zeroth in the middle."""
        # First remove the previous items
        for label in self.circle[:]:
            label.hide()
            label.destroy()

        # Then create the circle list
        self.circle = []
        for icon, action in items: 
	    label = QLabel(self)
	    label.icon = icon
            label.action = action
	    label.setPixmap(self.iconloader.loadIcon(icon, 0))
	    self.circle.append(label)

        # Now set the center icon
        self.circle[0].move(0.5*self.width() - 0.25*self.circle[0].width(), 0.5*self.height() - 0.75*self.circle[0].height())

	# And finally arrange all other items in a circle around the center.
        for i in self.circle[1:]: 
	    angle = 2 * pi * (self.circle.index(i) -1 ) / len(self.circle[1:])
	    x_displacement = sin(angle)*CIRCLE_RADIUS
	    y_displacement = cos(angle)*CIRCLE_RADIUS
	    x = 0.5*self.width() - 0.25*i.width()
	    y = 0.5*self.height() - 0.75*i.height()
	    x += x_displacement
	    y += y_displacement
	    i.move(x, y)

        # Finally show the new circle
        for i in self.circle: 
            i.show()
	            


### Self Test ###

if __name__ == "__main__":
    KCmdLineArgs.init (argv, aboutData)
    app = KApplication()
    rad = Rad()
    rad.show()
    exit_(app.exec_())
