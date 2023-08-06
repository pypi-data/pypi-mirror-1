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

from trosnoth.src.gui.framework import framework
from trosnoth.src.gui.framework.elements import TextElement, Backdrop, TextButton
from trosnoth.src.trosnothgui.pregame.settingsMenu import SettingsMenu
from trosnoth.src.trosnothgui.pregame.savedGameMenu import SavedGameMenu
from trosnoth.src.trosnothgui.pregame.playMenu import PlayMenu
from trosnoth.src.trosnothgui.pregame.playerNameMenu import PlayerNameMenu
from trosnoth.src.trosnothgui.credits import CreditsScreen
from trosnoth.src.utils.getUserInfo import getName
from trosnoth.data import getPath
from trosnoth.src.utils import logging
from trosnoth.src.utils.getUserInfo import isFirstTime

from trosnoth.src.trosnothgui.pregame.connectionFailedDialog import ConnectionFailedDialog
from trosnoth.src.trosnothgui.pregame.firstplaynotify import FirstPlayNotificationBar



from trosnoth.src.gui.common import *
from trosnoth.src.trosnothgui.pregame import colours


from twisted.internet import reactor

class StartupInterface(framework.CompoundElement):
    '''Represents the interface while the game is not connected to a server.'''
    
    def __init__(self, app, mainInterface):
        super(StartupInterface, self).__init__(app)
        self.interface = mainInterface

        # Create font.
        self.font = self.app.screenManager.fonts.bigMenuFont
        
        self.offsets = self.app.screenManager.offsets

        # Create other elements.
        self.buttons = [self.button('play',             self.playClicked,       (20, 210),      hugeFont = True),
                        self.button('recorded games',   self.savedGamesClicked, (20, 340)),
                        self.button('settings',         self.settingsClicked,   (20, 410)),
                        self.button('credits',          self.creditsClicked,    (20, 480)),
                        self.button('exit',             self.exitClicked,       (20, 690))
                        ]
        self.firstTimeNotification = FirstPlayNotificationBar(app)
        self.elements = self.buttons + [self.firstTimeNotification]

        if isFirstTime():
            self.firstTimeNotification.show()

        # Create sub-menus.
        self.settingsMenu = SettingsMenu(app, self)
        self.savedGameMenu = SavedGameMenu(app, self)
        self.playMenu = PlayMenu(app, self)
        self.playerNameMenu = PlayerNameMenu(app)
        self.playerNameMenu.onGotName.addListener(self.gotName)
        self.creditsScreen = CreditsScreen(self.app, colours.mainMenuColour, self.mainMenu)

        # Which sub-menu is currently active.
        self.currentMenu = None

    def button(self, text, onClick, pos, anchor='topleft', hugeFont=False):
        pos = Location(ScaledScreenAttachedPoint(ScaledSize(pos[0], pos[1]), anchor), anchor)
        if hugeFont:
            font = self.app.screenManager.fonts.hugeMenuFont
        else:
            font = self.app.screenManager.fonts.bigMenuFont
        result = TextButton(self.app, pos, text, font, colours.mainMenuColour, colours.white)
        result.onClick.addListener(lambda sender: onClick())
        return result
    
    def heading(self, caption):
        return TextElement(self.app, caption, self.font,
                                 ScaledLocation(1000, 60, 'topright'),
                                 colours.headingColour)

    def playClicked(self):
        name = getName()
        if name is None:
            self.elements = [self.playerNameMenu]
        else:
            self.gotName(name)

    def creditsClicked(self):
        self.creditsScreen.restart()
        self.elements = [self.creditsScreen]

    def gotName(self, name):
        self.playMenu.setName(name)
        self.playMenu.regainedFocus()
        self.elements = [self.playMenu]

    def exitClicked(self):
        # Quit the game.
        self.app.stop()

    def mainMenu(self):
        self.elements = self.buttons

    def settingsClicked(self):
        self.elements = [self.settingsMenu]

    def savedGamesClicked(self):
        self.savedGameMenu.populateList()
        self.elements = [self.savedGameMenu]

    def inetConnect(self, server, port):
        'Called when user selects connect from inet menu.'
        self.mainMenu()

        # Actually connect.
        self.interface.connectToServer(server, port)

    def replayConnect(self, fname, alias):
        self.mainMenu()

        self.interface.connectToReplay(fname)

