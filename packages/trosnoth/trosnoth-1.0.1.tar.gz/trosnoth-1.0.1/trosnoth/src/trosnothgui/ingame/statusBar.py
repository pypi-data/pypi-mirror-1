# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2007  Joshua Bartlett
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

'''statusBar.py - defines the StatusBar class which deals with drawing the
zone tallies and time remaining onto the screen.'''

import pygame
import random

from twisted.internet import reactor
from trosnoth.src.gui.framework.elements import TextElement
from trosnoth.src.gui.framework import clock, timer
from trosnoth.src.gui.common import *
import trosnoth.src.gui.framework.framework as framework
from trosnoth.src.trosnothgui.ingame.messagebank import MessageBank
from trosnoth.src.trosnothgui.ingame import colours
from trosnoth.src.gui.fonts import font
from trosnoth.src.universe_base import GameState

class ZoneProgressBar(framework.CompoundElement):
    def __init__(self, app, world, gameViewer):
        super(ZoneProgressBar, self).__init__(app)
        self.world = world
        self.gameViewer = gameViewer
        self.app = app

        self.mapLeft = self.gameViewer.miniMap.sRect.left
        self.mapRight = self.gameViewer.miniMap.sRect.right
        self.mapBottom = self.gameViewer.miniMap.sRect.bottom

        self.width = max(int(3*self.app.screenManager.scaleFactor), 1)
        # Anything more than width 2 looks way too thick
        if self.width > 2:
            self.width = 2

        self.black = colours.black
        self.blue = colours.team1Mn_zone
        self.red = colours.team2Mn_zone
        self.grey = colours.zoneBarNeutral

        # Define a few constants to make things easier
        self.triangleLength = 25
        self.sideDistance = 4
        self.barHeight = self.gameViewer.zoneBarHeight
        self.textSpace = 130
        self.neutralTextSpace = 15

        self.barFont = font.Font('JENKT___.TTF', 35)

    def draw(self, surface):
        super(ZoneProgressBar, self).draw(surface)
        
        # Automatically generated constants
        yTop = self.mapBottom - 1
        yBottom = yTop + self.barHeight
        yText = yTop - 7

        xFarLeft = self.mapLeft + self.sideDistance
        xFarRight = self.mapRight - self.sideDistance

        xLeft = xFarLeft + self.triangleLength
        xRight = xFarRight - self.triangleLength

        # Define the coordinates for the static shapes
        border = [(xFarLeft, yTop),
                  (xFarRight, yTop),
                  (xRight, yBottom),
                  (xLeft, yBottom)]

        blueTriangle = [(xFarLeft, yTop),
                        (xLeft, yTop),
                        (xLeft, yBottom)]

        redTriangle = [(xFarRight, yTop),
                       (xRight, yTop),
                       (xRight, yBottom)]

        # Get the information we need
        blueZones = self.world.teams[0].numOrbsOwned
        redZones = self.world.teams[1].numOrbsOwned
        totalZones = len(self.world.zones)
        neutralZones = totalZones - blueZones - redZones

        if blueZones == 0 or redZones == 0:
            gameOver = True
        else:
            gameOver = False

        # Define the coordinates for the dynamic shapes
        mutableBarLength = xRight - xLeft
        if redZones > 0:
            blueBarLength = round(mutableBarLength * ((blueZones * 1.0) / totalZones))
        else:
            blueBarLength = mutableBarLength
        if blueZones > 0:
            redBarLength = round(mutableBarLength * ((redZones * 1.0) / totalZones))
        else:
            redBarLength = mutableBarLength
        neutralBarLength = mutableBarLength - blueBarLength - redBarLength

        xNeutral = ((xLeft + blueBarLength) + (xRight - redBarLength)) / 2

        xFirstBar = xLeft + blueBarLength
        xSecondBar = xRight - redBarLength

        blueBar = [(xLeft, yTop),
                   (xLeft + blueBarLength, yTop),
                   (xLeft + blueBarLength, yBottom),
                   (xLeft, yBottom)]
        redBar = [(xRight - redBarLength, yTop),
                  (xRight, yTop),
                  (xRight, yBottom),
                  (xRight - redBarLength, yBottom)]
        greyBar = [(xLeft + blueBarLength + 1, yTop),
                   (xRight - redBarLength - 1, yTop),
                   (xRight - redBarLength - 1, yBottom),
                   (xLeft + blueBarLength + 1, yBottom)]
                   
        # Draw the two triangles on the sides
        if blueZones > 0:
            pygame.draw.polygon(surface, self.blue, blueTriangle, 0)
        else:
            pygame.draw.polygon(surface, self.red, blueTriangle, 0)
        if redZones > 0:
            pygame.draw.polygon(surface, self.red, redTriangle, 0)
        else:
            pygame.draw.polygon(surface, self.blue, redTriangle, 0)

        # Draw the team colours
        if blueZones > 0:
            pygame.draw.polygon(surface, self.blue, blueBar, 0)
        if redZones > 0:
            pygame.draw.polygon(surface, self.red, redBar, 0)
        if neutralZones > 0 and not gameOver:
            pygame.draw.polygon(surface, self.grey, greyBar, 0)

        # Draw the black seperator line(s)
        if not gameOver:
            pygame.draw.line(surface, self.black, (xFirstBar, yTop), (xFirstBar, yBottom), self.width)
            if neutralZones != 0:
                pygame.draw.line(surface, self.black, (xSecondBar, yTop), (xSecondBar, yBottom), self.width)

        # Draw the border last so that it goes on top
        pygame.draw.polygon(surface, self.black, border, self.width)
        pygame.draw.line(surface, colours.minimapBorder, (self.mapLeft, self.mapBottom - 1), (self.mapRight, self.mapBottom - 1), 2)

        # Define the necessary text       
        self.blueText = TextElement(self.app, '', self.barFont,
                                    Location((xFirstBar - 3, yText), 'topright'),
                                    colour = colours.black)
        self.neutralText = TextElement(self.app, '', self.barFont,
                                    Location((xNeutral, yText), 'midtop'),
                                    colour = colours.black)
        self.redText = TextElement(self.app, '', self.barFont,
                                    Location((xSecondBar + 3, yText), 'topleft'),
                                    colour = colours.black)

        blueString = str(blueZones)
        redString = str(redZones)

        if xSecondBar - xFirstBar < self.neutralTextSpace:
            neutralString = ""
        else:
            neutralString = str(neutralZones)

        self.blueText.setText(blueString)
        self.redText.setText(redString)
        self.neutralText.setText(neutralString)

        # Draw the text
        if blueZones > 0:
            self.blueText.draw(surface)
        if redZones > 0:
            self.redText.draw(surface)
        if neutralZones > 0 and not gameOver:
            self.neutralText.draw(surface)

