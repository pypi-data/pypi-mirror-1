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
from trosnoth.src.model.obstacles import *
from trosnoth.src.trosnothgui.ingame.colours import *
from trosnoth.src.model.map import MapLayout
from trosnoth.src.model.universe_base import GameState

# TODO: Don't use isinstance so we don't have to use this
from trosnoth.src.model.shot import Shot, GrenadeShot
from trosnoth.src.model.player import Player

class MapBlockDef(object):
    '''Represents the static information about a particular map block. A map
    block is a grid square, and may contain a single zone, or the interface
    between two zones.'''

    def __init__(self, kind, x, y):
        self.pos = (x, y)       # Pos is the top-left corner of this block.
        assert kind in ('top', 'btm', 'fwd', 'bck')
        self.kind = kind

        self.plObstacles = []   # Obstacles for players.
        self.shObstacles = []   # Obstacles for shots.
        self.indices = MapLayout.getMapBlockIndices(x, y)

        self.rect = pygame.Rect(x, y, 0, 0)
        self.rect.size = (self._getWidth(), MapLayout.halfZoneHeight)

        self.graphics = None
        self.blocked = False    # There's a barrier somewhere depending on type.

        # For body block.
        self.zone = None

        # For interface block.
        self.zone1 = None
        self.zone2 = None

    def _getWidth(self):
        if self.kind in ('top', 'btm'):
            return MapLayout.zoneBodyWidth
        else:
            return MapLayout.zoneInterfaceWidth

    def spawnState(self, universe, zoneWithDef):
        if self.kind == 'top':
            return TopBodyMapBlock(universe, self,
                zoneWithDef.get(self.zone, None))
        elif self.kind == 'btm':
            return BottomBodyMapBlock(universe, self,
                zoneWithDef.get(self.zone, None))
        elif self.kind == 'fwd':
            return ForwardInterfaceMapBlock(universe, self,
                zoneWithDef.get(self.zone1, None),
                zoneWithDef.get(self.zone2, None))
        elif self.kind == 'bck':
            return BackwardInterfaceMapBlock(universe, self,
                zoneWithDef.get(self.zone1, None),
                zoneWithDef.get(self.zone2, None))
        else:
            assert False

