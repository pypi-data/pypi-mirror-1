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

from math import sin, cos
import struct
import random

import trosnoth

# TODO: Get GUI code out of model
from trosnoth.src.trosnothgui.ingame.nametag import NameTag, StarTally
#####

from trosnoth.src.model.unit import Unit
from trosnoth.src.model.obstacles import JumpableObstacle, VerticalWall, GroundObstacle
from trosnoth.src.model.map import MapLayout


class Player(Unit):
    '''Maintains the state of a player. This could be the user's player, a
    player on the network, or conceivably even a bot.

    If this player is controlled locally (human or bot), then player.local
    is True. If the player is controlled by the network, player.local is False.
    '''

    def __init__(self, universe, nick, team, id, zone, dead = False):
        '''Note that player instances are not local when they are created.
        The value of local is set only when the server gives us the player
        by calling self.makeLocal().'''
        Unit.__init__(self)
        
        self.universe = universe
        self.nick = nick
        self.team = team
        self.id = id
        self.local = False
        self._state = {'left':  False,
                       'right': False,
                       'jump':  False,
                       'down': False,
                       'respawn' : False}

        # If we're in test mode, start with lots of stars.
        try:
            trosnoth._testmode
            self.stars = 20
        except AttributeError:
            self.stars = 0
        
        # Place myself.
        self.pos = zone.defn.pos
        self._jumpTime = 0.0
        self.yVel = 0
        self._onGround = None
        self._ignore = None                 # Used when dropping through a platform.
        self.angleFacing = 1.57
        self.ghostThrust = 1.0              # Determined by mouse position
        self._faceRight = True
        self.reloadTime = 0.0
        self.turretHeat = 0.0
        self.respawnGauge = 0.0
        self.upgradeGauge = 0.0
        self.upgradeTotal = 0.0
        self.ghost = dead
        self.upgrade = None
        self.shielded = False
        self.hasRicochet = False
        self.phaseshift = False
        self.turret = False
        self.turretOverHeated = False
        self.shots = {}

        # Create a nametag.
        self.nametag = NameTag(self.nick)
        self.starTally = StarTally(0)
        
        self.currentZone = zone
        zone.addPlayer(self)

    def setAngleFacing(self, value):
        self.angleFacing = value

    def setPos(self, pos):
        self.pos = pos
        # Ensure we're in the right mapBlock
        i, j = MapLayout.getMapBlockIndices(*pos)
        self.currentMapBlock = self.universe.zoneBlocks[i][j]

        # TODO: try to put ourselves on solid ground.

    def __repr__(self):
        return self.nick

    def getDetails(self):

        pID = struct.unpack('B', self.id)[0]
        nick = self.nick
        team = self.team.id
        dead = self.ghost
        stars = self.stars
        if self.upgrade:
            upgrade = repr(self.upgrade)
        else:
            upgrade = None
        
        return {'pID': pID,
                'nick': nick,
                'team': team,
                'dead': dead,
                'stars': stars,
                'upgrade': upgrade}

    def removeFromGame(self):
        '''Called by network client when server says this player has left the
        game.'''
        # Remove myself from the register of players.
        if self.team.currentTransaction and self.team.currentTransaction.getNumStars(self) > 0:
            self.team.currentTransaction.removeStars(self)
        if self.upgrade:
            self.upgrade.clientDelete()
        self.universe.delPlayer(self)
        
        # Remove myself from all groups I'm in.
        self.currentMapBlock.removePlayer(self)
        self.currentZone.removePlayer(self)
        
        

    def makeLocal(self):
        'Called by network client at instruction of server.'
        self.local = True
        
    def solid(self):
        return not self.ghost
    
    def setMapBlock(self, block):
        self.currentMapBlock.removePlayer(self)
        Unit.setMapBlock(self, block)
        block.addPlayer(self)
            
        # If we're changing blocks, we can't hold on to the same obstacle,
        # as obstacles belong to a particular mapblock.
        self._onGround = None
    
    def updateState(self, key, value):
        '''Update the state of this player. State information is information
        which is needed to calculate the motion of the player. For a 
        human-controlled player, this is essentially only which keys are
        pressed. Keys which define a player's state are: left, right, jump and
        down.
        Shooting is processed separately.'''
        
        # Ignore messages if we already know the answer.
        if self._state[key] == value:
            return
        if not self.ghost:
            # If a jump is requested and we're not on the ground, ignore it.
            if key == 'jump':
                if value:
                    if not self._onGround or not isinstance(self._onGround, \
                                                            JumpableObstacle):
                        return
                        
                    # Otherwise, initiate the jump.
                    self._jumpTime = self.maxJumpTime
                    self._onGround = None
                elif self._jumpTime > 0:
                    # If we're jumping, cancel the jump.
                    # The following line ensures that small jumps are possible
                    #  while large jumps still curve.
                    self.yVel = -(1 - self._jumpTime / self.maxJumpTime) * \
                                self.jumpThrust
                    self._jumpTime = 0
        
        # Set the state.
        self._state[key] = value
        
        # If the state changes and the player is not local, tell network.
        if self.local:
            self.universe.onPlayerUpdate.execute(self)

    def lookAt(self, angle, thrust=None):
        '''Changes the direction that the player is looking.  angle is in
        radians and is measured clockwise from the right.'''
        if thrust is not None:
            self.ghostThrust = thrust
        
        if self.angleFacing == angle:
            return
        
        self.angleFacing = angle
        tempBool = self._faceRight
        self._faceRight = angle > 0
        if tempBool != self._faceRight and self.local:
            self.universe.onPlayerUpdate.execute(self)
            

    def fireShot(self):
        '''Fires a shot in the direction the player's currently looking.'''
        if not self.ghost and not self.phaseshift:
            # While on a vertical wall, one canst not fire
            if self.reloadTime <= 0 and (not self._onGround or not \
                                      isinstance(self._onGround, VerticalWall)):
                
                if self.turret:
                    if self.turretOverHeated:
                        return
                    self.reloadTime = self.turretReloadTime
                    self.turretHeat += self.shotHeat
                    if self.turretHeat > self.turretHeatCapacity:
                        self.turretOverHeated = True
                        
                elif self.currentZone.zoneOwner == self.team:
                    self.reloadTime = self.ownReloadTime
                    
                elif self.currentZone.zoneOwner == None:
                    self.reloadTime = self.neutralReloadTime
                    
                else:
                    self.reloadTime = self.enemyReloadTime
                self.universe.onShotFired.execute(self, self.__getShotType())

    def __getShotType(self):
        if self.turret:
            return 'T'
        if self.hasRicochet:
            return 'R'
        return 'N'
    
    def update(self, deltaT):
        '''Called by this player's universe when this player should update
        its position. deltaT is the time that's passed since its state was
        current, measured in seconds.'''

        # Update upgrade gauge based on Time:
        if self.upgrade:
            self.upgradeGauge -= deltaT
                
        #########
        # GHOST #
        #########
        if self.ghost:
            deltaX = self.maxGhostVel * deltaT * sin(self.angleFacing) * self.ghostThrust
            deltaY = -self.maxGhostVel * deltaT * cos(self.angleFacing) * self.ghostThrust

            self._move(deltaX, deltaY)

            # Update respawn gauge based on Time:
            if self.respawnGauge >= 0:
                self.respawnGauge -= deltaT

        ##########
        # TURRET #
        ##########
        elif self.turret:
                              
            # Now adjust the time till reloaded.
            self.reloadTime = max(0.0, self.reloadTime - deltaT)

            self.turretHeat = max(0.0, self.turretHeat - deltaT)
            if self.turretOverHeated and self.turretHeat == 0.0:
                self.turretOverHeated = False

                
        ##########
        # PLAYER #
        ##########
        else:
            
            # Consider horizontal movement of player.
            if self._state['left'] and not self._state['right']:
                if self._faceRight:
                    absVel = -self.slowXVel
                else:
                    absVel = -self.xVel
            elif self._state['right'] and not self._state['left']:
                if self._faceRight:
                    absVel = self.xVel
                else:
                    absVel = self.slowXVel
            else:
                absVel = 0
            
            # Allow falling through fall-through-able obstacles
            if self._onGround and self._onGround.drop and self._state['down']:
                
                # Put the player through the floor:
                if not isinstance(self._onGround, VerticalWall):
                    self._ignore = self._onGround
                self._onGround = None
                
            # Now consider vertical movement.
            if isinstance(self._onGround, GroundObstacle):
                # Ask the ground obstacle I'm on where I'm moving to.
                deltaX, deltaY = self._onGround.walkTrajectory(absVel, deltaT)
        
                # Check for collisions in this path.
                self._move(deltaX, deltaY)
            elif isinstance(self._onGround, VerticalWall):
                # Stuck to the wall. Allow falling off:
                if self._state['right'] and self._onGround.deltaPt[1] > 0 \
                   or (self._state['left'] and self._onGround.deltaPt[1] < 0):
                    self._onGround = None
                    self.fallTime = deltaT
            else:
                deltaY = 0
                deltaX = absVel * deltaT
                
                # If the player is jumping, calculate how much they jump by.
                if self._jumpTime > 0:
                    thrustTime = min(deltaT, self._jumpTime)
                    self.yVel = -self.jumpThrust
                    deltaY = thrustTime * self.yVel
                    self._jumpTime = self._jumpTime - deltaT
                    
                    # Automatically switch off the jumping state if the player
                    # has reached maximum time.
                    if self._jumpTime <= 0:
                        self.updateState('jump', False)
                        self._jumpTime = 0
                    fallTime = deltaT - thrustTime
                else:
                    fallTime = deltaT
                
                # If player is falling, calculate how far they fall.
                
                # v = u + at
                vFinal = self.yVel + self.gravity * fallTime
                if vFinal > self.maxFallVel:
                    # Hit terminal velocity. Fall has two sections.
                    deltaY = deltaY + (self.maxFallVel**2 - self.yVel**2) \
                             / (2 * self.gravity) + self.maxFallVel * (fallTime - \
                             (self.maxFallVel - self.yVel) / self.gravity)
                    self.yVel = self.maxFallVel
                else:
                    # Simple case: s=ut+0.5at**2
                    deltaY = deltaY + self.yVel * fallTime + 0.5 * self.gravity * \
                             fallTime ** 2
                    self.yVel = vFinal
            
                # Check for collisions in this path.
                self._move(deltaX, deltaY)
            
            # Now adjust the time till reloaded.
            self.reloadTime = max(0.0, self.reloadTime - deltaT)

    def movedBy(self, deltaX, deltaY):
        '''
        Called just after the player has moved by moveUnit().
        '''
        if self.ghost and self.respawnGauge > 0:
            distanceTravelled = ((deltaX ** 2) + (deltaY ** 2)) ** 0.5
            self.respawnGauge -= distanceTravelled / self.respawnMovementValue
            
    def _move(self, deltaX, deltaY):
        '''Called by the player's update() routine to move the player a given
        distance. This method should check for collisions with bullets and the
        ground.'''

        # For a ghost:
        if self.ghost:
                # TODO: Check for smaller resulting deltaX and deltaY due
                #  to hitting the edge of the map.
                self.currentMapBlock.moveUnit(self, deltaX, deltaY)

        # For a player:
        else:
            while True:
                # Check for collisions with solid objects, and change of zone.
                obstacle = self.currentMapBlock.moveUnit(self, deltaX, deltaY)
                if obstacle is not None:
                    # Ask obstacle where the player should end up.
                    targetPt = obstacle.finalPosition(self.pos, deltaX, deltaY)
                    
                    if targetPt == None:
                        break

                    deltaX = targetPt[0] - self.pos[0]
                    deltaY = targetPt[1] - self.pos[1]
                    
                else:
                    break
                
            # The following if statement will perform calculations for setting
            #  the current obstacle if any of the following conditions are met:
            # (1) Player is not currently on the ground.
            # (2) Player is currently on the ground and has hit another obstacle.
            # (3) Player was on the ground but has walked off the end.
            if not isinstance(self._onGround, GroundObstacle) or obstacle or \
                               not self._onGround.inBounds(self.pos):
                if isinstance(obstacle, JumpableObstacle):
                    if isinstance(self._onGround, GroundObstacle) and \
                       isinstance(obstacle, VerticalWall):
                        # Running into a vertical wall while on the ground.
                        # Don't attach self to it.
                        pass
                    else:
                        self._onGround = obstacle
                else:
                    self._onGround = None
                if obstacle:
                    # Hit an obstacle. Process change to velocity etc.
                    if obstacle:
                        obstacle.hitByPlayer(self)

            # Check for zone tag.
            if self.currentZone.orbOwner != self.team and self.local:
                self.universe.checkTag(self)

        self._ignore = None

    def changeZone(self, newZone):
        self.currentZone.removePlayer(self)
        newZone.addPlayer(self)
        self.currentZone = newZone

    def die(self):
        self.ghost = True
        self.respawnGauge = self.respawnTotal
        if self.stars > 0:
            if self.team.currentTransaction and \
               self.team.currentTransaction.contributions.has_key(self):
                self.team.currentTransaction.removeStars(self)
        self.universe.updateStars(self, 0)
        if self.upgrade:
            self.upgrade.clientDelete()

    def respawn(self):
        self._onGround = None
        self.ghost = False
        self.respawnGauge = 0
        self.pos = self.currentZone.defn.pos
        i, j = MapLayout.getMapBlockIndices(self.pos[0], self.pos[1])
        try:
            self.currentMapBlock = self.universe.zoneBlocks[i][j]
        except IndexError:
            raise IndexError, "You're off the map!"
        
    def updateNametag(self):
        self.starTally.setStars(self.stars)

    def deleteUpgrade(self):
        '''Deletes the current upgrade object from this player'''
        if self.upgrade:
            print "%s's Upgrade Gone" % self.nick
            self.upgrade.clientDelete()

    def destroyShot(self, sId):
        try:
            del self.shots[sId]
        except KeyError:
