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

'''Displays the state of a transaction'''

from trosnoth.src.gui.framework import framework
from trosnoth.src.upgrades import upgradeNames
import trosnoth.src.transaction as transactionModule
from trosnoth.src.gui.common import addPositions

import pygame

class TransactionGUI(framework.Element):
    '''Shows current Transaction information on screen'''
    buffer = 20
    def __init__(self, app, pos, transaction, player, bigFont = None, midFont = None, smallFont = None, bgColour = (0,0,255), foreColour = (255,255,255)):
        super(TransactionGUI, self).__init__(app)
        self.player = player
        self.pos = pos
        self.transaction = transaction
        self.starsRqd = transaction.requiredStars

        if bigFont:
            self.bigFont = bigFont
        else:
            self.bigFont = app.screenManager.fonts.bigTransactionFont

        if midFont:
            self.midFont = midFont
        else:
            self.midFont = self.app.screenManager.fonts.midTransactionFont
            
        if smallFont:
            self.smallFont = smallFont
        else:
            self.smallFont = app.screenManager.fonts.smallTransactionFont        
                   
        self.bgColour = bgColour
        self.foreColour = foreColour
        self.borderColour = (0,0,0)
        self._purchasingText = '%s purchasing %s' % (self.transaction.purchasingPlayer.nick, upgradeNames[self.transaction.upgrade])


##        self.transaction.onNumStarsChanged.addListener(transactionChanged)
##        self.transaction.onStateChanged.addListener(stateChanged)

    # Find the largest size that this box should become
    # This function assumes that all numbers are the same width
    # in the given font. Could be improved.
    def _getNeededSize(self):
        fontSize1 = self.bigFont.size(self.app, "00 of %d" % (self.starsRqd))
        fontSize2 = self.midFont.size(self.app, self._purchasingText)
        fontSize3 = self.smallFont.size(self.app, "You have contributed 10 stars")
        width = max(fontSize1[0], fontSize2[0], fontSize3[0]) + self.buffer
        height = fontSize1[1] + fontSize2[1] + fontSize3[1] + self.buffer
        
        return (width, height)

    def _getRect(self):
        rect = pygame.Rect((0,0), self._getNeededSize())
        if hasattr(self.pos, 'apply'):
            self.pos.apply(self.app, rect)
            return rect
        else:
            rect.topleft = self.pos

    def _getPt(self):
        return self._getRect().topleft

    def draw(self, surface):
        rect = self._getRect()
        surface.fill(self.bgColour, rect)
        pygame.draw.rect(surface, self.borderColour, rect, 2)
        if self.transaction.state == transactionModule.TransactionState.Open:
            self._drawUncompleted(surface)
        else:
            self._drawCompleted(surface)

    def _drawUncompleted(self, surface):
            rect = self._getRect()
            pos = rect.topleft
            purchasingImage = self.midFont.render(self.app, self._purchasingText, True, self.foreColour, self.bgColour)
                        
            # Number of stars donated
            numDonated = "%d of %d" % (self.transaction.totalStars, self.starsRqd)
            numImage = self.bigFont.render(self.app, numDonated, True, self.foreColour, self.bgColour)

            # Number that the focused player has contributed
            contributedText = "You have contributed %d stars" % \
                              (self.transaction.getNumStars(self.player))
            conTextImage = self.smallFont.render(self.app, contributedText, True, self.foreColour, self.bgColour)

            self._drawTexts(surface, [purchasingImage, numImage, conTextImage])

    def _drawTexts(self, surface, textImages):
        rect = self._getRect()
        between = self.buffer / (len(textImages) + 1)
        rem = self.buffer % (len(textImages) + 1)
        lastPos = addPositions(rect.midtop, (0, between + rem))
        for image in textImages:
            textRect = image.get_rect()
            textRect.midtop = lastPos
            surface.blit(image, textRect.topleft)
            lastPos = addPositions(textRect.midbottom, (0, between))
            
    
    def _drawCompleted(self, surface):
        
        reason = transactionModule.TransactionStateText[self.transaction.state]
        images = [self.bigFont.render(self.app, "Transaction", True, self.foreColour, self.bgColour),
                  self.bigFont.render(self.app, reason, True, self.foreColour, self.bgColour)]
        self._drawTexts(surface, images)