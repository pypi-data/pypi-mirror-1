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

'''upgrades.py - defines the behaviour of upgrades. Used by both the
client and the server.

At the moment the only advantage to having server and client using the
same upgrade class is that you only have to edit in one place to edit
an upgrade, but the goal in future is to have the client and server
performing essentially the same set of calculations as one another.'''

from twisted.internet import reactor

from trosnoth.src.base import MenuError

class Upgrade(object):
    '''Represents an upgrade that can be bought. Used by client and server.'''

    # Upgrades have an upgradeType: this must be a unique, single-character
    # value.
    def __init__(self, player):
        '''At present player may be universe.Player or serverUniverse.Player
        depending on whether this is client or server.'''
        self.inUse = False
        self.player = player

    def __repr__(self):
        return upgradeNames[type(self)]
    
    def clientUse(self):
        '''Initiate the upgrade (client-side)'''
        raise NotImplementedError, 'Upgrade.clientUse() not implemented.'

    def requestUse(self):
        '(client-side)'
        raise NotImplementedError, 'Upgrade.requestUse() not implemented.'
    
    def clientDelete(self):
        '''Performs any necessary tasks to remove this upgrade from the game.'''
        self.inUse = False
        self.player.upgrade = None
        self.player.universe.netClient.interface.upgradeDestroyed(self.player)

    def serverUse(self):
        '''Initiate the upgrade (server-side). Return True if successful.'''
        self.inUse = True

    def serverDelete(self):
        '''Performs any necessary tasks to remove this upgrade from the game.'''
        self.player.universe.netServer.sendDeleteUpgrade(self.player.id)
        self.player.upgrade = None
        self.inUse = False

    def timeOver(self):
        '(server-side)'
        if self.inUse:
            self.serverDelete()

class Shield(Upgrade):
    '''Represents a shield; a purchasable upgrade that protects a player from
    one shot'''
    upgradeType = 's'
    requiredStars = 4
    timeRemaining = 30
    def __init__(self, player):
        super(Shield, self).__init__(player)
        self.active = False     # Server-side
        
    def requestUse(self):
        '''Request initiation of the upgrade'''
        self.player.universe.netClient.useUpgrade(self.player)

    def clientUse(self):
        '''Initiate the upgrade'''
        self.inUse = True
        self.player.shielded = True
            
    def clientDelete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        super(Shield, self).clientDelete()
        self.player.shielded = False

    def serverUse(self):
        '''Initiate the upgrade'''
        reactor.callLater(self.timeRemaining, self.timeOver)
        self.inUse = True
        self.player.shielded = True
        print "%s using Shield" % self.player.nick
        return True
            
    def serverDelete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        super(Shield, self).serverDelete()
        self.player.shielded = False

class PhaseShift(Upgrade):
    '''Represents a phase shift, a purchasable upgrade that means a player cannot
    be shot, but cannot shoot; lasts for a limited time only.'''
    upgradeType = 'h'
    requiredStars = 6
    timeRemaining = 25
    def __init__(self, player):
        super(PhaseShift, self).__init__(player)
        self.active = False   # Server-side.
        
        
    def requestUse(self):
        '''Request initiation of the upgrade'''
        self.player.universe.netClient.useUpgrade(self.player)

    def clientUse(self):
        '''Initiate the upgrade'''
        self.inUse = True
        self.player.phaseshift = True
            
    def clientDelete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        super(PhaseShift, self).clientDelete()
        self.player.phaseshift = False

    def serverUse(self):
        '''Initiate the upgrade'''
        reactor.callLater(self.timeRemaining, self.timeOver)
        self.inUse = True
        self.player.phaseshift = True
        print "%s using Phase Shift" % self.player.nick
        return True
            
    def serverDelete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        super(PhaseShift, self).serverDelete()
        self.player.phaseshift = False