class TimerBar(framework.CompoundElement):
    def __init__(self, app, world):
        super(TimerBar, self).__init__(app)
        self.world = world
        self.app = app

        # Change these constants to say where the box goes
        self.area = Area(FullScreenAttachedPoint(ScaledSize(0, -3), 'midtop'), ScaledSize(110, 35), 'midtop')

        self.lineWidth = max(int(3*self.app.screenManager.scaleFactor), 1)
        # Anything more than width 2 looks way too thick
        if self.lineWidth > 2:
            self.lineWidth = 2
        self.notStarted = TextElement(self.app, "--:--",
                                      self.app.screenManager.fonts.timerFont,
                                      Location(FullScreenAttachedPoint(ScaledSize(0, -17), 'midtop'), 'midtop'),
                                      colours.timerFontColour)
        self.elements = [self.notStarted]
    
        self.gameTimer = None
        self.gameOver = False
        self.timerAdjustLoop = None
        
        self.loop()

    def loop(self):
        if self.world.gameState in (GameState.PreGame, GameState.Ended):
            return

##        # sync the clock every 10 seconds
##        if self.world.gameState == GameState.InProgress:
##            self.timerAdjustLoop = reactor.callLater(10, self.loop)
      
      
        if self.gameTimer is None:
            timeLeft = self.world.getTimeLeft()
            self.gameStarted(timeLeft)
                
        self.syncTimer()

    def syncTimer(self):
        if self.world.gameState in (GameState.PreGame, GameState.Ended):
            return
        time = self.world.getTimeLeft()
        
        if time < 0:
            self.gameTimer.counted = -time
        else:
            self.gameTimer.countTo = time
            self.gameTimer.counted = 0

    def kill(self):
        if self.world.gameState == GameState.InProgress and self.timerAdjustLoop is not None:
            self.timerAdjustLoop.cancel()
        self.gameTimer = None

    def gameStarted(self, time):

        if time > 0:
            self.gameTimer = timer.CountdownTimer(time, highest = "minutes")
        else:
            self.gameTimer = timer.Timer(startAt = -time, highest = "minutes")
            
        self.gameClock = clock.Clock(self.app, self.gameTimer,
                                     Location(FullScreenAttachedPoint(ScaledSize(0, -17), 'midtop'), 'midtop'),
                                     self.app.screenManager.fonts.timerFont,
                                     colours.timerFontColour)
        self.gameTimer.start()
        self.elements = [self.gameClock]

    def gameFinished(self):
        if self.timerAdjustLoop is not None:
            self.timerAdjustLoop.cancel()
            self.timerAdjustLoop = None
            self.gameTimer.pause()
            self.gameOver = True
        self.elements = [self.notStarted]

    def _getRect(self):
        return self.area.getRect(self.app)
        

    def draw(self, surface):
        super(TimerBar, self).draw(surface)

        timerBox = self._getRect()
        surface.fill(colours.timerBackground, timerBox)      # Box background
        pygame.draw.rect(surface, colours.black, timerBox, self.lineWidth)   # Box border
        
        super(TimerBar, self).draw(surface)
                    
