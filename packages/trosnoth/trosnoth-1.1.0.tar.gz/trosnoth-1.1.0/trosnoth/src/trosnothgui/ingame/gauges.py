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

from trosnoth.src.gui.framework import framework
import pygame
from trosnoth.src.trosnothgui.ingame import colours
            
class GaugeBase(framework.Element):
    '''Represents a graphical gauge to show the overheatedness of a turret'''
    def __init__(self, app, area):
        super(GaugeBase, self).__init__(app)
        self.area = area

    def draw(self, surface):
        rect = self.area.getRect(self.app)
        pos = rect.topleft
        amount = int(self.getRatio() * rect.width)

        backColour = self.getBackColour()
        if backColour != None:
            backRect = pygame.rect.Rect(pos[0]+amount, pos[1],
                                        rect.width - amount + 1, rect.height)
            surface.fill(backColour, backRect)
            
        if amount > 0:
            insideRect = pygame.rect.Rect(pos, (amount, rect.height))
            surface.fill(self.getForeColour(), insideRect)

        # Draw the border on top
        pygame.draw.rect(surface, colours.gaugeBorder, rect, 2)            


    # Return a number as a proportion (0..1) of how complete
    # this box is. To be implemented in subclasses
    def getRatio(self):
        raise NotImplementedException

    # Return the foreground colour that this gauge should be.
    # To be implemented in subclasses
    def getForeColour(self):
        raise NotImplementedException

    # Return the background colour that this gauge should be.
    # None = blank
    # To be implemented in subclasses
    def getBackColour(self):
        return None


class RespawnGauge(GaugeBase):
    '''Represents a graphical gauge to show how close to respawning a player
    is.'''
    def __init__(self, app, area, player):
        super(RespawnGauge, self).__init__(app, area)
        self.player = player

    def getRatio(self):
        return min(self.player.respawnGauge / self.player.respawnTotal, 1)

    def getForeColour(self):
        return colours.gaugeRespawnFore

    def getBackColour(self):
        if self.getRatio() <= 0:
            return colours.gaugeRespawnReady
        else:
            return colours.gaugeRespawnBack

        
class TurretGauge(GaugeBase):
    '''Represents a graphical gauge to show the overheatedness of a turret'''
    def __init__(self, app, area, player):
        self.player = player
        super(TurretGauge, self).__init__(app, area)

    def getRatio(self):
        return min(1, self.player.turretHeat / self.player.turretHeatCapacity)

    def getForeColour(self):
        if self.player.turretOverHeated:
            return colours.gaugeTurretHeated
        elif self.getRatio() > 0.5:
            return colours.gaugeTurretWarn
        else:
            return colours.gaugeTurretFine

class UpgradeGauge(GaugeBase):
    '''Represents a graphical gauge to show how much time a player has left
    to use their upgrade.'''
    def __init__(self, app, area, player):
        super(UpgradeGauge, self).__init__(app, area)
        self.player = player

    def getRatio(self):
        return min(self.player.upgradeGauge / self.player.upgradeTotal, 1)

    def getForeColour(self):
        return colours.gaugeUpgradeFore

    def getBackColour(self):
        return colours.gaugeUpgradeBack
