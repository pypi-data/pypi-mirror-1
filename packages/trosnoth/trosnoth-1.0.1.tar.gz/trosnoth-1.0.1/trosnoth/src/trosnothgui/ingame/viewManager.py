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

'''viewManager.py - defines the ViewManager class which deals with drawing the
state of a universe to the screen.'''

from math import sin, cos

import pygame

from trosnoth.src.utils.utils import new, timeNow
from trosnoth.src.utils.logging import writeException
from trosnoth.src import universe
from trosnoth.src.trosnothgui.ingame.minimap import MiniMap
from trosnoth.src.trosnothgui.ingame import colours
from trosnoth.src.gui.framework import framework, elements
from trosnoth.src.trosnothgui.ingame.leaderboard import LeaderBoard
from trosnoth.src.trosnothgui.ingame.statusBar import ZoneProgressBar, TimerBar
from trosnoth.src.trosnothgui.ingame.chatBox import ChatBox
from trosnoth.src.universe_base import GameState

from trosnoth.src.gui.common import Location, FullScreenAttachedPoint, ScaledSize

class ViewManager(framework.CompoundElement):
    '''A ViewManager object takes a given universe, and displays a screenfull
    of the current state of the universe on the specified screen object.  This
    class displays only a section of the universe and no other information
    (scores, menu etc.).
    
    Note: self._focus represents the position that the ViewManager is currently
    looking at.  self.target is what the ViewManager should be trying to look
    at.
    
    self.target = None - the ViewManager will use its algorithm to follow a
        point of action.
    self.target = (x, y) - the ViewManager will look at the specified point.
    self.target = player - the ViewManager will follow the specified player.
    '''
    
    # The fastest speed that the viewing position can shift in pixels per sec
    maxSpeed = 1800
    acceleration = 1080
    
    # How far ahead of the targeted player we should look.
    lengthFromPlayer = 125
    
    def __init__(self, app, universe, target=None):
        '''Called upon creation of a ViewManager object.  screen is a pygame
        screen object.  universe is the Universe object to draw.  target is
        either a point, a Player object, or None.  If target is None, the view
        manager will follow the action, otherwise it will follow the specified
        point or player.'''
        super(ViewManager, self).__init__(app)
        self.setTarget(target)
        self.universe = universe
        
        self.sRect = pygame.Rect((0,0), self.app.screenManager.size)
        
        # self._focus represents the point where the viewManager is currently
        # looking.
        self._focus = (universe.map.layout.centreX, universe.map.layout.centreY)
        self.lastUpdateTime = timeNow()
        self.speed = 0          # Speed that the focus is moving.
        
        # Create a surface for storing the background stuff.
        self.backdrop = pygame.surface.Surface(self.sRect.size).convert()
        self.spareCanvas = pygame.surface.Surface(self.sRect.size).convert()
        
        # Now fill the backdrop with what we're looking at now.
        self.drawBackdropRect(self.sRect)

    def setTarget(self, target):
        '''Makes the viewManager's target the specified value.'''
        self.target = target
        if isinstance(self.target, universe.Player):
            # Move directly to looking at player.     
            self._focus = target.pos
            self.reDraw()
        elif isinstance(self.target, (tuple, list)):
            pass
        else:
            self.autoFocusInfo = [0, []]
        
    def getTargetPoint(self):
        '''Returns the position of the current target.'''
        if self.target is None:
            return self._focus
        if isinstance(self.target, universe.Player):
            return self.target.pos
        return self.target

    def draw(self, screen):
        '''Draws the current state of the universe at the current viewing
        location on the screen.  Does not call pygame.display.flip()'''
        # Update where we're looking at.
        deltaBackdrop = self.updateFocus()
        
        # Create the new backdrop canvas, scrolling the backdrop.
        self.spareCanvas.blit(self.backdrop, deltaBackdrop)
        self.spareCanvas, self.backdrop = self.backdrop, self.spareCanvas
                
        # Fill in the parts which need filling.
        x, y = deltaBackdrop
        yTop = 0
        yHeight = self.sRect.height - abs(y)
        if y > 0:
            # Fill in a gap at the top.
            self.drawBackdropRect(pygame.Rect(0, 0, self.sRect.width, y))
            yTop = y
        elif y < 0:
            # Fill gap at bottom.
            self.drawBackdropRect(pygame.Rect(0, yHeight, self.sRect.width, -y))
        if x > 0:
            # Fill in gap at left.
            self.drawBackdropRect(pygame.Rect(0, yTop, x, yHeight))
        elif x < 0:
            # Fill in gap at right.
            self.drawBackdropRect(pygame.Rect(self.sRect.width + x, yTop, \
                                              -x, yHeight))
        
        # Now put the backdrop onto the screen.
        screen.blit(self.backdrop, (0,0))
        
        # Go through and update the positions of the players on the screen.
        ntGroup = pygame.sprite.Group()
        visPlayers = pygame.sprite.Group()
        for player in self.universe.players:
            # Calculate the position of the player.
            player.rect.center = [player.pos[i] - self._focus[i] + \
                    self.sRect.center[i] for i in (0,1)]
        
            # Check if this player needs its nametag shown.
            if player.rect.colliderect(self.sRect):
                visPlayers.add(player)
                player.nametag.rect.midtop = player.rect.midbottom
                # Check that entire nametag's on screen.
                if player.nametag.rect.left < self.sRect.left:
                    player.nametag.rect.left = self.sRect.left
                elif player.nametag.rect.right > self.sRect.right:
                    player.nametag.rect.right = self.sRect.right
                if player.nametag.rect.top < self.sRect.top:
                    player.nametag.rect.top = self.sRect.top
                elif player.nametag.rect.bottom > self.sRect.bottom:
                    player.nametag.rect.bottom = self.sRect.bottom
                ntGroup.add(player.nametag)
                
                # Place the star rectangle below the nametag.
                mx, my = player.nametag.rect.midbottom
                player.starTally.rect.midtop = (mx, my-5)
                ntGroup.add(player.starTally)
        
        # Draw the on-screen players and nametags.
        visPlayers.draw(screen)
        ntGroup.draw(screen)
        ntGroup.empty()
        
        # Draw the shots.
        for shot in self.universe.shots:
            # Calculate the position of the player.
            shot.rect.center = [shot.pos[i] - self._focus[i] + \
                    self.sRect.center[i] for i in (0,1)]
        
        self.universe.shots.draw(screen)
        try:
            # Draw the grenades.
            for grenade in self.universe.grenades:
                # Calculate the position of the player.
                grenade.rect.center = [grenade.pos[i] - self._focus[i] + \
                        self.sRect.center[i] for i in (0,1)]
            self.universe.grenades.draw(screen)
        except:
            writeException()

    def drawBackdropRect(self, rect):
        '''Updates the contents of the backdrop surface within the specified
        rect. Called when the screen scrolls.'''
        self.backdrop.fill((64, 0, 64), rect)
        
        # Find which map blocks are within the bounds of that rect.
        i, j = universe.MapLayout.getMapBlockIndices(self._focus[0] - self.sRect.center[0] + rect.left - self.sRect.left,
                                                     self._focus[1] - self.sRect.center[1] + rect.top - self.sRect.top)
        
        y = i
        while True:
            if y < 0:
                y += 1
                continue
            try:
                row = self.universe.zoneBlocks[y]
            except IndexError:
                break
            x = j
            first = True
            while True:
                if x < 0:
                    x += 1
                    continue
                try:
                    block = row[x]
                except IndexError:
                    break
                
                # Put the block in its rightful place.
                block.drawRect.topleft = [block.pos[n] - self._focus[n] + \
                                          self.sRect.center[n] for n in (0,1)]
                # Draw the block.
                if block.drawRect.colliderect(rect):
                    crop = rect.clip(block.drawRect)
                    block.draw(self.backdrop, crop)
                    x += 1
                    first = False
                else:
                    break
            y += 1
            if first:
                # Not even the first one was drawn; it must have drawn enough
                # rows
                break
                                               
    def updateFocus(self):
        '''Updates the location that the ViewManager is focused on.  First
        calculates where it would ideally be focused, then moves the focus
        towards that point. The focus cannot move faster than self.maxSpeed 
        pix/s, and will only accelerate or decelerate at self.acceleration
        pix/s/s. This method returns the negative of the amount scrolled by.
        This is useful for moving the backdrop by the right amount.
        '''
        
        # Calculate where we should be looking at.
        if isinstance(self.target, universe.Player):
            # Take into account where the player's looking.
            plPos = self.target.pos
            plAngle = self.target.angleFacing

            radius = self.target.distanceToTarget
            if radius == None or radius > self.lengthFromPlayer:
                radius = self.lengthFromPlayer
                
            targetPt = (plPos[0] + radius * sin(plAngle),
                        plPos[1] - radius * cos(plAngle))

            # If the player no longer exists, look wherever we want.
            if self.target not in self.universe.players:
                self.setTarget(None)
        elif isinstance(self.target, (tuple, list)):
            targetPt = self.target
        else:
            # Follow the action.
            countdown, players = self.autoFocusInfo

            # First check for non-existent players.
            for i in range(len(players)):
                if players[-i-1] not in self.universe.players:
                    players.pop(-i-1)

            if len(self.universe.players) == 0:
                # No players anywhere. No change.
                targetPt = tuple(self._focus)
            elif len(players) == 0:
                # No players in view. Look for action.
                # Less than 4 players. Look for more action.
                maxP = 0
                curZone = None
                for z in self.universe.zones:
                    count = len(z.players) + len(z.nonPlayers)
                    if count > maxP:
                        maxP = count
                        curZone = z
                self.autoFocusInfo[1] = list(curZone.players) + \
                                        list(curZone.nonPlayers)

                targetPt = tuple(self._focus)
                countdown = 10
            else:
                # Look at centre-of-range of these players.
                minPos = [min(p.pos[i] for p in players) for i in (0,1)]
                maxPos = [max(p.pos[i] for p in players) for i in (0,1)]
                targetPt = [0.5 * (minPos[i] + maxPos[i]) for i in (0,1)]

                # Every 10 iterations recheck details.
                if countdown <= 0:
                    # Count players in view.
                    numInView = 0
                    for p in self.universe.players:
                        if abs(p.pos[0] - targetPt[0]) < self.app.screenManager.scaledSize[0] and \
                                abs(p.pos[1] - targetPt[1]) < self.app.screenManager.scaledSize[1]:
                            numInView += 1

                    if numInView < 4:
                        # Less than 4 players. Look for more action.
                        maxP = 0
                        curZone = None
                        for z in self.universe.zones:
                            count = len(z.players) + len(z.nonPlayers)
                            if count > maxP:
                                maxP = count
                                curZone = z
                        self.autoFocusInfo[1] = list(curZone.players) + \
                                                list(curZone.nonPlayers)
                    countdown = 10
                countdown -= 1
        
        # Calculate time that's passed.
        now = timeNow()
        deltaT = now - self.lastUpdateTime
        self.lastUpdateTime = now
        
        # Calculate distance to target.
        sTarget = sum((targetPt[i] - self._focus[i])**2 for i in (0,1)) ** 0.5
        
        if sTarget == 0:
            return (0, 0)
        
        # Calculate the maximum velocity that will result in deceleration to
        # reach target. This is based on v**2 = u**2 + 2as
        vDecel = (2. * self.acceleration * sTarget) ** 0.5
        
        # Actual velocity is limited by this and maximum velocity.
        self.speed = min(self.maxSpeed, vDecel, \
                         self.speed + self.acceleration * deltaT)
        
        # Distance travelled should never overshoot the target.
        s = min(sTarget, self.speed * deltaT)
        
        # How far does the backdrop need to move by?
        #  (This will be negative what the focus moves by.)
        deltaBackdrop = tuple(round(-s * (targetPt[i] - self._focus[i]) \
                                    / sTarget, 0) for i in (0,1))
        
        # Calculate the new focus.
        self._focus = tuple(round(self._focus[i] - deltaBackdrop[i], 0) \
                            for i in (0,1))
        
        # Return the distance the backdrop must be moved.
        return deltaBackdrop

    def reDraw(self):
        self.drawBackdropRect(self.sRect)

