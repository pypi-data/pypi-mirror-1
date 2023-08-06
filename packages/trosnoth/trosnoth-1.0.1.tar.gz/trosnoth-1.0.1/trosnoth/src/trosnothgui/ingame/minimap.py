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

'''miniMap.py - defines the MiniMap class which deals with drawing the
miniMap to the screen.'''

from math import sin, cos
import random
import pygame
import trosnoth.src.universe as universe
from trosnoth.src.universe import MapLayout
import trosnoth.src.gui.framework.framework as framework
from trosnoth.src.gui.framework.basics import Animation
from trosnoth.src.trosnothgui.ingame import colours

# TODO: Get a full-screen minimap upon a hotkey.

class MiniMap(framework.Element):

    def __init__(self, app, offset, size, scale, universe, viewManager):
        '''Called upon creation of a ViewManager object.  screen is a pygame
        screen object.  universe is the Universe object to draw.  target is
        either a point, a Player object, or None.  If target is None, the view
        manager will follow the action, otherwise it will follow the specified
        point or player.'''
        super(MiniMap, self).__init__(app)
        self.scale = scale
        self.universe = universe
        self.viewManager = viewManager
        self.disrupt = False
        # Initialise the graphics in all the mapBlocks
        self.bodyRect = pygame.rect.Rect(0, 0, MapLayout.zoneBodyWidth / scale,
                                         MapLayout.halfZoneHeight / scale)
        self.interfaceRect = pygame.rect.Rect(0, 0, MapLayout.zoneInterfaceWidth / \
                                scale, MapLayout.halfZoneHeight / scale)
        
        universeSize = len(universe.zoneBlocks[0]), len(universe.zoneBlocks)

        mapHeight = universeSize[1] * self.bodyRect.height - 3
        mapWidth = (universeSize[0] / 2) * self.bodyRect.width + \
                   (universeSize[0] / 2 + 1) * self.interfaceRect.width - 3

        actualSize = (min(mapWidth, size[0]), min(mapHeight, size[1]))
        
        self.sRect = pygame.rect.Rect(offset, actualSize)
        self.disruptAnimation = self.createDisrupted()
        
        # Find the position at which the map should stop scrolling to the right
        # or to the bottom
        sizes = (self.interfaceRect.size, self.bodyRect.size)
        # The edge of the map will always be an interfaceMapBlock
        a = 0
        indices = (len(self.universe.zoneBlocks) - 1,
                   len(self.universe.zoneBlocks[0]) - 1)
        block = self.universe.zoneBlocks[indices[0]][indices[1]]
        pos = block.rect.bottomright
        self.rightMostPos = (pos[0] - self.sRect.size[0] * scale / 2,
                             pos[1] - self.sRect.size[1] * scale / 2)
        self.leftMostPos = (self.sRect.size[0] * scale / 2,
                            self.sRect.size[1] * scale / 2)
        
        # self._focus represents the point where the miniMap is currently
        # looking.
        self._focus = None
        self.updateFocus()

    def draw(self, screen):
        '''Draws the current state of the universe at the current viewing
        location on the screen.  Does not call pygame.display.flip() .'''

        pygame.draw.rect(screen, colours.black, self.sRect, 0)

        # If disrupted, draw static 95% of the time
        if self.disrupt and random.random() > 0.05:
            self.drawDisrupted(screen)
            return
        
        # Update where we're looking at.
        self.updateFocus()

        self.drawZones(screen)

        # DRAW PLAYERS
        
        # Go through and update the positions of the players on the screen.
        for player in self.universe.players:
            # Calculate the position of the player.
            playerPos = [(player.pos[i] - self._focus[i]) / self.scale + \
                                  self.sRect.center[i] for i in (0,1)]
            if self.sRect.collidepoint(*playerPos):
                
                # The player being drawn is the one controlled by the user.
                if player == self.viewManager.target:
                    clr = colours.minimapOwnColour
                    radius = 3

                else:
                    if player.ghost:
                        clr = player.team.miniMapGhostColour
                    else:
                        clr = player.team.miniMapPlayerColour
                    radius = 2
                playerPos = [int(playerPos[i]) for i in (0,1)]
                pygame.draw.circle(screen, clr, playerPos, radius)



        
        # Draw the shots.
        for shot in self.universe.shots:
            # Calculate the position of the player.
            shotPos = [(shot.pos[i] - self._focus[i]) / self.scale + \
                    self.sRect.center[i] for i in (0,1)]
            if self.sRect.collidepoint(*shotPos):
                shotPos = [int(shotPos[i]) for i in (0,1)]
                pygame.draw.circle(screen, colours.white, shotPos, 0)

    def drawZones(self, screen):
        '''Draws the miniMap graphics onto the screen'''
        # TODO: It's still a few pixels out on the bottom of the minimap
        topCorner = [self._focus[i] - (self.sRect.size[i] / 2 * self.scale) \
                     for i in (0,1)]
        # Find which map blocks are on the screen.
        i, j = MapLayout.getMapBlockIndices(*topCorner)
        i = max(0, i)
        j = max(0, j)
        firstBlock = self.universe.zoneBlocks[i][j]
        
        
        # Set the initial position back to where it should be.
        firstPos = [min((firstBlock.rect.topleft[a] - topCorner[a]) / self.scale +\
                    self.sRect.topleft[a], self.sRect.topleft[a]) for a in (0,1)]        
            
        posToDraw = [firstPos[a] for a in (0,1)]
        y, x = i, j
        while True:
            while True:
                try:
                    block = self.universe.zoneBlocks[y][x]
                except IndexError:
                    break
                if isinstance(block, universe.InterfaceMapBlock):
                    currentRect = self.interfaceRect
                else:
                    currentRect = self.bodyRect
                currentRect.topleft = posToDraw
                area = currentRect.clip(self.sRect)
                if area.size == currentRect.size:
                    # Nothing has changed.
                    block.drawMiniBg(screen, self.scale, currentRect)
                elif area.size == (0,0):
                    # Outside the bounds of the minimap
                    pass
                else:
                    block.drawMiniBg(screen, self.scale, currentRect, area)

                posToDraw[0] += currentRect.width
                if posToDraw[0] > self.sRect.right:
                    break
                x += 1
            x = j
            y += 1
            # Next Row
            posToDraw[0] = firstPos[0]
            # Add the height; could use either bodyRect or interfaceRect; they
            # have the same height.
            posToDraw[1] += self.interfaceRect.height
            if posToDraw[1] > self.sRect.bottom:
                break
        pygame.draw.rect(screen, colours.minimapBorder, self.sRect, 2)

                                               
    def updateFocus(self):
        if isinstance(self.viewManager.target, universe.Player):
            self._focus = self.viewManager.target.pos
        elif self.viewManager.target == None:
            self._focus = self.viewManager._focus
        else:
            self._focus = self.viewManager.target
            
        self._focus = [max(min(self._focus[i], self.rightMostPos[i]),\
                           self.leftMostPos[i]) for i in (0,1)]

    def disrupted(self):
        self.disrupt = True

    def endDisruption(self):
        self.disrupt = False

    def createDisrupted(self):
        screens = []
        for a in range(0,4):
            screen = (pygame.surface.Surface(self.sRect.size))
            x = y = yy = 0
            rect = pygame.rect.Rect(0,0,2,2)
            disruptColours = [colours.black, colours.white]
            while x < self.sRect.right:
                while y < self.sRect.bottom:
                    rect.top = y
                    pygame.draw.rect(screen, random.choice(disruptColours), rect, 0)
                    y += 2
                y = yy
                rect.left = x
                x += 2
            pygame.draw.rect(screen, colours.minimapBorder, self.sRect, 2)
            screens.append(screen)
        return Animation(0.1, *screens)
        


    def drawDisrupted(self, screen):
        screen.blit(self.disruptAnimation.getImage(), self.sRect.topleft)
                
        
