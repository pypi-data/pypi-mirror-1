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

from framework import Element, CompoundElement
from elements import TextButton, TextElement
from trosnoth.src.gui.common import translateEvent, Location
from trosnoth.src.gui.fonts.fontcache import get as getFont
from trosnoth.src.utils.event import Event
from trosnoth.src.utils.utils import new
import pygame


class ScrollableCanvas(CompoundElement):
    # For a scrollable canvas, the displaySize is
    # how big it will actually be drawn, while its
    # size is how big the canvas is in memory.
    # If the size is bigger than the displaySize
    # either horizontally or vertically, there will
    # be a scroll bar to allow moving around the
    # full area.

    class ScrollBar(Element):
        defaultWidth = 15
        defaultButtonChange = 20 ## number of pixels moved when button is pressed
        defaultColour = (0,255,0)
        defaultBackColour = (128,128,128)
        def __init__(self, app, parent, fullSize, displaySize, pos, horizontal = False):
            super(ScrollableCanvas.ScrollBar, self).__init__(app)
            self.width = self.defaultWidth
            self.buttonChange = self.defaultButtonChange
            self.colour = self.defaultColour
            self.backColour = self.defaultBackColour
            self.parent = parent
            self.fullSize = fullSize
            self.displaySize = displaySize
            self.pos = pos
            self.horizontal = horizontal
            assert self.fullSize > self.displaySize, "For there to be a scroll bar, the " + \
                   "displaying size must be less than the full size"

            self.barLength = displaySize ** 2 / fullSize
            self.originalPosition = 0
            self.position = 0
            self.beingDraggedFrom = None
            self.__setBarRect()
            if self.horizontal:
                x = displaySize
                y = self.width
            else:
                x = self.width
                y = displaySize
            self.fullRect = pygame.rect.Rect(self.pos, (x,y))

        def __setBarRect(self):
            if self.horizontal:
                size = (self.barLength, self.width)
                pos = (self.pos[0]+self.position, self.pos[1])
            else:
                size = (self.width, self.barLength)
                pos = (self.pos[0], self.pos[1]+self.position)
            self.barRect = pygame.rect.Rect(pos, size)

        def __movedTo(self, pos):
            if self.horizontal:
                self.position = self.originalPosition + (pos[0] - self.beingDraggedFrom[0])
            else:
                self.position = self.originalPosition + (pos[1] - self.beingDraggedFrom[1])
            # Keep it inside the bounds of the bar
            self.position = min(max(self.position, 0), self.displaySize - self.barLength)
            newScrollingPos = self.position * self.fullSize / self.displaySize
            newScrollingPos = min(newScrollingPos, self.fullSize - self.displaySize)
            if self.horizontal:
                self.parent.setHorizontalPos(newScrollingPos)
            else:
                self.parent.setVerticalPos(newScrollingPos)
            self.__setBarRect()
            

        def processEvent(self, event):
            if event.type == pygame.locals.MOUSEBUTTONDOWN and \
               event.button == 1 and self.barRect.collidepoint(event.pos) and \
               self.beingDraggedFrom == None:
                self.beingDraggedFrom = event.pos
                return None
            elif event.type == pygame.locals.MOUSEMOTION and self.beingDraggedFrom != None:
                self.__movedTo(event.pos)
                return None
            elif event.type == pygame.locals.MOUSEBUTTONUP and event.button == 1 and self.beingDraggedFrom != None:
                self.beingDraggedFrom = None
                self.originalPosition = self.position
                return None
            return event

        def draw(self, screen):
            pygame.draw.rect(screen, self.backColour, self.fullRect, 0)
            pygame.draw.rect(screen, self.colour, self.barRect, 0)
            

        
    def __init__(self, app, pos, size, displaySize):
        super(ScrollableCanvas, self).__init__(app)

        self.horizontalScrollBar = None
        self.verticalScrollBar = None

        self.pos = pos
        self.size = size
        self.displaySize = displaySize
        self.surface = pygame.surface.Surface(self.size)
        hasHorizontalScrollBar = self.size[0] > self.displaySize[0]
        if hasHorizontalScrollBar:
            hasVerticalScrollBar = self.size[1] > self.displaySize[1] - self.ScrollBar.defaultWidth
        else:
            hasVerticalScrollBar = self.size[1] > self.displaySize[1]
        if hasVerticalScrollBar and not hasHorizontalScrollBar:
            # re-calculate now that we know we have a vertical scroll bar
            hasHorizontalScrollBar = self.size[0] > self.displaySize[0] - self.ScrollBar.defaultWidth
        self.drawableHeight = self.displaySize[1]
        if hasHorizontalScrollBar:
            self.drawableHeight -= self.ScrollBar.defaultWidth
            horPos = (self.pos[0], self.pos[1] + self.displaySize[1] - self.ScrollBar.defaultWidth)
        self.drawableWidth = self.displaySize[0]
        if hasVerticalScrollBar:
            self.drawableWidth -= self.ScrollBar.defaultWidth
            verPos = (self.pos[0] + self.displaySize[0] - self.ScrollBar.defaultWidth, self.pos[1])

        if hasHorizontalScrollBar:
            self.horizontalScrollBar = self.ScrollBar(app, self, self.size[0], self.drawableWidth, horPos, True)
        if hasVerticalScrollBar:
            self.verticalScrollBar = self.ScrollBar(app, self, self.size[1], self.drawableHeight, verPos, False)
    
        ## internalPos is the position on the full canvas that we are drawing from
        self.internalPos = (0,0)
        self.__setDrawingRect()
        assert self.drawingRect.width <= self.size[0], "Full canvas size too large"
        assert self.drawingRect.height <= self.size[1], "Full canvas size too large"

    def __setDrawingRect(self):
        self.drawingRect = pygame.rect.Rect(self.internalPos, (self.drawableWidth, self.drawableHeight))

    def setVerticalPos(self, verticalPos):
        self.internalPos = (self.internalPos[0], verticalPos)
        self.__setDrawingRect()
        
    def setHorizontalPos(self, horizontalPos):
        self.internalPos = (horizontalPos, self.internalPos[1])
        self.__setDrawingRect()
        
        
    def draw(self, screen):
        super(ScrollableCanvas, self).draw(self.surface)
        if self.horizontalScrollBar:
            self.horizontalScrollBar.draw(screen)
        if self.verticalScrollBar:
            self.verticalScrollBar.draw(screen)
        subSurface = self.surface.subsurface(self.drawingRect)
        screen.blit(subSurface, self.pos)

       
    def processEvent(self, event):
        if self.horizontalScrollBar:
            event = self.horizontalScrollBar.processEvent(event)
        if self.verticalScrollBar and event:
            event = self.verticalScrollBar.processEvent(event)
        if event:
            if hasattr(event, 'pos'):
                event2 = translateEvent(event, tuple([self.pos[i] - self.internalPos[i] for i in 0,1]))
                isPos = True
            else:
                event2 = event
                isPos = False
            event2 = super(ScrollableCanvas, self).processEvent(event2)
            if event2 == None:
                return None
            else:
                return event        
        