class MapBlock(object):
    '''Represents a grid square of the map which may contain a single zone,
    or the interface between two zones.

    Attributes which should be moved entirely to the MapBlockDef:
        pos
        plObstacles
        shObstacles
        rect
    '''

    def __init__(self, universe, defn):
        self.universe = universe
        self.defn = defn
        self.pos = defn.pos     # Pos is the top-left corner of this block.

        self.plObstacles = defn.plObstacles   # Obstacles for players.
        self.shObstacles = defn.shObstacles   # Obstacles for shots.

        self.rect = defn.rect

        self.shots = set()
        self.players = set()
        self.grenades = set()
        self.drawRect = pygame.Rect(0, 0, 0, 0) # drawRect is the rect object
                                                # representing where the block
                                                # must be drawn. It is changed
                                                # by the viewManager object.
        self.drawRect.size = self.rect.size


    def removePlayer(self, player):
        if player in self.players:
            self.players.remove(player)

    def addPlayer(self, player):
        self.players.add(player)

    def __contains__(self, point):
        '''Checks whether a given point is within this zone.'''
        return self.rect.collidepoint(*point)

    def _getBlockLeft(self):
        i, j = self.defn.indices
        if j == 0:
            return None
        return self.universe.zoneBlocks[i][j-1]
    blockLeft = property(_getBlockLeft)

    def _getBlockRight(self):
        i, j = self.defn.indices
        if j >= len(self.universe.zoneBlocks[i]) - 1:
            return None
        return self.universe.zoneBlocks[i][j+1]
    blockRight = property(_getBlockRight)
    
    def _getBlockAbove(self):
        i, j = self.defn.indices
        if i == 0:
            return None
        return self.universe.zoneBlocks[i-1][j]
    blockAbove = property(_getBlockAbove)

    def _getBlockBelow(self):
        i, j = self.defn.indices
        if i >= len(self.universe.zoneBlocks) - 1:
            return None
        return self.universe.zoneBlocks[i+1][j]
    blockBelow = property(_getBlockBelow)

    def getObstacles(self, unitClass):
        if issubclass(unitClass, Player):
            result = list(self.plObstacles)

            return result
        if issubclass(unitClass, (Shot, GrenadeShot)):
            return self.shObstacles
        return


    def draw(self, surface, area):
        '''draw(surface) - draws this map block to the given surface.'''
        if self.defn.graphics is None:
            return

        # Find its rightful place
        rp = (area.left - self.drawRect.left, area.top - self.drawRect.top)
        rr = pygame.rect.Rect(rp, area.size)
        surface.blit(self.defn.graphics.graphic, area.topleft, rr)
        
    def drawMiniBg(self, surface, scale, rect, area = None):
        '''draws the background colours'''
        if self.defn.graphics is None:
            return

        if area is not None:
            cropPos = (area.left - rect.left, area.top - rect.top)
            crop = pygame.rect.Rect(cropPos, area.size)
            surface.blit(self.defn.graphics.getMini(scale), area.topleft, crop)
        else:
            surface.blit(self.defn.graphics.getMini(scale), rect.topleft)

    def getZoneAtPoint(self, x, y):
        '''getZoneAtPoint(x, y)
        Returns what zone is at the specified point, ASSUMING that the point
        is in fact within this map block.'''
        raise NotImplementedError, 'getZoneAtPoint not implemented.'

    def checkShotCollisions(self, player, deltaX, deltaY):
        '''Check for collisions of a local player with shots'''
        for shot in self.shots:
            if shot.team != player.team:
                if self.collideTrajectory(shot.pos, player.pos,
                                          (deltaX, deltaY), 20):
                    if player.phaseshift:
                        self.universe.onShotDestroyed.execute(shot)
                    else:
                        self.universe.onPlayerKilled.execute(player, \
                                                    shot.originatingPlayer,
                                                    shot)

    def checkPlayerCollisions(self, shot, deltaX, deltaY):
        '''Check for collisions of the specified shot with living local
        players. DeltaX and deltaY specify the path along which the shot is
        traveling.'''
        for player in self.players:
            if player.local and not player.ghost:
                if shot.team != player.team:
                    # FIXME: It would be better not to have a hard-coded 20.
                    if self.collideTrajectory(player.pos, shot.pos,
                                              (deltaX, deltaY), 20):
                        print 'player killed 2'
                        self.universe.onPlayerKilled.execute(player, \
                                                            shot.originatingPlayer, \
                                                            shot)

    def collideTrajectory(self, pt, origin, trajectory, tolerance):
        '''Returns true if pt lies within a distance of tolerance from the
        line segment described by origin and trajectory.'''

        # Get distance between point and trajectory origin.
        tr0 = origin
        d0 = ((tr0[0] - pt[0]) ** 2 + (tr0[1] - pt[1]) ** 2) ** 0.5
        if d0 < tolerance:
            return True

        delta = trajectory

        while True:
            # Calculate other end of trajectory.
            tr1 = (tr0[0] + delta[0],
                   tr0[1] + delta[1])
            d1 = ((tr1[0] - pt[0]) ** 2 + (tr1[1] - pt[1]) ** 2) ** 0.5

            # Check for collision.
            if d1 < tolerance:
                return True

            # Refine and loop.
            if d1 < d0:
                tr0, delta = tr1, (-0.5 * delta[0],
                                   -0.5 * delta[1])
            else:
                delta = (0.5 * delta[0],
                         0.5 * delta[1])

            # Check end condition.
            if (delta[0] ** 2 + delta[1] ** 2) < 5:
                return False
    
    def moveUnit(self, unit, deltaX, deltaY):
        '''moveUnit(unit, deltaX, deltaY)
        Attempts to move the unit by the specified amount, taking into
        account the positions of walls. Also checks if the unit
        changes zones or changes map blocks.

        If the unit is a player, checks for collisions with shots.
        If the unit hit an obstacle, returns the obstacle.
        This routine only checks for obstacle collisions if unit.solid() is
        True.
        Assumes that the unit is already within this map block.
        '''
        
        lastObstacle = None
        if unit.solid():
            # Check for collisions with obstacles - find the closest obstacle.
            for obstacle in self.getObstacles(type(unit)):
                if isinstance(unit, Player) and unit._ignore == obstacle:
                    continue
                dX, dY = obstacle.collide(unit.pos, deltaX, deltaY)
                if (dX, dY) != (deltaX, deltaY):
                    # Remember the last obstacle we hit.
                    lastObstacle = obstacle
                    deltaX = dX
                    deltaY = dY

        # Check for change of map block.
        newBlock = False  # This is False because None means leaving the map.

        # Leaving via lefthand side.
        if deltaX < 0 and unit.pos[0] + deltaX < self.pos[0]:
            # Check for collision with left-hand edge.
            y = unit.pos[1] + deltaY * (self.pos[0] - unit.pos[0]) / deltaX
            if self.rect.top <= y <= self.rect.bottom:
                newBlock = self.blockLeft
        if not newBlock and deltaX > 0 and unit.pos[0] + deltaX >= \
                                       self.rect.right:
            # Check for collision with right-hand edge.
            y = unit.pos[1] + deltaY * (self.rect.right - unit.pos[0]) \
                            / deltaX
            if self.rect.top <= y <= self.rect.bottom:
                newBlock = self.blockRight
        if not newBlock and deltaY < 0 and unit.pos[1] + deltaY < self.pos[1]:
            # Check for collision with top edge.
            x = unit.pos[0] + deltaX * (self.pos[1] - unit.pos[1]) / deltaY
            if self.rect.left <= x <= self.rect.right:
                newBlock = self.blockAbove
        if not newBlock and deltaY > 0 and unit.pos[1] + deltaY >= \
                                        self.rect.bottom:
            x = unit.pos[0] + deltaX * (self.rect.bottom - unit.pos[1]) \
                            / deltaY
            if self.rect.left <= x <= self.rect.right:
                newBlock = self.blockBelow
                
        if newBlock == None and isinstance(unit, Player) and unit.ghost:
            return
        
        if newBlock:
            unit.setMapBlock(newBlock)
            if isinstance(unit, Shot):
                self.removeShot(unit)
                newBlock.addShot(unit)
            
            # Another map block can handle the rest of this.
            return unit.currentMapBlock.moveUnit(unit, deltaX, deltaY)
        
        # Check for change of zones.
        if isinstance(unit, Player):
            newZone = self.getZoneAtPoint(unit.pos[0] + deltaX,
                                          unit.pos[1] + deltaY)
            if newZone is None and unit.ghost:
                # Ghost cannot enter purple zones.
                return lastObstacle

            if newZone != unit.currentZone and newZone is not None:
                if self.universe.gameState == GameState.PreGame and \
                           newZone.orbOwner != unit.team:
                    # Disallowed zone change.
                    return lastObstacle
                if not unit.local:
                    newZone = None
            else:
                newZone = None
        else:
            newZone = None

        # Check for player/shot collisions along the path.
        if isinstance(unit, Player):
            if unit.local and not unit.ghost:
                self.checkShotCollisions(unit, deltaX, deltaY)
        elif isinstance(unit, Shot):
            self.checkPlayerCollisions(unit, deltaX, deltaY)
        
        # Move the unit.
        unit.pos = (unit.pos[0] + deltaX,
                      unit.pos[1] + deltaY)
        # Notify (for things like ghost respawn gauge).
        unit.movedBy(deltaX, deltaY)

        if newZone:
            # Zone needs to know which players are in it.
            unit.changeZone(newZone)
            self.universe.onZoneChanged.execute(unit, newZone)

        return lastObstacle
            
    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is'''
        return

    def removeShot(self, shot):
        '''Removes a given shot from this mapBlock'''
        self.shots.remove(shot)

    def addShot(self, shot):
        '''Adds a given shot to this mapBlock'''
        if shot not in self.shots:
            self.shots.add(shot)

    def removeGrenade(self, grenade):
        '''Removes a given grenade from this mapBlock'''
        self.grenades.remove(grenade)

    def addGrenade(self, grenade):
        '''Adds a given grenade to this mapBlock'''
        self.grenades.add(grenade)
                
    def addPlatform(self, pos, dx, reverse):
        '''Adds a horizontal platform which can be dropped through to this
        block's list of obstacles.

        pos         The position of the obstacle's first point relative to the
                    top-left corner of this block, or relative to the top-right
                    corner if reverse is set to True.
        dx          The horizontal displacement from first point to the second
                    point of the obstacle. This value should always be positive.
        reverse     Determines whether the obstacle is defined in terms of the
                    top-left corner of this map block or the top-right corner.
        '''

        # Add the block's position offset.
        pt = [pos[0] + self.pos[0],
              pos[1] + self.pos[1]]
        if reverse:
            pt[0] += self.rect.width

        # Put the platform in.
        x, y = pt

        self._obstacleEdge(pt, 7, LedgeObstacle)
        self._obstacle(pt, (x+dx, y), 0, LedgeObstacle)
        self._obstacleEdge((x+dx, y), 0, LedgeObstacle)

    def addObstacle(self, points, reverse):
        '''Adds an obstacle to this block's list of obstacles.

        points      A sequence specifying the positions of the obstacle's points
                    relative to the top-left corner of this block, or relative
                    to the top-right corner if reverse is set to True.
        reverse     Determines whether the obstacle is defined in terms of the
                    top-left corner of this map block or the top-right corner.
        '''

        # Go through and interpret list of points.
        # curPt - the point about which the next obstacle will start.
        # nextPt - the point about which the next obstacle will end.
        # cuCnr - the corner of the current point about from which the
        #           next line segment should start. Corners are represented
        #           as a number from 0 to 7, starting at zero as vertically
        #           above the point, and proceding in a clockwise direction.
        
        iterPoints = iter(points)
        nextPt = iterPoints.next()
        nextPt = [nextPt[0] + self.pos[0],
                  nextPt[1] + self.pos[1]]
        if reverse:
            nextPt[0] += self.rect.width
        curCnr = None

        while True:
            # Get next point.
            curPt = nextPt
            try:
                nextPt = iterPoints.next()
            except StopIteration:
                break

            # Add the block's position offset.
            nextPt = [nextPt[i] + self.pos[i] for i in (0,1)]
            if reverse:
                nextPt[0] += self.rect.width

            # Decide what corner it needs.
            dx, dy = (nextPt[i] - curPt[i] for i in (0, 1))
            if dx > 0:
                if dy < 0:      cnr = 7
                elif dy == 0:   cnr = 0
                else:           cnr = 1
            elif dx == 0:
                if dy > 0:      cnr = 2
                else:           cnr = 6
            else:
                if dy > 0:      cnr = 3
                elif dy == 0:   cnr = 4
                else:           cnr = 5

            if not curCnr:
                # First point: gets a bit of extra border.
                if cnr % 2:
                    curCnr = (cnr - 1) % 8
                else:
                    curCnr = (cnr - 2) % 8
                
            # Advance around current point until we reach the right corner.
            while curCnr != cnr:
                self._obstacleEdge(curPt, curCnr)
                curCnr = (curCnr + 1) % 8

            # Insert the correct line segment.
            self._obstacle(curPt, nextPt, curCnr)

        # Last point also gets a bit of extra border.
        if cnr % 2:
            cnr = (cnr + 1) % 8
        else:
            cnr = (cnr + 2) % 8
        while curCnr != cnr:
            self._obstacleEdge(nextPt, curCnr)
            curCnr = (curCnr + 1) % 8
        
    def _obstacle(self, pt0, pt1, cnr, kind=None):
        '''(kind, pt, delta) - internal. Adds a barrier for shots and players.
        kind        the class of obstacle to add for players.
        pt          the point about which the obstacle starts.
        offset      multipliers for offset to add to point.
        data        displacement from starting point.'''

        x,y = pt0
        delta = tuple(pt1[i] - pt0[i] for i in (0,1))
        kind2, offset, dummy, dummy = _cornerInfo[cnr]
        if kind == None:
            kind = kind2

        ox, oy = (offset[i] * self.universe.halfPlayerSize[i] for i in (0,1))
        self.plObstacles.append(kind((x+ox, y+oy), delta))
        # Shots shouldn't worry about ledgeObstacles
        if kind == LedgeObstacle:
            pass
        else:
            ox, oy = (offset[i] * self.universe.halfShotSize[i] for i in (0,1))
            self.shObstacles.append(kind((x+ox, y+oy), delta))

    def _obstacleEdge(self, pt, cnr, kind=None):
        '''(pt, cnr) - internal. Adds an edge barrier for players and shots
        around the specified point.
        '''
        if kind != LedgeObstacle:
            x,y = pt
            dummy, offset, kind2, deltaOffset = _cornerInfo[cnr]
            if kind == None:
                kind = kind2

            ox, oy = (offset[i] * self.universe.halfPlayerSize[i] for i in (0,1))
            delta = [deltaOffset[i] * self.universe.halfPlayerSize[i] for i in (0,1)]
            self.plObstacles.append(kind((x+ox, y+oy), delta))
            ox, oy = (offset[i] * self.universe.halfShotSize[i] for i in (0,1))
            delta = [deltaOffset[i] * self.universe.halfShotSize[i] for i in (0,1)]
            self.shObstacles.append(kind((x+ox, y+oy), delta))
            
class BodyMapBlock(MapBlock):
    '''Represents a map block which contains only a single zone.'''

    def __init__(self, universe, defn, zone):
        super(BodyMapBlock, self).__init__(universe, defn)
        self.zone = zone

    def __repr__(self):
        return '< %s >' % self.zone

    def getZoneAtPoint(self, x, y):
        return self.zone
    
    def Zones(self):
        if self.zone:
            return [self.zone]
        else:
            return []

    def drawMiniBg(self, surface, scale, rect, area = None):
        '''draws the background colours'''

        if self.zone:
            clr = self.zone.getMiniMapColour()
        else:
            clr = (0, 0, 0)
        if area is not None:
            pygame.draw.rect(surface, clr, area)
        else:
            pygame.draw.rect(surface, clr, rect)
        
        super(BodyMapBlock, self).drawMiniBg(surface, scale, rect, area)
    
    def draw(self, surface, area):
        # First draw the background the colour of the zone.
        if self.zone:
            clr = self.zone.getBackgroundColour()
            surface.fill(clr, area)

        # Now draw the obstacles.
        super(BodyMapBlock, self).draw(surface, area)
        if self.zone:
            # Draw the orb.
            img = self.zone.getOrbImage()
            r = img.get_rect()
            r.center = self.orbPos()
            surface.blit(img, r)


class TopBodyMapBlock(BodyMapBlock):
    '''Represents a map block containing the top half of a zone.'''
    
    def orbPos(self):
        return self.drawRect.midbottom

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is'''

        return min(abs(player.pos[1] - self.rect.top), \
                   self.blockLeft.fromEdge(player),\
                   self.blockRight.fromEdge(player))

