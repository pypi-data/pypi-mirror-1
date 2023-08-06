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

import pygame
from trosnoth.src.gui.framework import framework
from math import atan2

class PlayerInterface(framework.Element):
    '''Interface for controlling a player.'''

    # The virtual keys we care about.
    state_vkeys = frozenset(['left', 'right', 'jump', 'down'])

    def __init__(self, app, gameInterface, playerSprite):
        super(PlayerInterface, self).__init__(app)
        
        world = gameInterface.world
        self.gameInterface = gameInterface
        self.keyMapping = gameInterface.keyMapping

        self.receiving = True
        
        self.world = world
        self.playerSprite = playerSprite
        self.player = playerSprite.player
        rect = pygame.Rect((0,0), self.app.screenManager.scaledSize)

        # Make sure the viewer is focusing on this player.
        self.gameInterface.gameViewer.setTarget(playerSprite)


    def tick(self, deltaT):
        pos = pygame.mouse.get_pos()
        self.updatePlayerViewAngle(pos)
        
    def updatePlayerViewAngle(self, pos):
        '''Updates the viewing angle of the player based on the mouse pointer
        being at the position pos. This gets its own method because it needs
        to happen as the result of a mouse motion and of the viewManager
        scrolling the screen.'''
        
        # Angle is measured clockwise from vertical.
        if not self.playerSprite.rect.collidepoint(pos):
            dx = pos[0]-self.playerSprite.rect.center[0]
            dy = pos[1]-self.playerSprite.rect.center[1]
            theta = atan2(dx, -dy)
            dist = (dx ** 2 + dy ** 2) ** 0.5

            # Calculate a thrust value based on distance.
            if dist < 25:
                thrust = 0.0
            elif dist > 125:
                thrust = 1.0
            else:
                thrust = (dist - 25) / 100.

            self.player.lookAt(theta, thrust)

    def processEvent(self, event):
        '''Event processing works in the following way:
        1. If there is a prompt on screen, the prompt will either use the
        event, or pass it on.
        2. If passed on, the event will be sent back to the main class, for it
        to process whether player movement uses this event. If it doesn't use
        the event, it will pass it back.
        3. If so, the hotkey manager will see if the event means anything to it.
        If not, that's the end, the event is ignored.'''
        
        # Handle events specific to in-game.
        if self.player:
            if event.type == pygame.KEYDOWN:
                try:
                    stateKey = self.keyMapping[event.key]
                except KeyError:
                    return event

                if stateKey not in self.state_vkeys:
                    return event

                self.player.updateState(stateKey, True)
            elif event.type == pygame.KEYUP:
                try:
                    stateKey = self.keyMapping[event.key]
                except KeyError:
                    return event

                if stateKey not in self.state_vkeys:
                    return event

                self.player.updateState(stateKey, False)
            elif event.type == pygame.MOUSEMOTION:
                # FIXME: The following line generates glitches.
                # self.updatePlayerViewAngle(event.pos)
                pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Fire a shot.
                self.player.fireShot()
            else:
                return event
