# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2009 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from trosnoth.src.trosnothgui.pregame import colours
from trosnoth.src.gui.framework import prompt
from trosnoth.src.gui.framework.tab import Tab
from trosnoth.src.gui.framework.elements import TextElement, TextButton
from trosnoth.src.gui.framework.checkbox import CheckBox
from trosnoth.src.gui.common import *
from trosnoth.src.gui import keyboard
from trosnoth.src import keymap
from trosnoth.data import getPath, user, makeDirs
import os


class KeymapTab(Tab):

    def __init__(self, app, startupInterface):
        super(KeymapTab, self).__init__(app, "Controls")
        self.startupInterface = startupInterface
        button = startupInterface.button

        # Break things up into categories
        movement = ['left', 'right', 'jump', 'down']
        menus =    ['menu']
        actions =  ['respawn', 'buy upgrade', 'use upgrade', 'add stars',
                    'abandon', 'captain', 'team ready']
        misc =     ['chat']
        upgrades = ['turret', 'shield', 'minimap disruption', 'phase shift',
                    'grenade']
        display =  ['leaderboard', 'zone progress', 'timer']

        actionNames = { 'abandon': 'Abandon upgrade',
                        'add stars': 'Contribute stars',
                        'buy upgrade': 'Buy upgrade',
                        'captain': 'Become captain',
                        'chat': 'Chat',
                        'down': 'Drop down',
                        'grenade': 'Grenade',
                        'jump': 'Jump',
                        'leaderboard': 'Show leaderboard',
                        'left': 'Move left',
                        'menu': 'Main menu',
                        'minimap disruption': 'Minimap Disruption',
                        'phase shift': 'Phase Shift',
                        'respawn': 'Respawn',
                        'right': 'Move right',
                        'shield': 'Shield',
                        'status bar': 'Status bar',
                        'team ready': 'Team ready',
                        'timer': 'Show timer',
                        'turret': 'Turret',
                        'use upgrade': 'Use upgrade',
                        'zone progress': 'Show zone bar'}

        # Organise the categories by column
        self.layout = [ [movement, menus, misc], [actions], [upgrades, display] ]

        self.errorInfo = TextElement(self.app, '', startupInterface.font,
                                 ScaledLocation(512, 580, 'center'))
        self.text = [
                     self.errorInfo
                    ]
                     
        self.inputLookup = {}

        xPos = 190

        # Lay everything out automatically.
        keymapFont = self.app.screenManager.fonts.keymapFont
        for column in self.layout:               # Each column
            yPos = 250
            for category in column:         # Each category
                for action in category:     # Each action
                    # Draw action name (eg. Respawn)
                    self.text.append(TextElement(self.app, actionNames[action],
                                    keymapFont,
                                    ScaledLocation(xPos, yPos,'topright'),
                                    colours.headingColour
                                    ))

                    # Create input box
                    box = prompt.KeycodeBox(self.app, ScaledArea(xPos+10, yPos, 100, 30),
                                    font = keymapFont)
                    box.onClick.addListener(self.setFocus)
                    box.onChange.addListener(self.inputChanged)
                    box.__action = action
                    self.inputLookup[action] = box

                    yPos += 35  # Between items
                yPos += 35      # Between categories
            xPos += 320         # Between columns

        self.elements = self.text + self.inputLookup.values() + \
                        [button('restore default controls',
                                self.restoreDefaults,
                                (0, -100), 'midbottom'),
                         button('save',
                                self.saveSettings,
                                (-100, -50), 'midbottom'),
                         button('cancel',
                                self.cancel,
                                (100, -50), 'midbottom'),
                         ]
        
        self.populateInputs()
        
    def inputChanged(self, box):
        # Remove the old key.
        try:
            oldKey = self.keyMapping.getkey(box.__action)
        except KeyError:
            pass
        else:
            del self.keyMapping[oldKey]

        # Set the new key.
        self.keyMapping[box.value] = box.__action

        # Refresh the display.
        self.refreshInputs()

    def populateInputs(self):
        # Set up the keyboard mapping.
        self.keyMapping = keyboard.KeyboardMapping(keymap.default_game_keys)

        try:
            # Try to load keyboard mappings from the user's personal settings.
            config = open(getPath(user, 'keymap'), 'rU').read()
            self.keyMapping.load(config)
        except IOError:
            pass

        # Refresh the display.
        self.refreshInputs()

    def refreshInputs(self):
        for column in self.layout:
            for category in column:
                for action in category:
                    # Get the current key and put it in the box.
                    try:
                        key = self.keyMapping.getkey(action)
                    except KeyError:
                        key = None
                    self.inputLookup[action].value = key

                    # Make the box white
                    self.inputLookup[action].backColour = (255,255,255)

    def restoreDefaults(self):
        self.keyMapping = keyboard.KeyboardMapping(keymap.default_game_keys)
        self.refreshInputs()

        self.incorrectInput("Default controls restored: press 'save' to confirm", (0,128,0))
    
    def clearBackgrounds(self):
        for action in self.inputLookup:
            self.inputLookup[action].backColour = (255,255,255)
        self.setFocus(None)

    def saveSettings(self):
        # Perform the save.
        open(getPath(user, 'keymap'), 'w').write(self.keyMapping.save())

        emptyBoxes = []

        for box in self.inputLookup.itervalues():
            if box.value is None:
                emptyBoxes.append(box)
            
        if len(emptyBoxes) > 0:
            self.populateInputs()
            for box in emptyBoxes:
                box.backColour = colours.invalidDataColour

            self.incorrectInput('Warning: some actions have no key', (192, 0, 0))
        else:
            self.mainMenu()

    def incorrectInput(self, string, colour):
        self.errorInfo.setColour(colour)
        self.errorInfo.setText(string)
        self.errorInfo.setFont(self.startupInterface.font)

    def cancel(self):
        self.populateInputs()
        self.mainMenu()

    def mainMenu(self):
        self.incorrectInput('', (0,0,0))
        self.clearBackgrounds()
        self.startupInterface.mainMenu()
