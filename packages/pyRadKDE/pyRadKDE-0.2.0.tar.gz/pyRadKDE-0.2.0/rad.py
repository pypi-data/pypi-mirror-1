#!/usr/bin/env python
# encoding: utf-8

"""Rad - the PyQt4 wheel Gui for pyRad"""

### Imports ###

# basic graphical stuff
from PyQt4.QtGui import QWidget, QGridLayout, QCursor, QIcon, QLabel, QLineEdit
# basic definitions and datatypes
from PyQt4.QtCore import Qt, QPointF
# Basics for KDE integration
from PyKDE4.kdecore import ki18n, KAboutData
from PyKDE4.kdeui import KIconLoader
# And a basic dialog class for the edit item dialog.
from PyKDE4.kdeui import KDialog
# For circles
from math import sin, cos, pi
# And for starting programs
from subprocess import Popen
# and parsing a command string into words for Popen
from shlex import split as split_action
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
DEFAULT_CONFIG = '''# v0.1 keep this line!
[
    ("''' + CENTER_ICON + '''", None), # the center item: (icon, action); action == None means "quit"
    ("konsole","konsole"), ("kontact","kontact"),
("konqueror","konqueror"), ("wesnoth","wesnoth"), # normal items
    ("krita","""[("''' + CENTER_ICON + '''", None), ("amarok", "amarok"), ("gimp","gimp")]""") # a folder with the center icon and only one real item
]
'''

### About the Program ###

# This also allows our users to use DrKonqui for crash recovery.

appName     = "pyRad"
catalog     = ""
programName = ki18n ("Rad")
version     = "0.2.0"
description = ki18n ("A simple radial command menu - best called with a gesture")
license     = KAboutData.License_GPL
copyright   = ki18n ("(c) 2009 Arne Babenhauserheide")
text        = ki18n ("pyRad is heavily inspired by Kommando, which sadly didn't make it into KDE4. Kommando in turn was inspired by the Neverwinternights menu.")
homePage    = "draketo.de"
bugEmail    = "arne_bab@web.de"

aboutData   = KAboutData (appName, catalog, programName, version, description,
                        license, copyright, text, homePage, bugEmail)

### Window ###

class ItemEditWidget(QWidget):
    def __init__(self, parent=None, icon="", action=None):
        QWidget.__init__(self, parent)
        # First add a Layout
        self.lay = QGridLayout()
        self.setLayout(self.lay)
        # Now add a description text
        self.description = QLabel("Edit the icon (KDE progam name) and the action (commandline input). To delete the item, just delete the action line (set to empty).")
        self.lay.addWidget(self.description, 0, 0, 1, 2)
        # Then add a text field with name
        self.icon_label = QLabel("Icon:", self)
        self.icon_edit = QLineEdit(self)
        self.lay.addWidget(self.icon_label, 1, 0)
        self.lay.addWidget(self.icon_edit, 1, 1)
        # Also add the same for the action
        self.action_label = QLabel("Action:", self)
        self.action_edit = QLineEdit(self)
        self.lay.addWidget(self.action_label, 2, 0)
        self.lay.addWidget(self.action_edit, 2, 1)

# First we need a message box for editing the entries
class ItemEditor(KDialog):
    def __init__(self, parent=None):
        KDialog.__init__(self, parent)
        # First add a layout
        # Now add widgets
        self.main = ItemEditWidget(self)
        self.setMainWidget(self.main)


    def edit(self, icon, action):
        """Edit an item - includes deleting it by returning None."""
        # Show the dialog.
        self.main.icon_edit.setText(icon)
        if action is None:
            action = ""
        self.main.action_edit.setText(action)
        self.show()
        self.raise_()
        self.activateWindow()
        # And run it.

        if self.exec_() == self.Accepted:
            action = self.main.action_edit.text()
            icon = self.main.icon_edit.text()
            if action == "":
                action = None
                return str(icon), action
            return str(icon), str(action)




