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

'''universe.py - defines anything that has to do with the running of the
universe. This includes players, shots, zones, and the level itself.'''

from math import sin, cos, atan2
import struct
import random

from twisted.internet import reactor
import pygame

import trosnoth
from trosnoth.src.base import MenuError
from trosnoth.src.utils.utils import timeNow
from trosnoth.src.trosnothgui import defines
import trosnoth.src.utils.logging as logging
import trosnoth.src.modes as modes
from trosnoth.src.trosnothgui.ingame.colours import *
from trosnoth.src.universe_base import GameState
from trosnoth.src.gui.framework.basics import SingleImage, AngledImageCollection, Animation

from trosnoth.src.trosnothgui.ingame import colours

from trosnoth.data import fonts, getPath, loadSprite

# FIXME: there's the potential for some things to require an interface
# before it is created (such as using a transaction)

def makeImage(string, colorkey = (255,255,255)):
    img = loadSprite(string)
    img.set_colorkey(colorkey)
    return img

def makeImages(strings, colorkey = (255,255,255)):
    images = []
    for string in strings:
        images.append(makeImage(string, colorkey))
    return images

def init():
    '''Initialises anything that's needed by this module. This function should
    only be called after pygame.init() and after the video mode has been set.'''
    # Load the name font.
    pygame.font.init()
    NameTag.nameFont = pygame.font.Font(getPath(fonts, 'FreeSans.ttf'), 20)

class Team(object):
    '''Represents a team of the game'''
    def __init__(self, bkgColour, sysMsgColour, chatColour, miniMapZoneOwnColour,
                 miniMapOrbOwnColour, miniPlayerClr, miniGhostClr, img, shotImg, orbImg, teamID):
        self.currentTransaction = None
        self.numOrbsOwned = 0
        try:
            trosnoth._testmode
            self.teamStars = 100
        except AttributeError:
            self.teamStars = 0
        self.backgroundColour = bkgColour
        self.sysMessageColour = sysMsgColour
        self.chatColour = chatColour
        self.miniMapZoneOwnColour = miniMapZoneOwnColour
        self.miniMapOrbOwnColour = miniMapOrbOwnColour
        self.miniMapPlayerColour = miniPlayerClr
        self.miniMapGhostColour = miniGhostClr
        self.captain = None
        self.ready = False
        self.image = img
        self.shotImage = shotImg
        self.orbImage = orbImg

        if (not isinstance(teamID, str)) or len(teamID) != 1:
            raise TypeError, 'teamID must be a single character'
        self.id = teamID

        if teamID == "A":
            self.teamName = "Blue"
        else:
            self.teamName = "Red"
        
    def __repr__(self):
        return '%s team' % self.teamName

    def orbLost(self):
        '''Called when a orb belonging to this team has been lost'''
        self.numOrbsOwned -= 1

    def orbGained(self):
        '''Called when a orb has been attributed to this team'''
        self.numOrbsOwned += 1

    def checkLost(self):
        '''Returns whether the team has lost the game (True = Lost Game)'''
        return self.numOrbsOwned == 0

    def validate(self, numOrbs, netClient):
        if self.numOrbsOwned != numOrbs:
            netClient.requestZones()

    def updateTeamStars(self, stars):
        self.teamStars += stars

    def changeTeamName(self, name):
        self.teamName = name     
            
    @staticmethod
    def setOpposition(teamA, teamB):
        teamA.opposingTeam = teamB
        teamB.opposingTeam = teamA

