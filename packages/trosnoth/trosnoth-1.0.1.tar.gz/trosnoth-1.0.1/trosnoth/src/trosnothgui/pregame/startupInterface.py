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

import trosnoth.src.gui.framework.framework as framework
from trosnoth.src.gui.framework.elements import TextElement, Backdrop, TextButton
from trosnoth.src.trosnothgui.pregame.settingsMenu import SettingsMenu
from trosnoth.src.trosnothgui.pregame.replayMenu import ReplayMenu
from trosnoth.src.trosnothgui.pregame.connectingScreen import ConnectingScreen
from trosnoth.src.trosnothgui.pregame.playMenu import PlayMenu
from trosnoth.src.trosnothgui.pregame.playerNameMenu import PlayerNameMenu
from trosnoth.src.trosnothgui.pregame.statsMenu import StatsMenu
from trosnoth.src.trosnothgui.credits import CreditsScreen
from trosnoth.src.utils.getUserInfo import getName
from trosnoth.data import getPath
from trosnoth.src.networkDefines import replayServerPort



from trosnoth.src.gui.common import *
from trosnoth.src.trosnothgui.pregame import colours


import trosnoth.data.startupMenu as startupMenu

from twisted.internet import reactor

class StartupInterface(framework.CompoundElement):
    '''Represents the interface while the game is not connected to a server.'''
    
    def __init__(self, app, mainInterface):
        super(StartupInterface, self).__init__(app)
        self.interface = mainInterface

        # Create font.
        self.font = self.app.screenManager.fonts.bigMenuFont
        
        # Create the backdrop image.
        backdrop = Backdrop(self.app, getPath(startupMenu, 'blackdrop.png'))

        # Place the title.
        titlefont = self.app.screenManager.fonts.titleFont
        titlepos = Location(FullScreenAttachedPoint(ScaledSize(0, 20), 'midtop'), 'midtop')
        title = TextElement(self.app, 'Trosnoth', titlefont, titlepos, colours.titleColour)

        # Things that will be part of the backdrop of the entire startup menu system.
        verFont = self.app.screenManager.fonts.versionFont
        self.backdrop = [
            backdrop,
            title,
            TextElement(self.app, u'v1.0.1', verFont,
                        Location(FullScreenAttachedPoint(ScaledSize(-10,-10), 'bottomright'), 'bottomright'), (192, 192, 192))
        ]



        self.offsets = self.app.screenManager.offsets

        # Create other elements.
        self.buttons = [self.button('settings',         self.settingsClicked,   (20, 340)),
                        self.button('load replay',      self.replayClicked,     (20, 410)),
                        self.button('view statistics',  self.statsClicked,      (20, 480)),
                        self.button('credits',          self.creditsClicked,    (20, 550)),
                        self.button('play',             self.playClicked,       (20, 210),      hugeFont = True),
                        self.button('exit',             self.exitClicked,       (20, 690)),
                        ]

        self.elements = self.backdrop + self.buttons

        # Create sub-menus.
        self.connectingScreen = ConnectingScreen(self.app, self)
        self.settingsMenu = SettingsMenu(self.app, self)
        self.replayMenu = ReplayMenu(self.app, self, mainInterface.netClient)
        self.statsMenu = StatsMenu(self.app, self)
        self.playMenu = PlayMenu(self.app, self, mainInterface.netClient)
        self.playerNameMenu = PlayerNameMenu(self.app)
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
            self.elements = self.backdrop + [self.playerNameMenu]
        else:
            self.gotName(name)

    def creditsClicked(self):
        self.creditsScreen.restart()
        self.elements = self.backdrop + [self.creditsScreen]

    def gotName(self, name):
        self.playMenu.setName(name)
        self.playMenu.regainedFocus()
        self.elements = self.backdrop + [self.playMenu]

    def exitClicked(self):
        # Quit the game.
        reactor.stop()

    def mainMenu(self):
        self.elements = self.backdrop + self.buttons

    def settingsClicked(self):
        self.elements = self.backdrop + [self.settingsMenu]

    def replayClicked(self):
        self.elements = self.backdrop + [self.replayMenu]

    def statsClicked(self):
        self.elements = self.backdrop + [self.statsMenu]

    def lanConnect(self, gameName):
        'Called when user selects connect from lan menu.'
        self.elements = self.backdrop + [self.connectingScreen]
        self.connectingScreen.setServer(gameName)
        # Actually connect.
        result = self.interface.netClient.connect(gameName)
        self.connectingDeferred = result
        result.addCallback(self.interface.connectionEstablished).addErrback(self.connectionFailed)

    def inetConnect(self, server, port):
        'Called when user selects connect from inet menu.'
        self.elements = self.backdrop + [self.connectingScreen]
        self.connectingScreen.setServer('%s:%s' % (server, port))
        # Actually connect.
        result = self.interface.netClient.connectByPort(server, port)
        self.connectingDeferred = result
        result.addCallback(self.interface.connectionEstablished).addErrback(
            self.connectionFailed)

    def replayConnect(self, fname, alias):
        self.elements = self.backdrop + [self.connectingScreen]
        self.connectingScreen.text.setText('Loading replay \'%s\'...' % alias)
        self.connectingScreen.text.setFont(self.font)

        from trosnoth.src.networkServer import NetworkServer

        fail = False
        try:
            self.interface.server = NetworkServer('', replayServerPort,
                                            settings = {'replayFile': fname})
        except Exception, e:
            # Creating a local server failed
            print "Exception: " + str(e)

        else:
            # Actually connect.
            result = self.interface.netClient.connectByPort("localhost", replayServerPort)
            self.connectingDeferred = result
            result.addCallback(self.interface.connectionEstablished).addErrback(
            self.connectionFailed)

    def cancelConnect(self):
        # Called when user clicks "cancel" while connecting.
        # TODO
        self.mainMenu()

    def connectionFailed(self, reason):
        # TODO
        print 'CONNECTION FAILED: %s' % (reason,)
        self.mainMenu()
        return reason

    def connectionComplete(self):
        'Called by main interface object after connection is made.'
        self.mainMenu()
    
    def startServer(self, serverName, halfMapWidth = None, mapHeight = None,
                    maxPlayers = None, gameDuration = None, recordReplay = None):
        self.interface.startServer(serverName, halfMapWidth, mapHeight,
                                   maxPlayers, gameDuration, recordReplay)
