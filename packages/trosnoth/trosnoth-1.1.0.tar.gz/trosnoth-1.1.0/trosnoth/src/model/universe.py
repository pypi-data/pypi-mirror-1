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

from twisted.internet import reactor
import pygame

import trosnoth
from trosnoth.src.utils.utils import timeNow
import trosnoth.src.utils.logging as logging
import trosnoth.src.model.modes as modes
from trosnoth.src.model.universe_base import GameState

# TODO: Colours should not be in model
from trosnoth.src.trosnothgui.ingame.colours import *
from trosnoth.src.gui.framework.utils import makeImage
from trosnoth.src.trosnothgui.ingame.nametag import NameTag

from trosnoth.data import fonts, getPath

# TODO; remove isinstances so we can remove some of these:
from trosnoth.src.model.obstacles import *
from trosnoth.src.model.mapblocks import MapBlockDef
from trosnoth.src.model.map import MapLayout, MapState
from trosnoth.src.model.shot import Shot, GrenadeShot
from trosnoth.src.model.player import Player
from trosnoth.src.model.team import Team

from trosnoth.src.utils.event import Event

# Component message passing
from trosnoth.src.utils.components import Component, handler, Plug
from trosnoth.src.messages.chat import *
from trosnoth.src.messages.connection import *
from trosnoth.src.messages.game import *
from trosnoth.src.messages.gameplay import *
from trosnoth.src.messages.players import *
from trosnoth.src.messages.shot import *
from trosnoth.src.messages.transactions import *


# FIXME: there's the potential for some things to require an interface
# before it is created (such as using a transaction)

# TODO: Get this GUI stuff out of model
def init():
    '''Initialises anything that's needed by this module. This function should
    only be called after pygame.init() and after the video mode has been set.'''
    # Load the name font.
    pygame.font.init()
    NameTag.nameFont = pygame.font.Font(getPath(fonts, 'FreeSans.ttf'), 20)

            
