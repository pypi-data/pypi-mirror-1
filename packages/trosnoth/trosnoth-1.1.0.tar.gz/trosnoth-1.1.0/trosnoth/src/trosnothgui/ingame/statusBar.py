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

'''statusBar.py - defines the StatusBar class which deals with drawing the
zone tallies onto the screen.'''

import pygame
import random

from twisted.internet import reactor, task
from trosnoth.src.gui.framework.elements import TextElement
from trosnoth.src.gui.common import *
import trosnoth.src.gui.framework.framework as framework
from trosnoth.src.trosnothgui.ingame import colours
from trosnoth.src.gui.fonts import font
from trosnoth.src.model.universe_base import GameState

class ZoneProgressBar(framework.CompoundElement):
    def __init__(self, app, world, gameViewer):
        super(ZoneProgressBar, self).__init__(app)
        self.world = world
        self.gameViewer = gameViewer
        self.app = app

        self.mapLeft = self.gameViewer.miniMap.sRect.left
        self.mapRight = self.gameViewer.miniMap.sRect.right
        self.mapBottom = self.gameViewer.miniMap.sRect.bottom

        # Width will always be between 1 and 2 inclusive
        self.width = min(max(int(3*self.app.screenManager.scaleFactor), 1), 2)

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

        self.barFont = app.screenManager.fonts.zoneBarFont

    def draw(self, surface):
        super(ZoneProgressBar, self).draw(surface)
        
        # Automatically generated constants
        yTop = self.mapBottom - 1
        yBottom = yTop + self.barHeight
        yText = yTop

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
                    
