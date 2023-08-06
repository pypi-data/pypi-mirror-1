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

'''
Provides a layer between a universe and the GUI, turning
players, shots, grenades into sprites, and drawing mapblocks.
'''

import pygame
from trosnoth.src.trosnothgui.ingame.sprites import PlayerSprite, ShotSprite, GrenadeSprite

class UniverseGUI(object):
    def __init__(self, universe):
        self.universe = universe
        # Sprites
        self.players = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()
        self.grenades = pygame.sprite.Group()

        # Indirection helpers - could be done better
        self.zoneBlocks = self.universe.zoneBlocks
        self.zones = self.universe.zones
        self.map = self.universe.map

        # TODO: remove this hack - have it go through the normal interface channels.
        self.universe.onShotKill.addListener(self.removeShot)
        self.universe.onGrenadeKill.addListener(self.removeGrenade)
        self.universe.onGrenadeExists.addListener(self.addGrenade)
        
    def getPlayerSprite(self, player):
        for playersprite in self.players:
            if playersprite.player == player:
                return playersprite
            

    def addPlayer(self, player):
        self.players.add(PlayerSprite(player))

    def removePlayer(self, player):
        for playersprite in self.players:
            if playersprite.player == player:
                self.players.remove(playersprite)
                return

    def addShot(self, shot):
        self.shots.add(ShotSprite(shot))

    def removeShot(self, shot):
        for shotsprite in self.shots:
            if shotsprite.shot == shot:
                self.shots.remove(shotsprite)
                return


    def addGrenade(self, grenade):
        self.grenades.add(GrenadeSprite(grenade))

    def removeGrenade(self, grenade):
        for grenadesprite in self.grenades:
            if grenadesprite.grenade == grenade:
                self.grenades.remove(grenadesprite)
                return

            

    def tick(self, deltaT):
        self.universe.tick(deltaT)
        
        self.players.update()
        self.shots.update()
        self.grenades.update()