class BottomBodyMapBlock(BodyMapBlock):
    '''Represents a map block containing the bottom half of a zone.'''
    
    def orbPos(self):
        return self.drawRect.midtop    

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is'''
        
        return min(abs(self.rect.bottom - player.pos[1]), \
                   self.blockLeft.fromEdge(player),\
                   self.blockRight.fromEdge(player))

class InterfaceMapBlock(MapBlock):
    '''Base class for map blocks which contain the interface between two
    zones.'''

    def __init__(self, universe, defn, zone1, zone2):
        super(InterfaceMapBlock, self).__init__(universe, defn)

        self.zone1 = zone1
        self.zone2 = zone2
        
    def Zones(self):
        tempZones = []
        if self.zone1 is not None:
            tempZones.append(self.zone1)
        if self.zone2 is not None:
            tempZones.append(self.zone2)
        return tempZones

    def draw(self, surface, area):
        # First draw the background the colour of the zone.
        if not (self.zone1 or self.zone2):
            # No zones to draw
            return
        
        if self.zone1 and self.zone2 and \
           self.zone1.zoneOwner == self.zone2.zoneOwner:
            # Same colour; simply fill in that colour
            clr = self.zone1.getBackgroundColour()
            surface.fill(clr, area)
        else:
            if not self.zone1:
                z1 = None
            else:
                if self.zone1.zoneOwner:
                    z1 = self.zone1.zoneOwner.id
                else:
                    z1 = '\x00'
            if not self.zone2:
                z2 = None
            else:
                if self.zone2.zoneOwner:
                    z2 = self.zone2.zoneOwner.id
                else:
                    z2 = '\x00'
                    
            # This is getting a pre-made image for the background colour
            img = interfaceSurfaces[type(self)][(z1, z2)]

            rp = (area.left - self.drawRect.left, area.top - self.drawRect.top)
            rr = pygame.rect.Rect(rp, area.size)
            surface.blit(img, area.topleft, rr)

        # Now draw the obstacles.
        super(InterfaceMapBlock, self).draw(surface, area)
    
class ForwardInterfaceMapBlock(InterfaceMapBlock):
    '''Represents a map block which contains the interface between two
    zones, split in the direction of a forward slash '/'.
    Note that exactly on the diagonal counts as being in the left-hand zone.
    '''

    def __repr__(self):
        return '< %s / %s >' % (self.zone1, self.zone2)

    def getZoneAtPoint(self, x, y):
        # Equation of interface line:
        #   (y - self.y) = -(halfZoneHeight / interfaceWidth)(x - self.x)
        #                        + halfZoneHeight
        deltaY = y - self.pos[1] - MapLayout.halfZoneHeight
        deltaX = x - self.pos[0]

        if deltaY * MapLayout.zoneInterfaceWidth > \
               -MapLayout.halfZoneHeight * deltaX:
            return self.zone2
        return self.zone1


    def drawMiniBg(self, surface, scale, rect, area = None):
        '''draws the background colours. Can be given an optional area, to
        only draw a part of this mapBlock.'''
        # TODO: implement as per draw()
        if area:
            tempSurface = pygame.surface.Surface(rect.size)
            tempRect = tempSurface.get_rect()
        if self.zone1:
            clr = self.zone1.getMiniMapColour()
        else:
            clr = (0, 0, 0)
        if area:
            pts = (tempRect.topleft, tempRect.topright, tempRect.bottomleft)
            pygame.draw.polygon(tempSurface, clr, pts)
        else:
            pts = (rect.topleft, rect.topright, rect.bottomleft)
            pygame.draw.polygon(surface, clr, pts)

        if self.zone2:
            clr = self.zone2.getMiniMapColour()
        else:
            clr = (0, 0, 0)


        if area:
            pts = (tempRect.bottomright, tempRect.topright, tempRect.bottomleft)
            pygame.draw.polygon(tempSurface, clr, pts)
            # Now put it onto surface
            cropPos = (area.left - rect.left, area.top - rect.top)
            crop = pygame.rect.Rect(cropPos, area.size)
            surface.blit(tempSurface, area.topleft, crop)
        else:
            pts = (rect.bottomright, rect.topright, rect.bottomleft)
            pygame.draw.polygon(surface, clr, pts)


        
        super(ForwardInterfaceMapBlock, self).drawMiniBg(surface, scale, rect, area)

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is.
        Assumes that the player is actually in this map block.'''
        relPos = (self.rect.left - player.pos[0], self.rect.top - player.pos[1])
        # Note: this following formula relies upon the dimensions:
        # MapLayout.halfZoneHeight = 384
        # MapLayout.zoneInterfaceWidth = 512
        # Should they be changed, should change this to:
        # d = sin(theta) * abs(relPos[1] + relPos[0] * \
        # MapLayout.halfZoneHeight / MapLayout.zoneInterfaceWidth + 384)
        # (where theta is the angle formed by the diagonal line seperating the
        # zones, and a vertical line).
        d = 0.8 * abs(relPos[1] + relPos[0] * 0.75 + 384)
        return d