# We just use and extend example from TechBase
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

        #: Option to decide if we should die on focus lost - used for prompts
        self.die_on_focus_out = True

        # Add an icon
        self.iconloader = KIconLoader()
        icon = QIcon(self.iconloader.loadIcon(PROGRAM_ICON, 0))
        self.setWindowIcon(icon)

        # Load the items from the config file.
        items = self.load_config()

        # Add a circle-list for all items
        self.circle = []

        # And arrange them as labels in a circle
        self.arrange_in_circle(items)

        # Finally add a message_box instance for editing items
        # self.message_box = KMessageBox()

        # Also we need an editor for the items. Call it with self.editor.exec(item).
        self.editor = ItemEditor(self)


    def focusOutEvent(self, event):
        """Close when we lose the focus and the mouse isn't inside the window."""
        # If we don't want to die on focus out, we just return None
        if not self.die_on_focus_out:
            return None
        # catch error case: don't close the window when the focus changed
        # due to becoming inactive even though the mouse is over the window.
        # Fixes the "quit when move across tooltip" bug.
        if event.reason() == Qt.ActiveWindowFocusReason and self.isInside(QPointF(QCursor.pos()), self):
            return None
        # if we lose focus, the wheel disappears
        self.close()

    def mouseReleaseEvent(self, event):
        """Close when we get a mouse release on a final item."""
        # Get the position
        pos = event.pos()

        for i in self.circle[:]:
            if self.isInside(pos, i):
                # If pyRad didn't reach a final action, we stop here.
                if event.button() == Qt.LeftButton:
                    if self.labelClicked(i) is None:
                        break
                elif event.button() == Qt.RightButton:
                    self.editLabel(i)
                    break
                else: # other buttons are ignored
                    break

                # Otherwise we can close the pyRad
                for label in self.circle:
                    label.destroy()
                self.close()


    def editLabel(self, label): # -> open message box -> set item.icon and item.action. -> save_config()
        """Edit a label. A click on the center item promts for adding a new label."""
        # Don't close when the dialog pops up
        self.die_on_focus_lost = False
        # if the center gets clicked, add a new label.
        if label == self.circle[0]:
            item = self.editor.edit(label.icon, label.action)
            if item is None:
                return None
            icon, action = item
            if action is None:
                return None
            items = [(i.icon, i.action) for i in self.circle]
            items.append((icon, action))
        # otherwise edit the current label.
        else:
            item = self.editor.edit(label.icon, label.action)
            if item is None:
                return None # clicked cancel
            icon, action = item
            items = [(i.icon, i.action) for i in self.circle]
            if action is not None:
                items[self.circle.index(label)] = (icon, action)
            else:
                idx = self.circle.index(label)
                items = items[:idx] + items[idx + 1:]
        self.save_config(items)
        self.die_on_focus_lost = True


    def labelClicked(self, label):
        """React to a label being clicked.

        @return: True if the circle reached an end, None if it should continue existing."""
        if label.action is None:
            return True
        if label.action is not None and label.action[0] == "[":
            # then it's a folder!
            # get its contents
            items = eval(label.action)
            # and store the current items in the new center.
            # as long as the user didn't click the center
            if not label == self.circle[0]:
                items[0] = ( CENTER_ICON , str([(i.icon, i.action) for i in self.circle]) )
            self.arrange_in_circle(items)
            # We don't do anything else in that case.
            return None
        # if it's no folder and not None, we start the program
        # if this fails, the code ends here
        # and the circle stays visible.
        if label.action is not None:
            try:
                Popen(split_action(label.action))
                return True
            except:
                return None



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
        self.circle = self.items_to_circle(items)

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

    def items_to_circle(self, items):
        """Create the circle list from the given items.
        @return: circle (list of labels)"""
        circle = []
        for icon, action in items:
            label = self.item_to_label(icon, action)
            circle.append(label)

        return circle

    def item_to_label(self, icon, action):
        """Turn an item into a QLabel."""
        label = QLabel(self)
        label.icon = icon
        label.action = action
        label.setToolTip(str(action))
        label.setPixmap(self.iconloader.loadIcon(icon, 0))
        return label

    def load_config(self):
        """Load the items from the config file.

        @return: items (list)"""
        # If there's no config, we use standard items
        if not isfile(join(home, CONFIG_FILE_NAME)):
            #: The items the menu should show in top-level (via folders this contains the whole of the wheel menu).
            items = eval(DEFAULT_CONFIG)
            # also create the config file -> this is an initial run
            f = open(join(home, CONFIG_FILE_NAME), "w")
            f.write(DEFAULT_CONFIG)
            f.close()
        else:
            # if a config file is present, we load the items from there.
            f = open(join(home, CONFIG_FILE_NAME))
            config = f.read()
            assert(config.startswith("# v0.1"))
            items = eval(config)
            f.close()
            del f
            del config

        return items

    def save_config(self, items):
        """Save the current wheel layout to the config file.

        @param items: The new layout at any level."""
        # We roll back the circle to the top level
        # The center can't change, so we can use the one from the previous version of the circle.
        while self.circle[0].action is not None:
            # store items to be able to identify the folder in the lower layout
            items_tmp = [(label.icon, label.action) for label in self.circle]
            # but replace the first with a generic center.
            items_tmp[0] = ( CENTER_ICON, None )
            self.labelClicked(self.circle[0])
            # find the folder corresponding to the upper layout.
            items_new = [(label.icon, label.action) for label in self.circle]
            for item in items_new:
                icon, action = item
                if action is not None and action[0] == "[" and eval(action) == items_tmp:
                    folder_new = items
                    folder_new[0] = ( CENTER_ICON, None )
                    idx = items_new.index(item)
                    item = (icon, str(folder_new))
                    items_new = items_new[:idx] + [item] + items_new[idx + 1:]
                    self.arrange_in_circle(items_new)

        items_tmp = [(i.icon, i.action) for i in self.circle]
        # Now we copy the previous circle back into the current circle.
        self.arrange_in_circle(items)
        # Finally we prepare the config data
        config = "# v0.1 keep this line!\n"
        config += str(items)
        # And save it
        f = open(join(home, CONFIG_FILE_NAME), "w")
        f.write(config)
        f.close()