class Turret(Upgrade):
    '''Represents a turret; a purchasable upgrade that turns a player into
    a turret; a more powerful player, although one who is unable to move.'''
    upgradeType = 't'
    requiredStars = 8
    timeRemaining = 50
    
    def requestUse(self):
        '''Request initiation of the upgrade'''
        if self.player.currentZone.zoneOwner == self.player.team:
            if not self.player.currentZone.turretedPlayer:

                distanceFromEdge = 100
                distanceFromOrb = 100
                edge = self.player.currentMapBlock.fromEdge(self.player)
                if edge >= distanceFromEdge:
                    zone = self.player.currentZone
                    distance = ((zone.defn.pos[0] - self.player.pos[0]) ** 2 + \
                               (zone.defn.pos[1] - self.player.pos[1]) ** 2) ** 0.5
                    if distance >= distanceFromOrb:
                    
                        self.player.universe.netClient.useUpgrade(self.player)
                    else:
                        raise MenuError, "Too close to orb to place turret"
                else:
                    raise MenuError, "Too close to edge of zone to place turret"
            else:
                raise MenuError, "Cannot have two turreted players in a single zone"
        else:
            raise MenuError, "Must own the orb and the zone to become a turret"

    def clientUse(self):
        '''Initiate the upgrade'''
        self.inUse = True
        self.player.turret = True
        self.player._onGround = None
        self.player.currentZone.turretedPlayer = self.player
        self.player.universe.netClient.interface.turretStarted(self.player)

        # Arrest vertical movement so that upon losing the upgrade, the
        # player doesn't re-jump
        self.player.yVel = 0
        
    def clientDelete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        if self.inUse:
            self.player.turret = False
            self.player.turretOverHeated = False
            self.player.turretHeat = 0.0
            self.player.currentZone.turretedPlayer = None
            self.player.universe.netClient.interface.turretEnded(self.player)
        super(Turret, self).clientDelete()


    def serverUse(self):
        '''Attempts to initiate the upgrade, returning True if all is well.'''
        if self.player.currentZone.zoneOwner == self.player.team:
            if not self.player.currentZone.turretedPlayer:                        
                self.inUse = True
                self.player.turret = True
                self.player.currentZone.turretedPlayer = self.player
                    
                reactor.callLater(self.timeRemaining, self.timeOver)
                print "%s using Turret" % self.player.nick
                return True
            else:
                # Cannot have two turreted players in a single zone
                self.player.universe.netServer.validateUpgrades(player = \
                                                                self.player)
                return False

        else:
            # Must own the orb and the zone to become a turret
            self.player.universe.netServer.validateZones(player = self.player)
            return False

    def serverDelete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        if self.inUse:
            self.player.turret = False
            self.player.turretOverHeated = False
            self.player.turretHeat = 0.0
            self.player.currentZone.turretedPlayer = None
        super(Turret, self).serverDelete()

class MinimapDisruption(Upgrade):
    upgradeType = 'm'
    requiredStars = 15
    timeRemaining = 40
    
    def requestUse(self):
        '''Request initiation of the upgrade'''
        self.player.universe.netClient.useUpgrade(self.player)

    def clientUse(self):
        '''Initiate the upgrade'''
        self.inUse = True
        self.player.universe.netClient.interface.gameInterface.minimapDisruption(self.player)

        
    def clientDelete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        self.player.universe.netClient.interface.gameInterface.endMinimapDisruption()
        super(MinimapDisruption, self).clientDelete()

    def serverUse(self):
        '''Initiate the upgrade'''
        reactor.callLater(self.timeRemaining, self.timeOver)
        self.inUse = True
        print "%s using Minimap Disruption on the enemy" % self.player.nick
        return True

    def serverDelete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        super(MinimapDisruption, self).serverDelete()


class Grenade(Upgrade):
    '''represents a grenade that after landing will shoot shots out in all
    directions; after 5 seconds, killing any players hit.'''
    upgradeType = 'g'
    requiredStars = 5
    timeRemaining = 2.5
    numShots = 40
    
    def __init__(self, player):
        self.gr = None                          # Client-side.
        super(Grenade, self).__init__(player)

    def requestUse(self):
        '''Request initiation of the upgrade.'''
        self.player.universe.netClient.useUpgrade(self.player)

    def clientUse(self):
        '''Initiate the upgrade.'''
        self.inUse = True

        if self.gr is not None:
            print '** Stray grenade'
            self.gr.delete()

        # FIXME: This is clumsy, but I'd rather not import universe into the top-level
        # namespace of a module like this that is used by the server.
        from trosnoth.src.universe import GrenadeShot
        self.gr = GrenadeShot(self.player.universe, self.player, 'X')

        reactor.callLater(self.timeRemaining, self.clientTimeOver)

    def clientTimeOver(self):
        if self.player.local:
            self.explode()

    def explode(self):
        self.player.universe.netClient.sendGrenadeExploded(self)

        # Delete the grenade
        if self.gr is not None:
            self.gr.delete()  

    def clientDelete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        if self.gr is not None:
            self.gr.delete()
        super(Grenade, self).clientDelete()

    def serverUse(self):
         '''Initiate the Upgrade'''
         reactor.callLater(self.timeRemaining, self.timeOver)
         self.inUse = True
         print "%s using Grenade" % self.player.nick
         return True

    def timeOver(self):
        print '**** Server: Grenade Time is over'
        super(Grenade, self).timeOver()

    def serverDelete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        super(Grenade, self).serverDelete()


upgradeOfType = {Shield.upgradeType : Shield,
                 PhaseShift.upgradeType: PhaseShift,
                 Turret.upgradeType : Turret,
                 MinimapDisruption.upgradeType : MinimapDisruption,
                 Grenade.upgradeType : Grenade}

upgradeNames = {Shield : "Shield",
               PhaseShift : "Phase Shift",
               Turret : "Turret",
               MinimapDisruption : "Minimap Disruption",
               Grenade : "Grenade"}