class BackwardInterfaceMapBlock(InterfaceMapBlock):
    '''Represents a map block which contains the interface between two
    zones, split in the direction of a backslash '\'.
    Note that a point exactly on the diagonal counts as being in the left-hand
    zone.
    '''

    def __repr__(self):
        return '< %s \ %s >' % (self.zone1, self.zone2)

    def getZoneAtPoint(self, x, y):
        # Equation of interface line:
        #   (y - self.y) = (halfZoneHeight / interfaceWidth)(x - self.x)
        deltaY = y - self.pos[1]
        deltaX = x - self.pos[0]

        if deltaY * MapLayout.zoneInterfaceWidth > \
               MapLayout.halfZoneHeight * deltaX:
            return self.zone1
        return self.zone2

    def drawMiniBg(self, surface, scale, rect, area = None):
        '''draws the background colours'''
        # TODO: implement it the same as draw()
        if area:
            tempSurface = pygame.surface.Surface(rect.size)
            tempRect = tempSurface.get_rect()
        if self.zone1:
            clr = self.zone1.getMiniMapColour()
        else:
            clr = (0, 0, 0)

        if area:
            pts = (tempRect.topleft, tempRect.bottomright, tempRect.bottomleft)
            pygame.draw.polygon(tempSurface, clr, pts)
        else:
            pts = (rect.topleft, rect.bottomright, rect.bottomleft)
            pygame.draw.polygon(surface, clr, pts)

        if self.zone2:
            clr = self.zone2.getMiniMapColour()
        else:
            clr = (0, 0, 0)
        if area:
            pts = (tempRect.topleft, tempRect.bottomright, tempRect.topright)
            pygame.draw.polygon(tempSurface, clr, pts)
            # Now put it onto surface
            cropPos = (area.left - rect.left, area.top - rect.top)
            crop = pygame.rect.Rect(cropPos, area.size)
            surface.blit(tempSurface, area.topleft, crop)
        else:
            pts = (rect.topleft, rect.bottomright, rect.topright)
            pygame.draw.polygon(surface, clr, pts)

        
        super(BackwardInterfaceMapBlock, self).drawMiniBg(surface, scale, rect, area)

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is.
        Assumes that the player is actually in this map block.'''
        relPos = (self.rect.left - player.pos[0], self.rect.top - player.pos[1])
        
        # Note: this following formula relies upon the dimensions:
        # MapLayout.halfZoneHeight = 384
        # MapLayout.zoneInterfaceWidth = 512
        # Should they be changed, should change this to:
        # d = sin(theta) * abs(relPos[1] - relPos[0] * \
        # MapLayout.halfZoneHeight / MapLayout.zoneInterfaceWidth)
        # where theta is the angle formed by the diagonal line seperating the
        # zones, and a vertical line.
        d = 0.8 * abs(relPos[1] - relPos[0] * 3 / 4)
        return d

            
        
# The following definition is used by the player class to add obstacles.
# Corner info: for each corner number (from 0 to 7), has a tuple of the
#            form (kind, offset, fillKind, fillDelta)
# kind          the kind of obstacle to use in _obstacle
# offset        the offset from the current point
# fillKind      the kind of obstacle to use for a filler from this point
# fillDelta     the change in offset for a filler from this corner
_cornerInfo = [(GroundObstacle, ( 0, -1), GroundObstacle,     ( 1,  0)),
               (GroundObstacle, ( 1, -1), FillerRoofObstacle, ( 0,  1)),
               (VerticalWall,   ( 1,  0), FillerRoofObstacle, ( 0,  1)),
               (RoofObstacle,   ( 1,  1), FillerRoofObstacle, (-1,  0)),
               (RoofObstacle,   ( 0,  1), FillerRoofObstacle, (-1,  0)),
               (RoofObstacle,   (-1,  1), FillerRoofObstacle, ( 0, -1)),
               (VerticalWall,   (-1,  0), FillerRoofObstacle, ( 0, -1)),
               (GroundObstacle, (-1, -1), GroundObstacle,     ( 1,  0))
               ]

options = ('A', 'B', '\x00', None)
colours = {'A' : team1bg,
           'B' : team2bg,
           '\x00' : neutral_bg,
           None : (0,0,0)}
forw = {}
backw = {}
i = 0
while i < len(options):
    # Skip ('A', 'B') by always starting j at least at '\x00'
    j = max(i + 1, 2)
    clr1 = colours[options[i]]
    while j < len(options):
        clr2 = colours[options[j]]
        
        img = pygame.surface.Surface((MapLayout.zoneInterfaceWidth, \
                                      MapLayout.halfZoneHeight))
        rect = img.get_rect()
        pts1 = (rect.topleft, rect.bottomright, rect.bottomleft)
        pts2 = (rect.topleft, rect.topright, rect.bottomright)
        pygame.draw.polygon(img, clr1, pts1)
        pygame.draw.polygon(img, clr2, pts2)
        img.set_colorkey((0,0,0))
        
        backw[(options[i], options[j])] = img
        
        img = pygame.transform.flip(img, True, False)
        forw[(options[j], options[i])] = img
        
        img = pygame.transform.flip(img, False, True)
        backw[(options[j], options[i])] = img
        
        img = pygame.transform.flip(img, True, False)
        forw[(options[i], options[j])] = img
        
        j += 1
    i += 1



# interfaceSurfaces: contains the surfaces used to blit the background
# colours for InterfaceMapBlocks. Each tuple key contains the two zone owners
# (in order) for which the corresponding surface is stored. Note that '\x00'
# indicates a neutral zone, whereas None indicates that there is no zone.
interfaceSurfaces = {ForwardInterfaceMapBlock: forw,
                     BackwardInterfaceMapBlock: backw
                    }

del options
del forw
del backw
del img