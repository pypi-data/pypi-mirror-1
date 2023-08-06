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

'''interface.py - defines the Interface class which deals with drawing the
game to the screen, including menus and other doodads.'''

import pygame

from trosnoth.src.network import networkClient
from trosnoth.src import replays

from trosnoth.src.gui.framework import framework, elements

from trosnoth.src.trosnothgui.pregame.startupInterface import StartupInterface
from trosnoth.src.trosnothgui.pregame.connectingScreen import ConnectingScreen
from trosnoth.src.trosnothgui.pregame.backdrop import TrosnothBackdrop
from trosnoth.data import loadSprite

from trosnoth.src.utils import logging
from trosnoth.src.trosnothgui.defines import *
from trosnoth.src.trosnothgui import pregame


from trosnoth.src.trosnothgui.pregame.connectionFailedDialog import ConnectionFailedDialog
from trosnoth.src.trosnothgui.ingame.interfaceComponent import InterfaceComponent
from trosnoth.src.trosnothgui.ingame.gameInterface import GameInterface

class Interface(framework.CompoundElement):
    def __init__(self, app):
        super(Interface, self).__init__(app)
        
        # Create an interfaces for pre- and post-connection.
        self.backdrop = TrosnothBackdrop(app)
        self.startupInterface = StartupInterface(app, self)
        
        self._buildPointer()
        self.gi = None
        
        self.elements = [self.backdrop, self.startupInterface]

    def _buildPointer(self):
        img = loadSprite('pointer.bmp')
        img.set_colorkey((255,255,255))
        pointer = elements.PictureElement(self.app, img, pygame.mouse.get_pos())
        self.app.screenManager.setPointer(pointer)
        pygame.mouse.set_visible(0)

    def processEvent(self, event):
        # Capture the quit event.
        if event.type == pygame.QUIT:                
            self.app.stop()
            return
        return super(Interface, self).processEvent(event)
    
    def connectToServer(self, host, port):
        self.elements = [
            self.backdrop,
            ConnectingScreen(self.app, '%s:%s' % (host, port),
                onCancel=self.cancelConnecting)
        ]

        self.netClient = networkClient.NetworkClient(self.app)
        self.netClient.onClosed.addListener(self.connectionLost)

        result = self.netClient.connectByPort(host, port)
        result.addCallback(self.connectionEstablished, self.netClient).addErrback(
                self.connectionFailed)
        return result

    def cancelConnecting(self, source):
        self.netClient.cancelConnecting()
        self.startupInterface.mainMenu()

    def connectionEstablished(self, world, netClient):
        'Called when this client establishes a connection to a server.'
        self.startupInterface.mainMenu()
        self.setupGame(world, netClient)

        self.elements = [self.gi]

    def setupGame(self, world, client):
        '''
        Used for both replays and games.
        '''
        # Create a game interface.
        self.gi = GameInterface(self.app, client, world)

        # Plug it to the netclient        
        interface = InterfaceComponent(self.gi)
        client.viewPlug.connectPlug(interface.plug)
        world.actionPlug.connectPlug(interface.plug)

        # A hack for now.
        di = self.gi.detailsInterface
        world.onUpgradeUsed.addListener(di.upgradeUsed)
        world.onUpgradeDestroyed.addListener(di.upgradeDestroyed)
        world.onTurretBegin.addListener(di.turretStarted)
        world.onTurretEnd.addListener(di.turretEnded)
        world.onMinimapBegin.addListener(self.gi.minimapDisruption)
        world.onMinimapEnd.addListener(self.gi.endMinimapDisruption)

    def connectionFailed(self, reason):
        self.elements = [self.backdrop, self.startupInterface]
        if not isinstance(reason, networkClient.UnableToConnect):
            print 'Unexpected failure in deferred: %s' % (reason.value,)
        d = ConnectionFailedDialog(self.app, str(reason.value))
        d.Show()

    def connectionLost(self, reason = None):
        self.elements = [self.backdrop, self.startupInterface]
        if reason is not None:
            if self.gi:
                self.gi.connectionLost()
                self.gi = None
            d = ConnectionFailedDialog(self.app, reason)
            d.Show()
        
    def connectToReplay(self, filename):
        self.startupInterface.mainMenu()

        client = replays.makeClient(self.app, filename)
        world = client.world
        client.onClosed.addListener(self.connectionLost)
        self.setupGame(world, client)

        self.elements = [self.gi]