class PregameMessage(elements.TextElement):
    def __init__(self, app):
        super(PregameMessage, self).__init__(
            app,
            'Game will begin when both captains signal ready.',
            app.screenManager.fonts.bigMenuFont,
            Location(FullScreenAttachedPoint((0, -150), 'center'), 'center'),
            colours.pregameMessageColour
        )

class GameViewer(framework.CompoundElement):
    '''The gameviewer comprises a viewmanager and a minimap, which can be
    switched on or off.'''

    # Needs to be declared here instead of in statusBar.py so that the
    # leaderboard can use it
    zoneBarHeight = 25

    def __init__(self, app, gameInterface, world):
        super(GameViewer, self).__init__(app)
        self.interface = gameInterface
        self.world = world
        self.app = app

        self.viewManager = ViewManager(self.app, world)
        miniMapSize = (min(self.app.screenManager.scaledSize[0] / 100 * 35, 300),
                    min(self.app.screenManager.scaledSize[1] / 100 * 35, 200))
        self.miniMap = MiniMap(self.app, (self.app.screenManager.size[0] - miniMapSize[0] - 5, 5),\
                                       miniMapSize, 20, world, \
                                       self.viewManager)

        xPos = int(self.app.screenManager.scaleFactor * -40)
        yPos = self.miniMap.sRect.bottom + self.zoneBarHeight + 10
        self.leaderboard = LeaderBoard(self.app, self.world, 50, Location(FullScreenAttachedPoint((xPos, yPos), 'topright'), 'topright'), 'right', 'top', self.app.screenManager.fonts.messageFont)
        self.zoneBar = ZoneProgressBar(app, world, self)
        self.timerBar = TimerBar(app, world)
        self.chatBox = ChatBox(self.app, self.world, self)

        self.pregameMessage = PregameMessage(self.app)
        if world.gameState == GameState.InProgress:
            self.pregameMessage.setText('')

        self.elements = [self.viewManager, self.miniMap, self.pregameMessage]

        self.minimapDisruptor = None

        # Show zone bar and timer by default.
        self.toggleZoneProgress()
        self.toggleTimer()
                
    def setTarget(self, target):
        'Target should be a player, a point, or None.'
        self.viewManager.setTarget(target)
        if isinstance(target, universe.Player):
            if self.minimapDisruptor:
                if target.team != self.minimapDisruptor.team:
                    self.miniMap.disrupted()
                else:
                    self.miniMap.endDisruption()
        
    def tick(self, deltaT):
        self.world.tick()
        super(GameViewer, self).tick(deltaT)

    def minimapDisruption(self, player):
        self.minimapDisruptor = player
        if isinstance(self.viewManager.target, universe.Player):
            if player.team != self.viewManager.target.team:
                self.miniMap.disrupted()

    def endMinimapDisruption(self):
        self.minimapDisruptor = None
        self.miniMap.endDisruption()

    def toggleLeaderBoard(self):
        if self.leaderboard in self.elements:
            self.elements.remove(self.leaderboard)
        else:
            self.elements.append(self.leaderboard)

    def toggleZoneProgress(self):
        if self.zoneBar in self.elements:
            self.elements.remove(self.zoneBar)
        else:
            self.elements.append(self.zoneBar)

    def toggleTimer(self):
        if self.timerBar in self.elements:
            self.elements.remove(self.timerBar)
        else:
            self.elements.append(self.timerBar)
            self.timerBar.syncTimer()

    def openChat(self, player):
        self.chatBox.reset()
        self.chatBox.setPlayer(player)
        self.chatBox.Show()

    def closeChat(self):
        self.chatBox.Close()
        
