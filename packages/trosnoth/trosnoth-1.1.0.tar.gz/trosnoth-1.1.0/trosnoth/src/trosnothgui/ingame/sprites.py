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
from trosnoth.src.gui.framework.basics import SingleImage, AngledImageCollection, Animation
from trosnoth.src.gui.framework.utils import makeImages, makeImage
from trosnoth.src.trosnothgui import defines

from trosnoth.src.model.obstacles import JumpableObstacle, VerticalWall, GroundObstacle
import random


class ShotSprite(pygame.sprite.Sprite):
    def __init__(self, shot):
        super(ShotSprite, self).__init__()
        self.shot = shot
        self.image = shot.team.shotImage
        self.rect = self.image.get_rect()

    @property
    def pos(self):
        return self.shot.pos

class GrenadeSprite(pygame.sprite.Sprite):
    def __init__(self, grenade):
        super(GrenadeSprite, self).__init__()
        self.grenade = grenade
        self.image = makeImage('grenade.bmp')
        self.rect = self.image.get_rect()
        
    @property
    def pos(self):
        return self.grenade.pos

class PlayerSprite(pygame.sprite.Sprite):
    # These parameters are used to create a canvas for the player sprite object.
    canvasSize = (33, 39)
    colourKey = (255, 255, 255)
    def __init__(self, player):
        super(PlayerSprite, self).__init__()
        self.player = player
        self.nametag = player.nametag

        # TODO: it'd be neater to make a single instance of all of these, for
        #       each animation instance to use
        gunImages = makeImages(['Head-4.png', 'Head-3.png', 'Head-2.png',
                           'Head-1.png', 'Head-0.png', 'Head-17.png',
                           'Head-16.png','Head-15.png', 'Head-14.png'])
        bodyImage = makeImage('Body-1.png')
        holdImage = makeImage('Hold-1.png')
        headImage = makeImage('headOutline.png')
        turretBaseImage = makeImage('TurretBase.png')
        
        ghostAnimation = makeImages(['ghost.png', 'ghost2.png', 'ghost3.png', 'ghost4.png', 'ghost3.png', 'ghost2.png'])
        ghostAnimationFaux = makeImages(['ghost.bmp', 'ghost2.bmp', 'ghost3.bmp', 'ghost4.bmp', 'ghost3.bmp', 'ghost2.bmp'])
        
        runningLegs = makeImages(['Legs-R1.png', 'Legs-R2.png',
                                      'Legs-R3.png', 'Legs-R4.png'])
        
        legsBackwards = makeImages(['Legs-W1-3.png', 'Legs-W1-2.png',
                                   'Legs-W1-1.png', 'Legs-W1.png'])
        shieldAnimation = makeImages(['shieldImage1.png', 'shieldImage2.png',
                                      'shieldImage3.png', 'shieldImage4.png'])
        phaseShiftAnimation = makeImages(['phaseShift1.png', 'phaseShift2.png', 'phaseShift3.png', 'phaseShift4.png'])
        
        standingImage = makeImage('Legs-S0.png')
        jumpingImage = makeImage('Legs-R3.png')
        # Create an image for myself.
        gunImages = AngledImageCollection(self, *gunImages)
        turretBaseImage = SingleImage(turretBaseImage)

        bodyImage = SingleImage(bodyImage)

        holdImage = SingleImage(holdImage)
        headImage = SingleImage(headImage)
        teamImage = SingleImage(self.player.team.image)

        if defines.useAlpha:
            self.ghostAnimation = [Animation(0.25, *ghostAnimation)]
        else:
            self.ghostAnimation = [Animation(0.25, *ghostAnimationFaux)]
        
        self.runningAnimation = [Animation(0.1, *runningLegs),
                                 headImage, bodyImage, gunImages,
                                 teamImage]
        
        self.reversingAnimation = [gunImages, bodyImage, headImage,
                                   Animation(0.2, *legsBackwards),
                                 teamImage]
        self.turretAnimation = [turretBaseImage, bodyImage, headImage,
                                teamImage, gunImages]
        self.standingAnimation = [SingleImage(standingImage),
                                  bodyImage, gunImages, headImage,
                                 teamImage]
        self.jumpingAnimation = [headImage, SingleImage(jumpingImage),
                                 gunImages, bodyImage,
                                 teamImage]
        self.holdingAnimation = [headImage, bodyImage, holdImage,
                                 teamImage]
        self.fallingAnimation = self.jumpingAnimation
        self.shieldAnimation = Animation(0.15, *shieldAnimation)
        self.phaseShiftAnimation = Animation(0.15, *phaseShiftAnimation)

        self.image = pygame.Surface(self.canvasSize)
        self.image.set_colorkey(self.colourKey)
        self.rect = self.image.get_rect()

    @property
    def pos(self):
        return self.player.pos

    @property
    def angleFacing(self):
        return self.player.angleFacing
    
    # This is hopefully a temporary fix to facilitate
    # the problem we have with angleFacing being given
    # values outside of the range -pi < x <= pi.as_integer_ratio
    # You can tell when this happens because it should print
    # "AIC: Weird angleFacing...". Would be better to fix it at the root.
    def setAngleFacing(self, value):
        self.player.setAngleFacing(value)

    # TODO: this is a bit hacky. Do those things accessing self.player actually need them?
    def __getattr__(self, attr):
        return getattr(self.player, attr)

    def update(self):
        self.setImage(self._isMoving(), self._isSlow())

    def _isMoving(self):
        return not (self.player._state['left'] or self.player._state['right'])

    def _isSlow(self):
        # Consider horizontal movement of player.
        if self.player._state['left'] and not self.player._state['right']:
            if self.player._faceRight:
                return True
            else:
                return False
        elif self.player._state['right'] and not self.player._state['left']:
            if self.player._faceRight:
                return False
            else:
                return True
        return False


    def setImage(self, moving, slow):
        flip = None
        if self.player.ghost:
            blitImages = self.ghostAnimation
        elif self.player.turret:
            blitImages = self.turretAnimation
        elif self.player._onGround:
            if isinstance(self.player._onGround, VerticalWall):
                blitImages = self.holdingAnimation
                if self.player._onGround.deltaPt[1] < 0:
                    flip = False
                else:
                    flip = True
                
            elif not moving == 0:
                blitImages = self.standingAnimation
            elif slow:
                blitImages = self.reversingAnimation
            else:
                blitImages = self.runningAnimation
        else:
            if self.player.yVel > 0:
                blitImages = self.fallingAnimation
            else:
                blitImages = self.jumpingAnimation
        self.image.fill(self.image.get_colorkey())
        # Put the pieces together:
        for element in blitImages:
            self.image.blit(element.getImage(), (0,0))
        if self.player.shielded:
            self.image.blit(self.shieldAnimation.getImage(), (0,0))
        if self.player.phaseshift and not defines.useAlpha:
            self.image.blit(self.phaseShiftAnimation.getImage(), (0,0))
        if not self.player._faceRight and flip == None or flip:
            self.image = pygame.transform.flip(self.image, True, False)
        # Flicker the sprite between different levels of transparency
        if defines.useAlpha:
            if self.player.local and self.player.phaseshift:
                self.image.set_alpha(random.randint(30, 150))
            elif self.player.ghost:
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)
                    