#            logging.writeException()
            pass

    def addShot(self, shot):
        self.shots[shot.id] = shot

    def canRequestUpgrade(self, upgradeClass):
        if self.team.currentTransaction != None:
            return False, 'Transaction already in play'
        
        elif self.upgrade != None:
            return False, 'You already have an upgrade'
        
        elif self.team.teamStars < upgradeClass.requiredStars:
            return False, 'Your team has insufficient stars'
        
        elif self.ghost:
            return False, 'You are dead! Can\'t purchase an upgrade'
        return True, ''

    def hasThisManyStars(self, numStars):
        return self.stars >= numStars

    def canAddStars(self):
        if not self.team.currentTransaction:
            return False, "No transaction to add stars to"
        return True, ''


    def canAddStarsNow(self, stars):
        '''Actually requests the star-adding'''
        if stars == 0:
            return False, 'Must add at least one star'
        elif self.team.currentTransaction is None:
            return False, 'There is no transaction currently in play'
        try:
            numStars = int(stars)
        except:
            return False, "Please enter a numerical value"
        else:
            if numStars + self.team.currentTransaction.getNumStars(self) > self.stars:
                return False, "You do not have that many stars"
        return True, ''

    def canUseUpgrade(self):
        if self.upgrade is None:
            return False, 'You have no upgrade to use'
        elif self.upgrade.inUse:
            return False, 'Your upgrade is already in use'
        return True, ''

    def requestUse(self):
        assert self.canUseUpgrade()[0]
        self.upgrade.requestUse()
        self.upgradeGauge = self.upgradeTotal = self.upgrade.timeRemaining
        self.universe.onUpgradeUsed.execute(self)

    def canRespawn(self):
        if not self.ghost:
            return False, 'Already Alive'
        elif self.respawnGauge > 0:
            return False, 'Not able to respawn yet'
        elif self.currentZone.orbOwner != self.team:
            return False, 'Not in a friendly Zone'
        else:
            return True, ''

    def requestRespawn(self):
        '''Called by the menu when a player wishes to respawn'''
        assert self.canRespawn()
        self.universe.onPlayerRespawn.execute(self)

    def abandon(self):

        if self.upgrade:
            self.universe.onUpgradeReqDel.execute(self)
        elif self.team.currentTransaction and \
             self.team.currentTransaction.purchasingPlayer == self:
            self.universe.onAbandonTransaction.execute(self.team)
