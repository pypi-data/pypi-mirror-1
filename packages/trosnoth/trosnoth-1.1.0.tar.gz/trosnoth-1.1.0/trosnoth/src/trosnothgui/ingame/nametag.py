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
from trosnoth.src.gui.framework.utils import makeImage

class NameTag(pygame.sprite.Sprite):
    '''Sprite object that every player has which indicates the player's nick.'''
    def __init__(self, nick):
        pygame.sprite.Sprite.__init__(self)

        if len(nick) > 15:
            nick = nick[:13] + '...'
        self.nick = nick
        self.image = self.nameFont.render(self.nick, True, (0,64,0))
        foreground = self.nameFont.render(self.nick, True, (64,128,64))
        self.image.blit(foreground, (-2, -2))

        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()

class StarTally(pygame.sprite.Sprite):
    def __init__(self, stars):
        pygame.sprite.Sprite.__init__(self)
        self.stars = 0
        self.image = None
        self.rect = None

        self.setStars(stars)

    def setStars(self, stars):
        global _smallStarPic
        try:
            pic = _smallStarPic
        except NameError:
            pic = _smallStarPic = makeImage('smallstar.png')

        if stars <= 5:
            self.image = pygame.Surface((12*stars+2, 13))
            # Blit the stars.
            for i in xrange(stars):
                self.image.blit(pic, (i*12, 0))

            self.rect = self.image.get_rect()
        else:
            self.image = pygame.Surface((62, 26))
            # Blit the stars.
            for i in xrange(5):
                self.image.blit(pic, (i*12-1, 0))
            for i in xrange(stars-5):
                self.image.blit(pic, (i*12-1, 13))

            self.rect = self.image.get_rect()
        self.image.set_colorkey((0, 0, 0))
    