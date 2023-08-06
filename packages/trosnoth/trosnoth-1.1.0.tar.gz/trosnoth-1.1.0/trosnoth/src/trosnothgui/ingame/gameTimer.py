# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2009  Joshua Bartlett
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
import random

from twisted.internet import reactor, task
from trosnoth.src.gui.framework.elements import TextElement
from trosnoth.src.gui.framework import clock, timer
from trosnoth.src.gui.common import *
import trosnoth.src.gui.framework.framework as framework
from trosnoth.src.trosnothgui.ingame import colours
from trosnoth.src.gui.fonts import font
from trosnoth.src.model.universe_base import GameState
from trosnoth.src.utils import logging

class GameTimer(framework.CompoundElement):
    def __init__(self, app, world):
        super(GameTimer, self).__init__(app)
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
                                      Location(FullScreenAttachedPoint(ScaledSize(0, -2), 'midtop'), 'midtop'),
                                      colours.timerFontColour)
        self.elements = [self.notStarted]

        self.flashControl = task.LoopingCall(self.flash)
    
        self.gameTimer = None
        self.gameOver = False
        self.timerAdjustLoop = None
        self.countingDown = None
        self.startedFlashing = False

        # Seconds between alternating flashes
        self.flashFreq = 0.25
        # Value the countdown has to get to before it starts to flash
        self.flashValue = 30

        self.flashState = 0
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

    def flash(self):
        try:
            self._flash()
        except:
            print 'UNHANDLED ERROR IN GameTimer.flash()'
            print
            logging.writeException()

    def _flash(self):
        if not self.countingDown:
            return
        
        if not self.startedFlashing:
            if self.gameTimer.getCurTime() <= self.flashValue:
                self.startedFlashing = True
            else:
                return

        if self.flashState == 0:
            self.gameClock.setColours(colours.timerFlashColour)
            self.flashState = 1
        else:
            self.gameClock.setColours(colours.timerFontColour)
            self.flashState = 0

    def kill(self):
        if self.world.gameState == GameState.InProgress and self.timerAdjustLoop is not None:
            self.timerAdjustLoop.cancel()
        self.gameTimer = None
        
        if self.flashControl.running:
            self.flashControl.stop()

    def gameStarted(self, time):

        if time > 0:
            self.gameTimer = timer.CountdownTimer(time, highest = "minutes")
            self.countingDown = True
        else:
            self.gameTimer = timer.Timer(startAt = -time, highest = "minutes")
            self.countingDown = False
            
        self.gameClock = clock.Clock(self.app, self.gameTimer,
                                     Location(FullScreenAttachedPoint(ScaledSize(0, -2), 'midtop'), 'midtop'),
                                     self.app.screenManager.fonts.timerFont,
                                     colours.timerFontColour)
        self.gameTimer.start()
        self.elements = [self.gameClock]

        self.flashControl.start(self.flashFreq)

    def gameFinished(self):
        if self.timerAdjustLoop is not None:
            self.timerAdjustLoop.cancel()
            self.timerAdjustLoop = None
            self.gameTimer.pause()
            self.gameOver = True
            self.flashControl.stop()
            self.gameClock.setColours(colours.timerFontColour)
        self.elements = [self.notStarted]

    def _getRect(self):
        return self.area.getRect(self.app)


    def draw(self, surface):     
        timerBox = self._getRect()
        surface.fill(colours.timerBackground, timerBox)      # Box background
        pygame.draw.rect(surface, colours.black, timerBox, self.lineWidth)   # Box border
        
        super(GameTimer, self).draw(surface)