class MapLayout(object):
    '''Stores static info about the layout of the map.

    Attributes:
        centreX, centreY: the x and y coordinates of the map centre.
        zones: collection of zoneDefs
        blocks: collection of blockDefs
    '''
    
    # The dimensions of zones. See diagram below.
    halfZoneHeight = 384        # a / 2
    zoneBodyWidth = 1024        # b
    zoneInterfaceWidth = 512    # c
    
    # This diagram explains the dimensions defined above.
    #     \___________/ _ _ _ _
    #     /           \       ^
    #    /             \      |
    # __/               \___  a
    #   \               /|    |
    #    \             / |    |
    #     \___________/ _|_ _ v
    #     /|         |\  | 
    #      |<-- b -->|<c>|

    # TODO!!!
    def __init__(self, details):
        '''details is a list of lists of tuples of the form (layout, owner)
        where layout is a BlockLayout object and owner is 0, 1 or 2 to indicate
        which team initially owns the zone.'''
    def __init__(self, universe, halfMapWidth, mapHeight):
        totalWidth = halfMapWidth * 2 + 1
        middleHeight = ((halfMapWidth - 1) % 2) + 1 + mapHeight
        zonesPerTeam = halfMapWidth * mapHeight + halfMapWidth / 2
        
        if middleHeight == mapHeight + 2:
            highExists = True
        else:
            highExists = False

        # Calculate position of centre.
        self.centreX = (halfMapWidth + 0.5) * MapLayout.zoneBodyWidth + \
                       (halfMapWidth + 1) * MapLayout.zoneInterfaceWidth
        self.centreY = middleHeight * MapLayout.halfZoneHeight
        
        # Collection of all zone definitions:
        self.zones = set()

        # Zones shall also be stored as a multidimensional array
        # in the following format of column/vertical position:
        #    0   1   2   3   4   5   6
        # 0 -/a  a  a\-  -  -/d  d  d\-
        # 1 -\a  a  a/c  c  c\d  d  d/-
        # 2 -/b  b  b\c  c  c/e  e  e\-
        # 3 -\b  b  b/-  -  -\e  e  e/-
        # so that the players' currentZone can more easily be calculated (in
        # the getMapBlockIndices procedure below)
        
        # This will be stored in the format of a list of lists of MapBlocks.
        # The most encompassing list will store the rows.
        # Each "row" will be a list of blocks.
        # Each "block" will be an instance of a subclass of MapBlock.

        self.blocks = []
        blockTypes = ('btm', 'fwd', 'top', 'bck')
        y = 0

        # Decide which type of block to start with.
        if halfMapWidth % 2 == 0:
            nextBlock = 1
        else:
            nextBlock = 3

        prevRow = None
        # Initialise self.blocks
        for i in range(middleHeight * 2):
            row = []
            x = 0
            bodyBlock = None
            for j in range(totalWidth):
                # Add an interface.
                blockType = blockTypes[nextBlock]
                ifaceBlock = MapBlockDef(blockType, x, y)
                row.append(ifaceBlock)
                
                x = x + MapLayout.zoneInterfaceWidth
                nextBlock = (nextBlock + 1) % 4
                
                # Add a body block.
                blockType = blockTypes[nextBlock]
                bodyBlock = MapBlockDef(blockType, x, y)
                row.append(bodyBlock)
                
                x = x + MapLayout.zoneBodyWidth
                nextBlock = nextBlock + 1

            # Add the last interface.
            blockType = blockTypes[nextBlock]
            ifaceBlock = MapBlockDef(blockType, x, y)
            row.append(ifaceBlock)
            
            self.blocks.append(row)
            y = y + MapLayout.halfZoneHeight

            prevRow = row

        # height: low means the column is of height mapHeight
        # mid means it is mapHeight + 1, high means mapHeight + 2 (middleHeight)

        # height starts (and ends) at low in every case.
        height = "low"

        # numSoFar keeps track of the number of zones created so far.
        numSoFar = 0

        # prevCol (previous Column) tells how high the previous column was.
        prevCol = None

        ''' To calculate adjacent zones, the zones were conceptualised in the
         following pattern, counting downwards by column, then left to right:
         (assuming mapHeight = 3, halfMapWidth = 2)
              7
            3    12
         0    8     16
            4    13
         1    9     17
            5    14
         2    10    18
            6    15
              11

        '''

        '''In order to create each of the zones, we will iterate firstly through
        each of the columns, then through each of the zones in each column. This
        allows us to calculate adjacent zones based on column height.'''

        # Keep track of where the zones should be put.
        xCoord = MapLayout.zoneInterfaceWidth + int(MapLayout.zoneBodyWidth / 2)
        
        # Iterate through each column:
        for i in range(0, totalWidth):
            # Determine number of zones in the current column
            if height == "low":
                colHeight = mapHeight
            elif height == "mid":
                colHeight = mapHeight + 1
            elif height == "high":
                colHeight = mapHeight + 2

            # Calculate y-coordinate of the first zone in the column.
            if height == "low" and highExists:
                yCoord = MapLayout.halfZoneHeight
            elif (height == "mid" and highExists) or \
                 (height == "low" and not highExists):
                yCoord = 0
            elif height == "high" or \
                 (height == "mid" and not highExists):
                yCoord = -MapLayout.halfZoneHeight

            prevZone = None

            # Iterate through each zone in the column
            for j in range(0, colHeight):

                # Determine Team, and create a zone.
                if i < halfMapWidth:
                    team = universe.teams[0]
                elif i > (halfMapWidth):
                    team = universe.teams[1]
                else:
                    team = None

                # Determine co-ordinates of the zone's orb (middle of zone)
                yCoord = yCoord + 2 * MapLayout.halfZoneHeight
                
                newZone = ZoneDef(numSoFar, team, xCoord, yCoord)

                # Tell the team object that it owns one more zone
                if team:
                    team.orbGained()
                

                # Link this zone to the zone above.
                if prevZone is not None:
                    prevZone.adjacentZones.add(newZone)
                    newZone.adjacentZones.add(prevZone)
                    
                # Add zone to list of zones
                self.zones.add(newZone)

                
                # Add zone to blocks
                if highExists and height == "low":
                    startRow = 2 + j * 2
                elif (highExists and height == "mid") or \
                     (not highExists and height == "low"):
                    startRow = 1 + j * 2
                elif height == "high" or \
                     (not highExists and height == "mid"):
                    startRow = 0 + j * 2
                else:
                    raise Exception, "There's an error in blocks allocation"

                startCol = i * 2
                # Put new zone into blocks, and connect it to zones left.
                for y in range(startRow, startRow+2):
                    self.blocks[y][startCol+2].zone1 = newZone
                    self.blocks[y][startCol+1].zone = newZone
                    block = self.blocks[y][startCol]
                    block.zone2 = newZone
                    
                    if block.zone1:
                        # Connect this block to the block to the left.
                        block.zone1.adjacentZones.add(newZone)
                        newZone.adjacentZones.add(block.zone1)

                        # Make sure the block is not divided.
                        block.blocked = False

                # If block is at the top of a column, it must have a roof.
                if prevZone is None:
                    self.blocks[startRow][startCol+1].blocked = True
                
                numSoFar = numSoFar + 1
                prevZone = newZone

            # Make sure that the bottom zone in each column has a floor.
            self.blocks[startRow+1][startCol+1].blocked = True

            # Reset for next column:    
            prevCol = height
            prevColHeight = colHeight

            # Advance x-coordinate.
            xCoord = xCoord + MapLayout.zoneBodyWidth + MapLayout.zoneInterfaceWidth

            # Determine how high the next column will be:
            if height == "low":
                if i == totalWidth - 1:
                    height = None
                else:
                    height = "mid"
            elif height == "mid":
                if i == halfMapWidth - 1:
                    height = "high"
                else:
                    height = "low"
            elif height == "high":
                height = "mid"
        
        # Zone initialisation and calculations end here.

    @staticmethod
    def getMapBlockIndices(xCoord, yCoord):
        '''Returns the index in Universe.zoneBlocks of the map block which the
        given x and y-coordinates belong to.
        (0, 0) is the top-left corner.

        To find a zone, use MapBlock.getZoneAtPoint()'''
        
        blockY = int(yCoord // MapLayout.halfZoneHeight)

        blockX, remainder = divmod(xCoord, MapLayout.zoneBodyWidth + \
                                   MapLayout.zoneInterfaceWidth)
        if remainder >= MapLayout.zoneInterfaceWidth:
            blockX = int(2 * blockX + 1)
        else:
            blockX = int(2 * blockX)

        return blockY, blockX            

class MapState(object):
    '''Stores dynamic info about the layout of the map including who owns what zone.

    Attributes:
        layout - the static MapLayout
        zones - a set of zones
        blocks - a set of blocks
        zoneWithId - mapping from zone id to zone (TODO: eventially move this to client)
    '''
    def __init__(self, universe, halfMapWidth, mapHeight):
        self.layout = MapLayout(universe, halfMapWidth, mapHeight)

        self.zones = set()
        self.zoneWithDef = {}
        for zone in self.layout.zones:
            newZone = ZoneState(universe, zone)

            self.zones.add(newZone)
            self.zoneWithDef[zone] = newZone

        self.zoneWithId = {}
        for zone in self.zones:
            self.zoneWithId[zone.id] = zone

        self.zoneBlocks = []
        for row in self.layout.blocks:
            newRow = []
            for blockDef in row:
                newRow.append(blockDef.spawnState(universe, self.zoneWithDef))
            self.zoneBlocks.append(newRow)
            
class Universe(object):
    '''Universe(netClient, halfMapWidth, mapHeight)
    Keeps track of where everything is in the level, including the locations
    and states of every alien, the terrain positions, and who owns the
    various territories and orbs.'''

    # The size of players and shots.
    halfPlayerSize = (10, 19)
    halfShotSize = (5, 5)

    def __init__(self, netClient, halfMapWidth, mapHeight):
        '''netClient is the client that local players should send their state
        updates to.

        halfMapWidth:   is the number of columns of zones in each team's
                        territory at the start of the game. There will always
                        be a single column of neutral zones between the two
                        territories at the start of the game.
        mapHeight:      is the number of zones in every second column of
                        zones. Every other column will have mapHeight + 1
                        zones in it. This is subject to the constraints that
                        (a) the columns at the extreme ends of the map will
                        have mapHeight zones; (b) the central (initially
                        neutral) column of zones will never have fewer zones
                        in it than the two bordering it - this will sometimes
                        mean that the column has mapHeight + 2 zones in it.'''

        # Initialise
        self.gameState = GameState.PreGame
        self.startTime = 0
        self.zonesToReset = []
        self.playerWithId = {}
        self.teamWithId = {'\x00' : None}

        # Create Teams:
        if netClient is not None:
            player1img = makeImage('Blue.png')
            teamAShot = makeImage('blueShot.bmp')
            player1img.set_colorkey((0,0,0))
            team1orb = makeImage('blueOrb.png')
            player2img = makeImage('Red.png')
            teamBShot = makeImage('redShot.bmp')
            player2img.set_colorkey((0,0,0))
            team2orb = makeImage('redOrb.png')

            self.neutralOrb = makeImage('greyOrb.png')

            # This is an active universe.

            self.teams = (Team(team1bg,
                               team1msg,
                               team1chat,
                               team1Mn_zone,
                               team1Mn_mk,
                               team1Mn_pl,
                               team1Mn_gh,
                               player1img,
                               teamAShot,
                               team1orb,
                               'A'),
                          Team(team2bg,
                               team2msg,
                               team2chat,
                               team2Mn_zone,
                               team2Mn_mk,
                               team2Mn_pl,
                               team2Mn_gh,
                               player2img,
                               teamBShot,
                               team2orb,
                               'B'))
        else:
            # This universe will not actually be displayed (created by server)
            self.teams = (Team(colours.team1bg,
                               colours.team1msg,
                               None,
                               'A'),
                          Team(colours.team2bg,
                               colours.team2msg,
                               None,
                               'B'))
            
        Team.setOpposition(self.teams[0], self.teams[1])
        
        for t in self.teams:
            self.teamWithId[t.id] = t
                
        # Set up zones
        self.zoneWithDef = {}
        self.map = MapState(self, halfMapWidth, mapHeight)
        self.zoneWithId = self.map.zoneWithId
        self.zones = self.map.zones
        self.zoneBlocks = self.map.zoneBlocks

        self.netClient = netClient
        self.players = pygame.sprite.Group()
        self.grenades = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()
        self.currentTime = timeNow()
        self.gameOverTime = None
        self.gameModeController = modes.GameMode(Shot, Player, GrenadeShot)

    def setGameMode(self, mode):
        try:
            getattr(self.gameModeController, mode)()
            print "Client: GameMode is set to " + mode
        except AttributeError:
            print "No such gameMode"
        except TypeError:
            print "No such gameMode"

    def setTimeLeft(self, time):
        # TODO: could do some validation here.
        pass

    def getTimeLeft(self):
        if self.gameState == GameState.PreGame:
            return None
        elif self.gameState == GameState.InProgress:
            return self.startTime + self.gameDuration - timeNow()
        elif self.gameState == GameState.Ended:
            return self.startTime + self.gameDuration - self.gameOverTime

    def showMessage(self, text, colour = None):
        self.netClient.interface.newMessage(text, colour)

    def gameOver(self):
        self.gameOverTime = timeNow()
        self.gameState = GameState.Ended

    def gameStart(self, time):
        if self.gameState == GameState.PreGame:
            self.gameDuration = time
            self.startTime = timeNow()
            self.gameState = GameState.InProgress

    def newPlayer(self, player):
        '''Adds this player to this universe.'''
        # Remember this player.
        player.add(self.players)
        self.playerWithId[player.id] = player

        # Make sure player knows its zone
        i, j = MapLayout.getMapBlockIndices(*player.pos)
        try:
            player.currentMapBlock = self.zoneBlocks[i][j]
        except IndexError:
            logging.writeException()
            raise IndexError, 'player start position is off the map'        

    def delPlayer(self, player):
        '''Removes the specified player from this universe. Should be called
        by the network client when the server sends an appropriate message.'''
        try:
            del self.playerWithId[player.id]
        except KeyError:
            logging.writeException()
            pass
        
    def tick(self):
        '''Advances all players and shots to their new positions.'''
        # Calculate the time lapse since last update.
        deltaT = timeNow() - self.currentTime
        self.currentTime += deltaT

        # Update the player and shot positions.
        self.shots.update(deltaT)
        self.players.update(deltaT)
        self.grenades.update(deltaT)

        # Tell the network about tagged zones
        for zone in self.zonesToReset:
            zone.taggedThisTime = False
        self.zonesToReset = []

    def shotFired(self, id, team, pos, angle, player, turret):
        '''This should be called by the networkClient object when the server
        indicates that a player has fired a shot.'''
        if turret and not player.turret:
            self.netClient.requestUpgrades()
        
        self.shots.add(Shot(id, team, pos, angle, player, turret))

    def shotWithId(self, pId, sId):
        try:
            return self.playerWithId[pId].shots[sId]
        except:
            logging.writeException()
            return None


        
    def checkTag(self, tagger):
        '''Checks to see if the player has touched the orb of its currentZone
        If so, it informs the network via netClient'''

        # How zone tagging works (more or less)
        # 1. In its _move procedure, if a player is local, it will call checkTag
        # 2. If it is close enough to the orb, and it has the numeric
        #    advantage, and it onws at least one adjacent zone, it has tagged
        #    the zone
        # 3. The zone is checked again to see if the opposing team has also
        #    tagged it
        #    - If so, the zone is rendered neutral (if it's already neutral,
        #    nothing happens).
        #    - If not, the zone is considered to be tagged by the team.
        # 4. If any zone ownership change has been made, the server is informed
        #    however, no zone allocation is performed yet.
        # 5. The server should ensure that the zone hasn't already been tagged
        #    (such as in the situation of two players form the one team tag
        #    a zone simultaneously), as well as checking zone numbers,
        #    before telling all clients of the zone change.
        # 6. The individual clients recalculate zone ownership based on the
        #    zone change

        zone = tagger.currentZone
        if tagger.team == zone.orbOwner:
            return
        
        # If the tagging player has a phase shift, the zone will not be tagged.
        if tagger.phaseshift:
            return

        # Ensure that the zone has not already been checked in this tick:
        if zone is None or zone.taggedThisTime:
            return


        # Radius from orb (in pixels) that counts as a tag.
        tagDistance = 35
        xCoord1, yCoord1 = tagger.pos
        xCoord2, yCoord2 = zone.defn.pos

        distance = ((xCoord1 - xCoord2) ** 2 + (yCoord1 - yCoord2) ** 2) ** 0.5
        if distance < tagDistance:
            # Check to ensure the team owns an adjacent orb
            found = False
            for adjZoneDef in zone.defn.adjacentZones:
                adjZone = self.zoneWithDef[adjZoneDef]
                if adjZone.orbOwner == tagger.team:
                    found = True
                    break
            if not found:
                return

            # Check to see if the team has sufficient numbers to take the zone.
            numTaggers = 0
            numDefenders = 0
            for player in zone.players.sprites():
                if player.turret:
                    # Turreted players do not count as a player for the purpose
                    # of reckoning whether an enemy can capture the orb
                    continue
                if player.team == tagger.team:
                    numTaggers += 1
                else:
                    numDefenders += 1

            if numTaggers > numDefenders or numTaggers > 3:
                   
                if numDefenders > 3 and \
                   zone.checkMore(tagger.team.opposingTeam):
                    # The other team has also tagged it
                    if zone.orbOwner != None:
                        self.netClient.sendZoneTagged(zone, None, None)
                else:
                    # This team is the only to have tagged it
                    self.netClient.sendZoneTagged(zone, tagger, tagger.team)
                    # Draw a star.
                    self.netClient.interface.starGroup.star(player.rect.center)
                zone.taggedThisTime = True
                self.zonesToReset.append(zone)

    def killPlayer(self, player, killer, shot):
        '''Turns a player into a ghost at the given location, crediting the
        killer with a star'''
        if shot:
            print killer.nick + ' killed ' + player.nick
        else:
            print killer.nick + ' killed turreted player ' + player.nick + \
                  ' by tagging the zone'

        # Remove player from its zone as a living player
        player.currentZone.removePlayer(player)
        # Turn them into a ghost
        player.die()
        # Add player back to the zone as a ghost
        player.currentZone.addPlayer(player)
        if shot:
            shot.kill()

        # Draw the star animation if applicable.
        if killer.local:
            self.netClient.interface.starGroup.star(player.rect.center)

    def respawn(self, ghost, zone):
        '''Brings a player back into the land of the living'''
        # Remove player from its zone as a ghost
        ghost.currentZone.removePlayer(ghost)
        ghost.currentZone = zone
        ghost.respawn()
        print ghost.nick + ' is back in the game'
        # Add player back to the zone as a living player
        ghost.currentZone.addPlayer(ghost)

    def initiateTransaction(self, upgrade, player, stars):
      self.netClient.StartTransaction(upgrade, player, stars)

    def updateTransaction(self, team, update, numStars = None, player = None,
                          stars = None):
        if not team.currentTransaction:
            if update != 'a':
                # We need the transaction; request it.
                print 'Requested Transaction Details'
                self.netClient.requestTransactionInfo(team)
            return

        if update == 's' and not team.currentTransaction.totalStars == numStars:
            # Don't have the correct total Stars. Request transaction info
            self.netClient.requestTransactionInfo(team)
            
        if update == 's':
            team.currentTransaction.addStars(player, stars)
        if update == 'a':
            team.currentTransaction.abandon()
        if update == 'c':
            team.currentTransaction.complete()   

    def mapBlockWidth(self, blockClass):
        '''Returns the width in pixels of a map block of the given class.'''
        if issubclass(blockClass, BodyMapBlock):
            return MapLayout.zoneBodyWidth
        else:
            return MapLayout.zoneInterfaceWidth


    def completeTransaction(self, transaction):
        '''Completes the given transaction, allocating the player who purchased
        it the relevant upgrade'''
        team = transaction.team
        if team.currentTransaction == None:
            return
        team.currentTransaction.complete()
        team.currentTransaction = None
        print "Transaction Completed"

    def updateStars(self, player, stars):
        oldNum = player.stars
        diff = stars - oldNum
        player.team.updateTeamStars(diff)
        player.stars = stars
        player.updateNametag()

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

        self.shots = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.grenades = pygame.sprite.Group()
        self.drawRect = pygame.Rect(0, 0, 0, 0) # drawRect is the rect object
                                                # representing where the block
                                                # must be drawn. It is changed
                                                # by the viewManager object.
        self.drawRect.size = self.rect.size

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

    def getObstacles(self, spriteClass):
        if issubclass(spriteClass, Player):
            result = list(self.plObstacles)

            return result
        if issubclass(spriteClass, (Shot, GrenadeShot)):
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
                        self.universe.netClient.shotDestroyed(shot)
                    else:
                        self.universe.netClient.sendPlayerKilled(player, \
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
                        self.universe.netClient.sendPlayerKilled(player, \
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
    
    def moveSprite(self, sprite, deltaX, deltaY):
        '''moveSprite(sprite, deltaX, deltaY)
        Attempts to move the sprite by the specified amount, taking into
        account the positions of walls. Also checks if the sprite
        changes zones or changes map blocks.

        If the sprite is a player, checks for collisions with shots.
        If the sprite hit an obstacle, returns the obstacle.
        This routine only checks for obstacle collisions if sprite.solid() is
        True.
        Assumes that the sprite is already within this map block.
        '''
        
        lastObstacle = None
        if sprite.solid():
            # Check for collisions with obstacles.
            for obstacle in self.getObstacles(type(sprite)):
                if isinstance(sprite, Player) and sprite._ignore == obstacle:
                    continue
                dX, dY = obstacle.collide(sprite.pos, deltaX, deltaY)
                if (dX, dY) != (deltaX, deltaY):
                    # Remember the last obstacle we hit.
                    lastObstacle = obstacle
                    deltaX = dX
                    deltaY = dY

        # Check for change of map block.
        newBlock = False  # This is False because None means leaving the map.

        # Leaving via lefthand side.
        if deltaX < 0 and sprite.pos[0] + deltaX < self.pos[0]:
            # Check for collision with left-hand edge.
            y = sprite.pos[1] + deltaY * (self.pos[0] - sprite.pos[0]) / deltaX
            if self.rect.top <= y <= self.rect.bottom:
                newBlock = self.blockLeft
        if not newBlock and deltaX > 0 and sprite.pos[0] + deltaX >= \
                                       self.rect.right:
            # Check for collision with right-hand edge.
            y = sprite.pos[1] + deltaY * (self.rect.right - sprite.pos[0]) \
                            / deltaX
            if self.rect.top <= y <= self.rect.bottom:
                newBlock = self.blockRight
        if not newBlock and deltaY < 0 and sprite.pos[1] + deltaY < self.pos[1]:
            # Check for collision with top edge.
            x = sprite.pos[0] + deltaX * (self.pos[1] - sprite.pos[1]) / deltaY
            if self.rect.left <= x <= self.rect.right:
                newBlock = self.blockAbove
        if not newBlock and deltaY > 0 and sprite.pos[1] + deltaY >= \
                                        self.rect.bottom:
            x = sprite.pos[0] + deltaX * (self.rect.bottom - sprite.pos[1]) \
                            / deltaY
            if self.rect.left <= x <= self.rect.right:
                newBlock = self.blockBelow
                
        if newBlock == None and isinstance(sprite, Player) and sprite.ghost:
            return
        
        if newBlock:
            sprite.setMapBlock(newBlock)
            if isinstance(sprite, Shot):
                self.removeShot(sprite)
                newBlock.addShot(sprite)
            
            # Another map block can handle the rest of this.
            return sprite.currentMapBlock.moveSprite(sprite, deltaX, deltaY)
        
        # Check for change of zones.
        if isinstance(sprite, Player):
            newZone = self.getZoneAtPoint(sprite.pos[0] + deltaX,
                                          sprite.pos[1] + deltaY)
            if newZone != sprite.currentZone and newZone is not None:
                if self.universe.gameState == GameState.PreGame and \
                           newZone.orbOwner != sprite.team:
                    # Disallowed zone change.
                    return lastObstacle
                if not sprite.local:
                    newZone = None
            else:
                newZone = None
        else:
            newZone = None

        # Check for player/shot collisions along the path.
        if isinstance(sprite, Player):
            if sprite.local and not sprite.ghost:
                self.checkShotCollisions(sprite, deltaX, deltaY)
        elif isinstance(sprite, Shot):
            self.checkPlayerCollisions(sprite, deltaX, deltaY)
        
        # Move the sprite.
        sprite.pos = (sprite.pos[0] + deltaX,
                      sprite.pos[1] + deltaY)

        if newZone:
            # Zone needs to know which players are in it.
            sprite.changeZone(newZone)
            self.universe.netClient.sendZoneChange(sprite, newZone)

        return lastObstacle
            
    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is'''
        return

    def removeShot(self, shot):
        '''Removes a given shot from this mapBlock'''
        self.shots.remove(shot)

    def addShot(self, shot):
        '''Adds a given shot to this mapBlock'''
        if not self.shots.has(shot):
            self.shots.add(shot)

    def removeGrenade(self, grenade):
        '''Removes a given grenade from this mapBlock'''
        self.grenades.remove(grenade)

    def addGrenade(self, grenade):
        '''Adds a given grenade to this mapBlock'''
        if not self.grenades.has(grenade):
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

        
class Obstacle(object):
    '''Represents an obstacle which can't be passed by player or shot.'''
    __slots__ = ['pt1', 'deltaPt']

    def __init__(self, pt1, deltaPt):
        self.pt1 = pt1
        self.deltaPt = deltaPt

    def collide(self, pt, deltaX, deltaY):
        '''Returns how far a point-sized object at the specified position
        could travel if it were trying to travel a displacement of
        [deltaX, deltaY].
        '''

        ax, ay = self.pt1
        bx, by = pt
        dX1, dY1 = self.deltaPt

        # Check if the lines are parallel.
        denom = dX1*deltaY - deltaX*dY1
        if denom <= 1e-10:
            # We can go through it in this direction.
            return deltaX, deltaY

        # Calculate whether the line segments intersect.

        s = (deltaX * (ay-by) - deltaY * (ax-bx)) / denom
        # Take into account floating point error.
        if s < -1e-10 or s > (1.+1e-10):
            return deltaX, deltaY

        t = (dX1 * (ay-by) - dY1 * (ax-bx)) / denom
        if t < -1e-10 or t > (1.+1e-10):
            return deltaX, deltaY

        # Calculate the actual collision point.
        x = bx + t*deltaX
        y = by + t*deltaY

        # Return the allowed change in position.
        return x - pt[0], y - pt[1]

    def finalPosition(self, pt, deltaX, deltaY):
        '''Returns the final position of a point-sized object at the specified
        position which is attempting to travel along the given displacement.
        May assume that the object hits this obstacle on the way.
        If the final position is simply the collision point, should return
        None.'''
        return None
    
class JumpableObstacle(Obstacle):
    '''Represents an obstacle that is not a wall.'''

    def hitByPlayer(self, player):
        '''This obstacle has been hit by player.'''
        if player.bounce:
            player._jumpTime = player.maxJumpTime
            player.yVel = -player.yVel
            player._onGround = None
        else:
            player._jumpTime = 0
            player.yVel = 0

class GroundObstacle(JumpableObstacle):
    '''Represents an obstacle that players are allowed to walk on.'''
    drop = False
    def __init__(self, pt1, deltaPt):
        super(GroundObstacle, self).__init__(pt1, deltaPt)
        angle = atan2((deltaPt[1] + 0.), (deltaPt[0] + 0.))
        self.ratio = (cos(angle), sin(angle))
    def walkTrajectory(self, vel, deltaTime):
        '''Returns the displacement that a player would be going on this
        surface if they would travel, given an absolute velocity and an amount
        of time.'''
        return tuple([vel * deltaTime * self.ratio[i] for i in (0,1)])

    def inBounds(self, pos):
        '''Checks whether a given point is within the boundaries of this
        obstacle. Should be called by a player object who was on this piece
        of ground, and has just moved.'''
        return self.pt1[0] <= pos[0] <= self.pt1[0] + self.deltaPt[0]

class LedgeObstacle(GroundObstacle):
    drop = True
    
class RoofObstacle(Obstacle):
    def __init__(self, pt1, deltaPt):
        super(RoofObstacle, self).__init__(pt1, deltaPt)
        
    def finalPosition(self, pt, deltaX, deltaY):
        '''Returns the final position of a point-sized object at the specified
        position trying to travel a displacement of [deltaX, deltaY], given
        that it collides with this obstacle.'''
        # If an object collides with a roof obstacle while falling, it still
        #  falls.
        
        if deltaY > 0:
            # We collided with the roof while falling.
            # New position is where the roof is at the correct y-position.

            # These next few lines are just here to make sure that there's not
            # a divide by zero error:
            if deltaX == 0 or self.deltaPt[1] == 0:
                return None
            # I added a quick fix to the bug that causes an infinite loop
            # while players are touching a sloped roof, by adding 0.1 to
            # the player's position, in the direction opposite travel. Have
            # not been able to reproduce the bug since, however should be
            # looked at some more. -Ashley (Smashery)
            x = self.pt1[0] + (pt[1] + deltaY - self.pt1[1]) * \
                 self.deltaPt[0] / (0. + self.deltaPt[1]) - \
                 ((deltaX / abs(deltaX)) * 0.1)
            y = pt[1] + deltaY
            # Note: the above statement should only ever cause a division by
            #  zero if someone has been silly enough to put a piece of
            #  horizontal roof in upside down (impassable from above not below)
            return x, y

        # Normal case:
        return None

    def hitByPlayer(self, player):
        # Stop any upward motion of the player.
        player.yVel = max(player.yVel, 0)
        player._jumpTime = 0

class FillerRoofObstacle(RoofObstacle):
    '''Represents an obstacle that would be used as an obstacleEdge;
    its endpoint calculations are less precise (that being they
    don't exist), but are able to be so due to their usage.'''
    
    def finalPosition(self, pt, deltaX, deltaY):
        if self.deltaPt[0] == 0:
            return pt[0], pt[1] + (deltaY/2)
        else:
            super(FillerRoofObstacle, self).finalPosition(pt, deltaX, deltaY)

    def collide(self, pt, deltaX, deltaY):
        '''Returns how far a point-sized object at the specified position
        could travel if it were trying to travel a displacement of
        [deltaX, deltaY].
        '''
        ax, ay = self.pt1
        bx, by = pt
        dX1, dY1 = self.deltaPt

        # Check if the lines are parallel.
        denom = dX1*deltaY - deltaX*dY1
        if denom <= 0:
            # We can go through it in this direction.
            return deltaX, deltaY

        # Calculate whether the line segments intersect.

        s = (deltaX * (ay-by) - deltaY * (ax-bx)) / denom
        # Take into account floating point error.
        if s <= 0 or s >= 1:
            return deltaX, deltaY

        t = (dX1 * (ay-by) - dY1 * (ax-bx)) / denom
        if t < -1e-10 or t > (1.+1e-10):
            return deltaX, deltaY

        # Calculate the actual collision point.
        x = bx + t*deltaX
        y = by + t*deltaY

        # Return the allowed change in position.
        return x - pt[0], y - pt[1]

class VerticalWall(JumpableObstacle):
    '''Represents a vertical wall that players can cling to and climb.'''
    drop = True
    
    def __init__(self, pt1, deltaPt):
        assert deltaPt[0] == 0

        # Can drop off a vertical wall, so drop is always set to True
        super(VerticalWall, self).__init__(pt1, deltaPt)

class ZoneDef(object):
    '''Stores static information about the zone.
    
    Attributes:
        adjacentZones - set of adjacent ZoneDef objects
        id - the zone id (TODO: remove the need for this at this level)
        initialOwner - the team that initially owned this zone,
            represented as a number (0 for neutral, 1 or 2 for a team).
        pos - the coordinates of this zone in the map
    '''
    def __init__(self, id, initialOwner, xCoord, yCoord):
        self.adjacentZones = set()
        self.id = id
        self.initialOwner = initialOwner
        self.pos = xCoord, yCoord

class ZoneState(object):
    '''Represents information about a given zone and its state.

    Attributes:
        universe
        zoneOwner - a team
        orbOwner - a team
        players - a Group
        nonPlayers - a Group for ghosts
        taggedThisTime - boolean flag used to compare whether multiple players have tagged the zone in one tick
        turretedPlayer - None or a Player

    Attributes which should (eventually) be completely migrated to the zoneDef:
        id
    '''

    def __init__(self, universe, zoneDef):
        self.defn = zoneDef
        self.id = zoneDef.id

        universe.zoneWithDef[zoneDef] = self
        
        self.universe = universe
        self.zoneOwner = zoneDef.initialOwner
        self.orbOwner = zoneDef.initialOwner
        self.players = pygame.sprite.Group()

        # zone.nonPlayers are those players that do not count in zone
        # calculations, such as ghosts and decoys
        self.nonPlayers = pygame.sprite.Group()
        self.taggedThisTime = False
        self.turretedPlayer = None
        
    def __repr__(self):
        # Debug: uniquely identify this zone within the universe.
        if self.id == None:
            return 'Z---'
        return 'Z%3d' % self.id
        
    def tag(self, team, player):
        '''This method should be called by netClient when the orb in this
        zone is tagged'''
        
        # Inform the team objects
        if self.orbOwner:
            self.orbOwner.orbLost()
        if team:
            team.orbGained()

            
        if team == None:
            self.orbOwner = None
            self.zoneOwner = None
            print 'Zone %s neutralised' % (self.id,)
        else:
            print '%s tagged Zone %s' % (player.nick, self.id)
            self.orbOwner = team
            allGood = True
            for zoneDef in self.defn.adjacentZones:
                zone = self.universe.zoneWithDef[zoneDef]
                if zone.orbOwner == team:
                    # Allow the adjacent zone to check if it is entirely
                    # surrounded by non-enemy zones
                    zone.checkAgain()
                elif zone.orbOwner == None:
                    pass
                else:
                    allGood = False
            if allGood:
                self.zoneOwner = team
            else:
                self.zoneOwner = None
        self.universe.netClient.interface.gameInterface.reDraw()

        
    def checkAgain(self):
        '''This method should be called by an adjacent friendly zone that has
        been tagged and gained. It will check to see if it now has all
        surrounding orbs owned by the same team, in which case it will
        change its zone ownership.'''

        # If the zone is already owned, ignore it
        if self.zoneOwner != self.orbOwner and self.orbOwner != None:
            for zoneDef in self.defn.adjacentZones:
                zone = self.universe.zoneWithDef[zoneDef]
                if zone.orbOwner == self.orbOwner \
                   or zone.orbOwner == None:
                    pass
                else:
                    # Found an enemy orb.
                    break
            else:
                # Change zone ownership to orb ownership.
                self.zoneOwner = self.orbOwner

    def checkMore(self, team):
        '''In the event that a zone is tagged by a team, this procedure is
        called to see if the opposing team also tags the orb.'''

        xCoord1, yCoord1 = self.defn.pos
        tagDistance = 30
        for player in self.players.sprites():
            if player.team == team:
                xCoord2, yCoord2 = player.pos
                distance = ((xCoord1 - xCoord2) ** 2 + \
                            (yCoord1 - yCoord2) ** 2) ** 0.5
                if distance < tagDistance:
                    return True
        return False
        
    def removePlayer(self, player):
        '''Removes a player from this zone'''
        if player.ghost:
            self.nonPlayers.remove(player)
        else:
            self.players.remove(player)

    def addPlayer(self, player):
        '''Adds a player to this zone'''
        if player.ghost:
            if not self.nonPlayers.has(player):
                self.nonPlayers.add(player)
        else:
            if not self.players.has(player):
                self.players.add(player)

    def getBackgroundColour(self):
        if self.zoneOwner:
            return self.zoneOwner.backgroundColour
        else:
            return neutral_bg

    def getOrbImage(self):
        if self.orbOwner:
            return self.orbOwner.orbImage
        else:
            return self.universe.neutralOrb

    def getMiniMapColour(self):
        if self.zoneOwner:
            return self.orbOwner.miniMapZoneOwnColour
        elif self.orbOwner:
                return self.orbOwner.miniMapOrbOwnColour
        else:
            return (224, 208, 224)
        
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

class Sprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.pos = (0, 0)

    def setMapBlock(self, block):
        '''Called when the sprite changes from one map block to another.'''
        self.currentMapBlock = block

    def solid(self):
        raise NotImplementedError, 'Sprite.solid() not implemented.'
    
class Player(Sprite):
    '''Maintains the state of a player. This could be the user's player, a
    player on the network, or conceivably even a bot.

    If this player is controlled locally (human or bot), then player.local
    is True. If the player is controlled by the network, player.local is False.
    '''

    # These parameters are used to create a canvas for the player sprite object.
    canvasSize = (33, 39)
    colourKey = (255, 255, 255)

    def __init__(self, universe, nick, team, id, zone, dead = False):
        '''Note that player instances are not local when they are created.
        The value of local is set only when the server gives us the player
        by calling self.makeLocal().'''
        Sprite.__init__(self)
        
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
        self.distanceToTarget = None        # Used in owned players by viewMan
        self._faceRight = True
        self.reloadTime = 0.0
        self.turretHeat = 0.0
        self.respawnGauge = 0.0
        self.upgradeGauge = 0.0
        self.upgradeTotal = 0.0
        self.ghost = dead
        self.upgrade = None
        self.shielded = False
        self.phaseshift = False
        self.turret = False
        self.turretOverHeated = False
        self.shots = {}

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
        
        # TODO: turret stuff
        standingImage = makeImage('Legs-S0.png')
        jumpingImage = makeImage('Legs-R3.png')
        # Create an image for myself.
        gunImages = AngledImageCollection(self, *gunImages)
        turretBaseImage = SingleImage(turretBaseImage)

        bodyImage = SingleImage(bodyImage)

        holdImage = SingleImage(holdImage)
        headImage = SingleImage(headImage)
        teamImage = SingleImage(self.team.image)

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
        
        # Create a nametag.
        self.nametag = NameTag(self.nick)
        self.starTally = StarTally(0)
        
        self.currentZone = zone
        zone.addPlayer(self)
        
        # Add self to the universe.
        universe.newPlayer(self)

    def __repr__(self):
        return self.nick

    def detailString(self):
        toReturn = repr(struct.unpack('B', self.id)[0]) + " "
        toReturn += self.nick
        if self.ghost:
            toReturn += " (D)"
        
        if self.stars:
            toReturn += " " + repr(self.stars) + " star"
            if self.stars != 1:
                toReturn += "s"
        
        if self.upgrade:
            toReturn += " Upgr: " + repr(self.upgrade)
        
        return toReturn

    def removeFromGame(self):
        '''Called by network client when server says this player has left the
        game.'''
        # Remove myself from the register of players.
        if self.team.currentTransaction:
            self.team.currentTransaction.removeStars(self)
        if self.upgrade:
            self.upgrade.clientDelete()
        self.universe.delPlayer(self)
        
        # Remove myself from all groups I'm in.
        self.kill()
        
        

    def makeLocal(self):
        'Called by network client at instruction of server.'
        self.local = True
        
    def solid(self):
        return not self.ghost
    
    def setMapBlock(self, block):
        self.currentMapBlock.players.remove(self)
        Sprite.setMapBlock(self, block)
        block.players.add(self)
            
        # If we're changing blocks, we can't hold on to the same obstacle.
        self._onGround = None

    def setToNoState(self):
        '''Sets a player's state to all False. Should be called when the
        current game loses focus (such as a menu being put up)'''
        for state in self._state:
            self._state[state] = False
        # Let the network know:
        if self.local:
            self.universe.netClient.sendPlayerUpdate(self)
    
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
            self.universe.netClient.sendPlayerUpdate(self)

    def lookAt(self, angle, dist=None):
        '''Changes the direction that the player is looking.  angle is in
        radians and is measured clockwise from the right.'''
        if dist:
            self.distanceToTarget = dist * 0.4
        
        if self.angleFacing == angle:
            return
        
        self.angleFacing = angle
        tempBool = self._faceRight
        self._faceRight = angle > 0
        if tempBool != self._faceRight and self.local:
            self.universe.netClient.sendPlayerUpdate(self)
            

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
                        #self.universe.showMessage("Turret overheated", colours.turretOverheated)
                        
                elif self.currentZone.zoneOwner == self.team:
                    self.reloadTime = self.ownReloadTime
                    
                elif self.currentZone.zoneOwner == None:
                    self.reloadTime = self.neutralReloadTime
                    
                else:
                    self.reloadTime = self.enemyReloadTime
                self.universe.netClient.sendShotFired(self, self.turret)
            
    def setImage(self, moving, slow):
        flip = None
        if self.ghost:
            blitImages = self.ghostAnimation
        elif self.turret:
            blitImages = self.turretAnimation
        elif self._onGround:
            if isinstance(self._onGround, VerticalWall):
                blitImages = self.holdingAnimation
                if self._onGround.deltaPt[1] < 0:
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
            if self.yVel > 0:
                blitImages = self.fallingAnimation
            else:
                blitImages = self.jumpingAnimation
        self.image.fill(self.image.get_colorkey())
        # Put the pieces together:
        for element in blitImages:
            self.image.blit(element.getImage(), (0,0))
        if self.shielded:
            self.image.blit(self.shieldAnimation.getImage(), (0,0))
        if self.phaseshift and not defines.useAlpha:
            self.image.blit(self.phaseShiftAnimation.getImage(), (0,0))
        if not self._faceRight and flip == None or flip:
            self.image = pygame.transform.flip(self.image, True, False)
        # Flicker the sprite between different levels of transparency
        if defines.useAlpha:
            if self.local and self.phaseshift:
                self.image.set_alpha(random.randint(30, 150))
            elif self.ghost:
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)
            
    
    def update(self, deltaT):
        '''Called by this player's universe when this player should update
        its position. deltaT is the time that's passed since its state was
        current, measured in seconds.'''
        slow = False

        # Update upgrade gauge based on Time:
        if self.upgrade:
            self.upgradeGauge -= deltaT
                
        #########
        # GHOST #
        #########
        if self.ghost:
            deltaX = self.maxGhostVel * deltaT * sin(self.angleFacing)
            deltaY = -self.maxGhostVel * deltaT * cos(self.angleFacing)

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
                #self.universe.showMessage("Turret back online", (0, 0, 255))

                
        ##########
        # PLAYER #
        ##########
        else:
            
            # Consider horizontal movement of player.
            if self._state['left'] and not self._state['right']:
                if self._faceRight:
                    slow = True
                    absVel = -self.slowXVel
                else:
                    slow = False
                    absVel = -self.xVel
            elif self._state['right'] and not self._state['left']:
                if self._faceRight:
                    slow = False
                    absVel = self.xVel
                else:
                    slow = True
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
        
        # Now update the player's image - draw a line to indicate angle.
        self.setImage(not (self._state['left'] or self._state['right']), slow)
        '''pygame.draw.line(self.image, (0,0,0), centre,
                         (centre[0] + 20*sin(self.angleFacing),
                          centre[1] - 20*cos(self.angleFacing)), 3)'''                  

    def _move(self, deltaX, deltaY):
        '''Called by the player's update() routine to move the player a given
        distance. This method should check for collisions with bullets and the
        ground.'''
        # For a ghost:
        if self.ghost:
                # TODO: Check for smaller resulting deltaX and deltaY due
                #  to hitting the edge of the map.
                self.currentMapBlock.moveSprite(self, deltaX, deltaY)
                if self.respawnGauge > 0:
                    distanceTravelled = ((deltaX ** 2) + (deltaY ** 2)) ** 0.5
                    self.respawnGauge -= distanceTravelled / self.respawnMovementValue
        # For a player:
        else:
                
            while True:
                # Check for collisions with solid objects, and change of zone.
                obstacle = self.currentMapBlock.moveSprite(self, deltaX, deltaY)
                if obstacle:
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
        self.universe.netClient.interface.playerDied(self)

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
        self.universe.netClient.interface.playerRespawned(self)
        
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

    def requestUpgrade(self, upgradeClass, getStars):
        '''Called by the menu when wanting to purchase an upgrade'''
        upgrade = upgradeClass
        if self.team.currentTransaction != None:
            raise MenuError, "Transaction already in play"
        
        elif self.upgrade != None:
            raise MenuError, "You already have an upgrade"
        
        elif self.team.teamStars < upgrade.requiredStars:
            raise MenuError, "Your team has insufficient stars"
        
        elif self.ghost:
            raise MenuError, "You are dead! Can't purchase an upgrade"
        
        else:
            getStars("How many stars to contribute from the start?",
                     self.GetUpgrade, upgrade)
            

    def GetUpgrade(self, stars, upgrade):
        '''Actually does the transaction-starting'''
        try:
            startingStars = int(stars)
        except:
            raise MenuError, "Please enter a valid value"
        else:
            if startingStars > self.stars:
                raise MenuError, "You do not have that many stars"
            else:
                self.universe.initiateTransaction(upgrade, self, startingStars)

    def addStars(self, getStars):
        '''Called when the user requests to add stars to a transaction'''
        
        if not self.team.currentTransaction:
            raise MenuError, "No transaction to add stars to"
        else:
            getStars("How many stars to contribute?",
                     self.addStarsNow)
            

    def addStarsNow(self, stars):
        '''Actually requests the star-adding'''
        if not stars or not self.team.currentTransaction:
            return
        try:
            numStars = int(stars)
        except:
            raise MenuError, "Please enter a numerical value"
        else:
            if numStars + self.team.currentTransaction.getNumStars(self) > self.stars:
                raise MenuError, "You do not have that many stars"
            else:
                self.universe.netClient.addStars(self.team, self, numStars)

    def requestUse(self):
        if not self.upgrade:
            raise MenuError, "You have no upgrade to use"
        elif self.upgrade.inUse:
            raise MenuError, "Your upgrade is already in use"
        else:
            self.upgrade.requestUse()
            self.upgradeGauge = self.upgradeTotal = self.upgrade.timeRemaining
            self.universe.netClient.interface.upgradeUsed(self)

    def requestRespawn(self):
        '''Called by the menu when a player wishes to respawn'''
        if not self.ghost:
            pass
        elif self.respawnGauge > 0:
            raise MenuError, "Not able to respawn yet"
        elif self.currentZone.orbOwner != self.team:
            raise MenuError, "Not in a friendly Zone"
        else:
            self.universe.netClient.sendPlayerRespawn(self)

    def abandon(self):

        if self.upgrade:
            self.universe.netClient.upgradeDelete(self)
        elif self.team.currentTransaction and \
             self.team.currentTransaction.purchasingPlayer == self:
            self.universe.netClient.abandonTransaction(self.team)

class GrenadeShot(Sprite):
    '''This will make the grenade have the same physics as a player without control
    and features of player movement'''

    # The following values control grenade movement.
    maxFallVel = 540            # pix/s
    gravity = 1000 #3672              # pix/s/s
    initYVel = -400
    initXVel = 200

    def __init__(self, universe, player, id):
        Sprite.__init__(self)
        self.image = makeImage('grenade.bmp')
        self.universe = universe
        self.player = player
        self.id = id
        self.local = False
        
        # Place myself.
        self.pos = player.pos
        self.yVel = self.initYVel


        # Select x velocity
        if player._faceRight:
            self.xVel = self.initXVel
        else:
            self.xVel = -self.initXVel

        print self.xVel

        self.rect = self.image.get_rect()
        universe.grenades.add(self)

        try:
            self.currentMapBlock = player.currentMapBlock
            self.currentMapBlock.addGrenade(self)
        except IndexError:
            logging.writeException()
            print "Init: Grenade off map"
            self.kill()
            return

    def delete(self):
        self.universe.grenades.remove(self)
        self.kill()

    def solid(self):
        return True
    
    def setMapBlock(self, block):
        self.currentMapBlock.grenades.remove(self)
        Sprite.setMapBlock(self, block)
        block.grenades.add(self)
              
    
    def update(self, deltaT):
        '''Called by this player's universe when this player should update
        its position. deltaT is the time that's passed since its state was
        current, measured in seconds.'''
        slow = False

        try:
            deltaX = self.xVel * deltaT
            deltaY = self.yVel * deltaT
            
            while True:
                # Check for collisions with solid objects, and change of zone.

                obstacle = self.currentMapBlock.moveSprite(self, deltaX, deltaY)

                
                if obstacle:

                    # Ask obstacle where the player should end up.
                    targetPt = obstacle.finalPosition(self.pos, deltaX, deltaY)
                    
                    if targetPt == None:
                        break

                    deltaX = targetPt[0] - self.pos[0]
                    deltaY = targetPt[1] - self.pos[1]
                    
                else:
                    break


            if obstacle:
                # Hit an obstacle. Process change to velocity etc.
                if obstacle:
                   self.yVel = -self.yVel

            
            # v = u + at
            vFinal = self.yVel + self.gravity * deltaT
            if vFinal > self.maxFallVel:
                # Hit terminal velocity. Fall has two sections.
                deltaY = deltaY + (self.maxFallVel**2 - self.yVel**2) \
                         / (2 * self.gravity) + self.maxFallVel * (deltaT - \
                         (self.maxFallVel - self.yVel) / self.gravity)
                self.yVel = self.maxFallVel
            else:
                # Simple case: s=ut+0.5at**2
                deltaY = deltaY + self.yVel * deltaT + 0.5 * self.gravity * \
                         deltaT ** 2
                self.yVel = vFinal
        
        except:
            logging.writeException()


class Shot(Sprite):
    '''Represents a shot fired by a player. Shots are created by the universe
    object when it receives word from the networkClient object.'''
    
    # Speed that shots travel at.
    speed = 600       # pix/s
    lifetime = 1.    # s
    
    def __init__(self, id, team, pos, angle, player, turret):
        Sprite.__init__(self)

        self.id = id
        self.team = team
        self.image = team.shotImage
        self.pos = tuple(pos)
        self.angle = angle
        self.originatingPlayer = player
        self.vel = (self.speed * sin(angle),
                    -self.speed * cos(angle))
        self.rect = self.image.get_rect()
        self.timeLeft = self.lifetime
        self.turretShot = turret

        self.originatingPlayer.addShot(self)
        
        i, j = MapLayout.getMapBlockIndices(self.pos[0], self.pos[1])
        try:
            self.currentMapBlock = self.originatingPlayer.universe.zoneBlocks[i][j]
            self.originatingPlayer.universe.zoneBlocks[i][j].addShot(self)
        except IndexError:
            logging.writeException()
            print "Init: Shot off map"
            self.kill()
            return

    def solid(self):
        return not self.turretShot
    
    def update(self, deltaT):
        '''Called by the universe when this shot should update its position.
        deltaT is the time that's passed since its state was current, measured
        in seconds.'''
        # Shots have a finite lifetime.
        self.timeLeft = self.timeLeft - deltaT
        if self.timeLeft <= 0:
            self.kill()

        # Remember where the shot was - this is so that collisions with path
        # of shot work.
        self.oldPos = self.pos
        
        delta = (self.vel[0]*deltaT,
                 self.vel[1]*deltaT)
        try:
            if self.currentMapBlock.moveSprite(self, *delta):
                # Shot hit an obstacle.
                self.kill()
        except AttributeError:
            print "Update: Shot off map"
            print MapLayout.getMapBlockIndices(self.pos[0], self.pos[1])
            self.kill()

    def kill(self):
        self.originatingPlayer.destroyShot(self.id)
        super(Shot, self).kill()

            
        

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
