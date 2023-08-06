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

from trosnoth.src.gui.framework import framework, hotkey
from trosnoth.src.gui import keyboard
from trosnoth.src.gui.screenManager.windowManager import MultiWindowException

from trosnoth.src.trosnothgui.ingame import viewManager
from trosnoth.src.trosnothgui.ingame.replayInterface import ReplayMenu, ViewControlInterface
from trosnoth.src.trosnothgui.ingame.gameMenu import GameMenu
from trosnoth.src.trosnothgui.ingame.detailsInterface import DetailsInterface
from trosnoth.src.trosnothgui.ingame.observerInterface import ObserverInterface
from trosnoth.src.trosnothgui.ingame.playerInterface import PlayerInterface
from trosnoth.src.trosnothgui.ingame.gameOverInterface import GameOverInterface
from trosnoth.src.trosnothgui.ingame import colours

from trosnoth.src.base import MenuError
from trosnoth.src import keymap

from trosnoth.data import user, getPath


class GameInterface(framework.CompoundElement):
    '''Interface for when we are connected to a server.'''

    def __init__(self, app, netClient, world):
        super(GameInterface, self).__init__(app)
        self.netClient = netClient
        self.world = world

        # Set up the keyboard mapping.
        self.keyMapping = keyboard.KeyboardMapping(keymap.default_game_keys)

        try:
            # Try to load keyboard mappings from the user's personal settings.
            config = open(getPath(user, 'keymap'), 'rU').read()
            self.keyMapping.load(config)
        except IOError:
            pass

        self.gameViewer = viewManager.GameViewer(self.app, self, world)
        if world.replay:
            self.gameMenu = ReplayMenu(self.app, netClient, world)
        else:
            self.gameMenu = GameMenu(self.app, self, world)
        self.detailsInterface = DetailsInterface(self.app, self)
        self.runningPlayerInterface = None
        self.observerInterface = ObserverInterface(self.app, self)
        self.menuHotkey = hotkey.MappingHotkey(self.app, 'menu', mapping=self.keyMapping)
        self.menuHotkey.onActivated.addListener(self.showMenu)
        self.elements = [
                         self.gameViewer, self.gameMenu,
                         self.menuHotkey, self.detailsInterface
                        ]
        self.hotkeys = hotkey.Hotkeys(self.app, self.keyMapping, self.detailsInterface.doAction)
        self.menuShowing = True
        self.gameOverScreen = None

        self.vcInterface = None
        if world.replay:
            self.vcInterface = ViewControlInterface(self.app, self)
            self.elements.append(self.vcInterface)
            self.hideMenu()

    def connectionLost(self):
        if not self.world.replay:
            self.cleanUp()
            self.gameMenu.cleanUp()

    def joined(self, player):
        '''Called when joining of game is successful.'''
        print 'Joined game ok.'
        playerSprite = self.gameViewer.worldgui.getPlayerSprite(player)
        self.runningPlayerInterface = pi = PlayerInterface(self.app, self, playerSprite)
        self.detailsInterface.setPlayer(player)
        self.elements = [self.gameViewer,
                         pi, self.menuHotkey, self.hotkeys, self.detailsInterface]

    def showMenu(self):
        if self.runningPlayerInterface is not None:
            if self.runningPlayerInterface.player is not None:
                # Can't get to this particular menu after you've joined the game.
                return
        self.elements = [self.gameViewer, self.gameMenu]
        self.menuShowing = True
        if self.vcInterface is not None:
            self.elements.insert(2, self.vcInterface)

    def minimapDisruption(self, player):
        self.gameViewer.minimapDisruption(player)

    def endMinimapDisruption(self):
        self.gameViewer.endMinimapDisruption()

    def hideMenu(self):
        if self.runningPlayerInterface is not None:
            self.elements = [self.gameViewer, self.runningPlayerInterface, self.gameMenu, self.menuHotkey,
                             self.hotkeys, self.detailsInterface]
        else:
            self.elements = [self.gameViewer, self.observerInterface, self.gameMenu, self.menuHotkey,
                             self.hotkeys, self.detailsInterface]
        if self.vcInterface is not None:
            self.elements.insert(2, self.vcInterface)

        if self.gameOverScreen:
            self.elements.append(self.gameOverScreen)
        self.menuShowing = False

    def disconnect(self):
        self.cleanUp()
        self.netClient.disconnect()

    def cleanUp(self):
        if self.gameViewer.timerBar is not None:
            self.gameViewer.timerBar.kill()
            self.gameViewer.timerBar = None
        try:
            self.gameViewer.closeChat()
        except MultiWindowException:
            pass

    def gameOver(self, winningTeam):
        self.gameOverScreen = GameOverInterface(self.app, winningTeam,
                self.disconnect)
        self.gameViewer.leaderboard.winner = winningTeam

        if self.runningPlayerInterface is not None:
            team = self.runningPlayerInterface.player.team
            if team is not None:
                if team is winningTeam:
                    self.gameViewer.pregameMessage.setText('Congratulations!')
                else:
                    self.gameViewer.pregameMessage.setText('Better luck next time!')

        self.elements.append(self.gameOverScreen)
        try:
            self.elements.remove(self.menuHotkey)
        except:
            pass

    def reDraw(self):
        # TODO: This is redrawing every time there's a tag.
        # Could optimise that a bit to only redraw if the screen contains
        # one of its mapblocks.
        self.gameViewer.viewManager.reDraw()

    def processEvent(self, event):
        try:
            return super(GameInterface, self).processEvent(event)
        except MenuError, err:
            self.detailsInterface.newMessage(err.value, colours.errorMessageColour)
            self.detailsInterface.endInput()
            return None