class Universe(Component):
    '''Universe(halfMapWidth, mapHeight)
    Keeps track of where everything is in the level, including the locations
    and states of every alien, the terrain positions, and who owns the
    various territories and orbs.'''

    # The size of players and shots.
    halfPlayerSize = (10, 19)
    halfShotSize = (5, 5)

    actionPlug = Plug()    

    def __init__(self, halfMapWidth, mapHeight):
        '''
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

        super(Universe, self).__init__()
        # Initialise
        self.gameState = GameState.PreGame
        self.startTime = 0
        self.zonesToReset = []
        self.playerWithId = {}
        self.teamWithId = {'\x00' : None}

        # Create Teams:
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
##        else:
##            # This universe will not actually be displayed (created by server)
##            self.teams = (Team(colours.team1bg,
##                               colours.team1msg,
##                               None,
##                               'A'),
##                          Team(colours.team2bg,
##                               colours.team2msg,
##                               None,
##                               'B'))
##            
        Team.setOpposition(self.teams[0], self.teams[1])
        
        for t in self.teams:
            self.teamWithId[t.id] = t

        self.onZoneTagged = Event()
        self.onPlayerKilled = Event()
        self.onShotDestroyed = Event()
        self.onShotFired = Event()
        self.onZoneChanged = Event()
        self.onPlayerUpdate = Event()
        self.onPlayerRespawn = Event()
        self.onUpgradeReqUse = Event()
        self.onUpgradeUsed = Event()
        self.onAbandonTransaction = Event()
        self.onUpgradeReqDel = Event()
        self.onUpgradeDestroyed = Event()
        self.onGrenadeExploded = Event()
        self.onTurretBegin = Event()
        self.onTurretEnd = Event()
        self.onMinimapBegin = Event()
        self.onMinimapEnd = Event()

        self.onShotKill = Event()
        self.onGrenadeKill = Event()
        self.onGrenadeExists = Event()
        
                
        # Set up zones
        self.zoneWithDef = {}
        self.map = MapState(self, halfMapWidth, mapHeight)
        self.zoneWithId = self.map.zoneWithId
        self.zones = self.map.zones
        self.zoneBlocks = self.map.zoneBlocks

        self.players = set()
        self.grenades = set()
        # TODO: could make shots iterate directly over the player objects rather than storing twice
        # (redundancy - potential inconsistencies)
        self.shots = set()
        self.gameOverTime = None
        self.gameModeController = modes.GameMode(Shot, Player, GrenadeShot)

    def setGameMode(self, mode):
        try:
            getattr(self.gameModeController, mode)()
            print 'Client: GameMode is set to ' + mode
        except AttributeError:
            print 'No such gameMode'
        except TypeError:
            print 'No such gameMode'

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


    def gameOver(self):
        self.gameOverTime = timeNow()
        self.gameState = GameState.Ended

    def gameStart(self, time):
        if self.gameState == GameState.PreGame:
            self.gameDuration = time
            self.startTime = timeNow()
            self.gameState = GameState.InProgress

    def addPlayer(self, nick, team, playerId, zone, dead = True):
        
        player = Player(self, nick, team, playerId, zone,
                        dead = True)

        #Add this player to this universe.
        self.players.add(player)
        self.playerWithId[playerId] = player

        # Make sure player knows its zone
        i, j = MapLayout.getMapBlockIndices(*player.pos)
        try:
            player.currentMapBlock = self.zoneBlocks[i][j]
        except IndexError:
            logging.writeException()
            raise IndexError, 'player start position is off the map'
        
        self.actionPlug.send(AddPlayer(player))

    def delPlayer(self, player):
        '''Removes the specified player from this universe. Should be called
        by the network client when the server sends an appropriate message.'''
        self.players.remove(player)
        try:
            del self.playerWithId[player.id]
        except KeyError:
            logging.writeException()
            pass
        
    def tick(self, deltaT):
        '''Advances all players and shots to their new positions.'''
        # Update the player and shot positions.
        update = lambda item: item.update(deltaT)
        map(update, list(self.shots))
        map(update, list(self.players))
        map(update, list(self.grenades))

        # Tell the network about tagged zones
        for zone in self.zonesToReset:
            zone.taggedThisTime = False
        self.zonesToReset = []

    def validateTurretVal(self, player, turretVal):
        return player.turret == turretVal

    def shotFired(self, id, team, pos, angle, player, turret, ricochet):
        '''This should be called by the networkClient object when the server
        indicates that a player has fired a shot.'''
        #assert self.validateTurretVal(player, turret)
        
        self.shots.add(Shot(id, team, pos, angle, player, turret, ricochet))

    def removeShot(self, shot):
        try:
            self.shots.remove(shot)
        except KeyError:
            logging.writeException()

    def shotWithId(self, pId, sId):
        try:
            return self.playerWithId[pId].shots[sId]
        except:
            logging.writeException()
            return None


        
    def checkTag(self, tagger):
        '''Checks to see if the player has touched the orb of its currentZone
        If so, it fires the onTagged event'''

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
            for player in zone.players:
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
                        self.onZoneTagged.execute(zone, None, None)
                else:
                    # This team is the only to have tagged it
                    self.onZoneTagged.execute(zone, tagger, tagger.team)

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


    def respawn(self, ghost, zone):
        '''Brings a player back into the land of the living'''
        # Remove player from its zone as a ghost
        ghost.currentZone.removePlayer(ghost)
        ghost.currentZone = zone
        ghost.respawn()
        print ghost.nick + ' is back in the game'
        # Add player back to the zone as a living player
        ghost.currentZone.addPlayer(ghost)

    def validateTransaction(self, team, update, numStars):
        if (not team.currentTransaction and update != 'a') or \
           (update == 's' and not team.currentTransaction.totalStars == numStars):
            print 'DEBUG: Invalid Transaction'
            print team.currentTransaction
            print update
            if team.currentTransaction:
                print team.currentTransaction.totalStars, numStars
            return False
        return True

    
    def addStarsToTransaction(self, team, player, stars):
        team.currentTransaction.addStars(player, stars)

    def abandonTransaction(self, team):        
        team.currentTransaction.abandon()

    def completeTransaction(self, team):
        team.currentTransaction.complete()   

    def mapBlockWidth(self, blockClass):
        '''Returns the width in pixels of a map block of the given class.'''
        if issubclass(blockClass, BodyMapBlock):
            return MapLayout.zoneBodyWidth
        else:
            return MapLayout.zoneInterfaceWidth


    def completeTransaction(self, team):
        '''Completes the team's transaction, allocating the player who purchased
        it the relevant upgrade'''
        if team.currentTransaction == None:
            return
        team.currentTransaction.complete()
        team.currentTransaction = None
        print 'Transaction Completed'

    def updateStars(self, player, stars):
        oldNum = player.stars
        diff = stars - oldNum
        player.team.updateTeamStars(diff)
        player.stars = stars
        player.updateNametag()

    def addGrenade(self, grenade):
        self.grenades.add(grenade)

    def removeGrenade(self, grenade):
        self.grenades.remove(grenade)

