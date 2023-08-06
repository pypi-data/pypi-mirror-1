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

import struct
import random
import marshal
import pickle
import sys
import os
import base64
import time
from math import pi

from trosnoth.src.utils.jsonImport import json

from twisted.internet.protocol import Factory, DatagramProtocol
from twisted.internet.error import CannotListenError
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet import reactor, task

from trosnoth.src.network import netmsg
from trosnoth.src.network.setup import *
from trosnoth.src.network.players import *
from trosnoth.src.network.game import *
from trosnoth.src.network.shot import *
from trosnoth.src.network.chat import *
from trosnoth.src.network.validation import *
from trosnoth.src.network.gameplay import *
from trosnoth.src.network.map import *
from trosnoth.src.network.transactions import *
from trosnoth.src.network.utils import *

from trosnoth.src.network.networkDefines import *

from trosnoth.src.gui import app
from trosnoth.src import serverUniverse, serverLayout
from trosnoth.src.model import upgrades
from trosnoth.src.model.universe_base import GameState
from trosnoth.src.model.upgrades import upgradeNames, Grenade
from trosnoth.src.utils import logging
from trosnoth.src.utils.event import Event
from trosnoth.src.utils.unrepr import unrepr
from trosnoth.src.utils.utils import timeNow
from trosnoth.src.model.transaction import TransactionState, ServerTransaction

from trosnoth.data import getPath, user, makeDirs

REJOIN_DELAY_TIME = 8.1

# The set of messages that the client expects to receive.
serverMsgs = netmsg.MessageCollection(
    # trosnoth.src.network.players
    JoinRequestMsg,
    LeaveRequestMsg,

    # trosnoth.src.network.game
    SetCaptainMsg,
    TeamIsReadyMsg,

    # trosnoth.src.network.shot 
    FireShotMsg,
    GrenadeExplodedMsg,

    # trosnoth.src.network.chat
    ChatMsg,

    # trosnoth.src.network.gameplay
    KillingMsg,
    KillShotMsg,
    PlayerUpdateMsg,
    TaggingZoneMsg,
    RespawnMsg,
    ZoneChangeMsg,

    # trosnoth.src.network.validation
    RequestPlayersMsg,
    RequestZonesMsg,
    RequestStarsMsg,
    RequestUpgradesMsg,
    RequestTransactionMsg,
    RequestUDPStatusMsg,

    # trosnoth.src.network.transactions
    StartingTransactionMsg,
    DeleteUpgradeMsg,
    AddingStarsMsg,
    AbandonTransactionMsg,
    UseUpgradeMsg,

    # trosnoth.src.network.map
    RequestMapBlock,

    # trosnoth.src.network.setup
    ReadyForDynamicDetailsMsg,
)

class Profanity(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ServerCommandInterface(object):
    
    def __init__(self, server):
        self.server = server

    def setGameMode(self, gameMode):
        return self.server.setGameMode(gameMode)

    def kickPlayer(self, playerId):
        self.server.kick(playerId)

    def endGame(self, team):
        if team == 'blue':
            self.server.gameOver(self.server.world.teams[0])
        elif team == 'red':
            self.server.gameOver(self.server.world.teams[1])
        elif team == 'draw':
            self.server.gameOver()

    def startGame(self):
        self.server.world.gameStart()

    def noCaptains(self):
        self.server.disableCaptains()

    def setTeamName(self, teamNumber, teamName):
        if teamNumber in (0, 1):
            team = self.server.world.teams[teamNumber]
            self.server.changeTeamName(team, teamName)

    def setTeamLimit(self, newLimit):
        if newLimit >= 1 and newLimit < 128:
            self.server.changeTeamLimit(newLimit)

    def shutdown(self):
        self.server.shutdown()

    def getGameState(self):
        currentGameState = self.server.world.gameState
        if currentGameState == GameState.PreGame:
            return 'P'
        if currentGameState == GameState.InProgress:
            return 'I'
        if currentGameState != GameState.Ended:
            return '?'
        
        winningTeam = self.server.world.winner
        if winningTeam is None:
            return 'D'
        if winningTeam.id < winningTeam.opposingTeam.id:
            return 'B'
        return 'R'

    def getOrbCounts(self):
        return (
            self.server.world.teams[0].numOrbsOwned,
            self.server.world.teams[1].numOrbsOwned
        )

    def getTeamNames(self):
        return (
            self.server.world.teams[0].teamName,
            self.server.world.teams[1].teamName
        )
        
    def getGameMode(self):
        return self.server.world.gameMode

class ServerNetHandler(object):
    '''
    A network message handler designed for use with trosnoth.network.netman.
    '''
    greeting = 'Trosnoth1'
    messages = serverMsgs

    # Ping time is for player update messages.
    pingTime = 0.75

    def __init__(self, netman, alias, settings):
        self.netman = netman
        self.alias = alias
        self.settings = settings

        # Initialise state variables.
        self.connectedClients = {}      # connId -> IP addr
        self.lastPlayerId = 41

        self.noCaptains = False     # Does not allow captains - start from server interface.

        self.playerConn = {}            # playerId -> connId
        self.players = {}               # connId -> [playerId]

        # Initialize the statistics
        self._initStats()
        
        self.onShutdown = Event()       # ()
        self._alreadyShutdown = False

        # delayData is used to ensure clients don't rejoin too soon.
        self.delayData = {}

        # Server identification string.
        self.serverString = alias + ' - ' + time.asctime()
        
        # Set up the protocols for the game.
        self.cmdInterface = ServerCommandInterface(self)

        self._initSettings(settings)

        self.initWorld()

        # Initialize the stats / replay file
        self._initGameFile()

        # Autostart if need be.
        if self.settings['beginNow']:
            self.world.gameStart()
        del self.settings['beginNow']

        self.running = True

        # Register with the network manager.
        netman.addHandler(self)

    #########################
    # Private set-up methods
    #########################

    def _initStats(self):
        self.stats = {}
        self.streaks = {}
        self.statTimers = {}
        
        # A: Recorded [A]ll game (including post-round)
        # G: Recorded during the main [G]ame only
        # P: Recorded [P]ost-Game only
        temp = {'kills': 0,           # G Number of kills they've made
                'deaths': 0,          # G Number of times they've died
                'zoneTags': 0,        # G Number of zones they've tagged
                'zoneAssists': 0,     # G Number of zones they've been in when their team tags it
                'shotsFired': 0,      # A Number of shots they've fired
                'shotsHit': 0,        # A Number of shots that have hit a target
                'starsEarned': 0,     # G Aggregate total of stars earned
                'starsUsed': 0,       # G Aggregate total of stars used
                'starsWasted': 0,     # G Aggregate total of stars died with
                'roundsWon': 0,       # . Number of rounds won
                'roundsLost': 0,      # . Number of rounds lost

                'killsAsRabbit': 0,   # P Number of kills they've made as a rabbit
                'rabbitsKilled': 0,   # P Number of rabbits they've killed

                'playerKills': {},    # A Number of kills against individual people
                'playerDeaths': {},   # A Number of deaths from individual people
                'upgradesUsed': {},   # G Number of each upgrade used
                
                'timeAlive': 0.0,     # G Total time alive
                'timeDead': 0.0,      # G Total time dead
                'timeRabbit': 0.0,    # P Total time alive as a rabbit

                'killStreak': 0,      # G Number of kills made without dying
                'tagStreak': 0,       # G Number of zones tagged without dying
                'aliveStreak': 0.0,   # G Greatest time alive in one life
                'rabbitStreak': 0.0,  # P Greatest time alive as a rabbit
                }

        # 'temp' is used to preserve horizontal screen real estate above.
        self.statList = temp

        # Streak trackers
        self.streakMapping = {'kills': 'killStreak',
                              'zoneTags': 'tagStreak',
                              'timeAlive': 'aliveStreak',
                              'timeRabbit': 'rabbitStreak',
                             }
        self.streakList = {}
       
        for streakName in self.streakMapping.values():
            self.streakList[streakName] = 0

        # Timer trackers
        self.statTimerList = {'timeAlive': None,
                              'timeDead': None,
                              'timeRabbit': None,
                             }

    def _initSettings(self, settings):
        # Set up the settings for this server   
        self.settings = defaultSettings.copy()
        self.settings.update(settings)

        # Error check the settings.
        if self.settings['maxPlayers'] > 128:
            raise ValueError, 'maxPlayers cannot exceed 128 (per team)'
        if self.settings['mapHeight'] <= 0:
            raise ValueError, 'mapHeight must be 1 or more'
        if self.settings['halfMapWidth'] <= 0:
            raise ValueError, 'halfMapWidth must be 1 or more'

        if self.settings['recordReplay'] == True:
            self.recordReplay = True
            self.replayData = []
        else:
            self.recordReplay = False

        if self.settings['teamNames']:
            self.changeTeamName(self.world.teams[0], settings['teamNames'][0][0:maxTeamNameLength])
            self.changeTeamName(self.world.teams[1], settings['teamNames'][1][0:maxTeamNameLength])

    def _initGameFile(self):
        # Check if the json library is available
        if json is None:
            print "WARNING: your version of Python does not have the json"
            print "or simplejson libraries installed. You will be unable"
            print "to save replays or statistics."
            self.recordReplay = False
            self.fileUpdate = None
            return

        # Figure out the filename to use for the main file        
        filename = self.alias + ' (0).trosgame'
        gamePath = getPath(user, 'savedGames')
        makeDirs(gamePath)
        filePath = os.path.join(gamePath, filename)
        copyCount = 0
        while os.path.exists(filePath):
            copyCount += 1
            filename = "%s (%s).trosgame" % (self.alias, str(copyCount))
            filePath = os.path.join(gamePath, filename)

        baseFilename = filename[:-9]
        self.gameFilename = filePath

        # Figure out the filename to use for the stat file
        filename = baseFilename + '.trosstat'
        statPath = getPath(user, 'savedGames', 'statistics')
        makeDirs(statPath)
        filePath = os.path.join(statPath, filename)
        copyCount = 0
        while os.path.exists(filePath):
            copyCount += 1
            filename = '%s (%s).trosstat' % (baseFilename, str(copyCount))
            filePath = os.path.join(statPath, filename)

        self.statFilename = filePath

        # Get all required server information
        serverInformation = {}
        serverInformation['serverName'] = self.alias
        serverInformation['dateTime'] = ",".join( map(str,time.localtime()) )
        serverInformation['serverVersion'] = serverVersion
        serverInformation['gameDataProtocol'] = gameDataProtocol
        serverInformation['serverSettings'] = self.settings
        serverInformation['unixTimestamp'] = "%#.3f" % timeNow()
        serverInformation['statsSaved'] = True
        serverInformation['statsLocation'] = self.statFilename
        serverInformation['replaySaved'] = self.recordReplay

        # Special processing for connection string.
        clientSettings = unrepr(self.getClientSettings())

        # Since the settings are going to be saved to a file, repr() the
        # map information, since otherwise the JSON output will use a
        # ridicuously large number of lines.
        clientSettings['worldMap'] = repr(clientSettings['worldMap'])
        clientSettings['layoutDefs'] = repr(clientSettings['layoutDefs'])
        serverInformation['connectionString'] = clientSettings

        self.serverInformation = serverInformation

        # Update the data file every 5 seconds
        self.fileUpdate = task.LoopingCall(self.writeGameData)
        self.fileUpdate.start(5, False)

    def initWorld(self):
        '''Uses self.settings to set up the universe information.'''
        
        # Create a universe object.
        self.world = serverUniverse.Universe(self, \
                                             self.settings['gameDuration'])
        
        # Initialise layout database.
        self.layoutDatabase = serverLayout.LayoutDatabase()
        
        for zone in self.world.zones: 
            zone.mapBlockList = [] 
        
        # Let each zone know which blocks contain it
        for blockList in self.world.zoneBlocks:
            for block in blockList:
                block.tempBlocked = False
                zones = block.Zones()
                for zone in zones:
                    zone.mapBlockList.append(block)
                    
        # Set a proportion (50%) of the connections to blocked

        blockRatio = 0.5
        x = -1
        for blockList in self.world.zoneBlocks:
            x += 1
            for i in range(len(blockList) / 2 + 1):
                block = blockList[i]
                oppBlock = block.oppositeBlock

                # If the block is on the edge, leave it as is
                if block.blocked:
                    continue
                # If the block is outside the confines of where the player can
                # go
                elif len(block.Zones()) == 0:
                    continue
                else:
                    # If it's a topBodyMapBlock, make it the same as the
                    # bottomBodyMapBlock just above it
                    if isinstance(block, serverUniverse.TopBodyMapBlock):
                        block.tempBlocked = block.blockAbove.tempBlocked
                    elif random.random() < blockRatio:
                        block.tempBlocked = True
                        if oppBlock:
                            oppBlock.tempBlocked = True

        # At this point, many of the blocks will probably be connected to all
        # others. However, we shall now ensure that all are connected, using
        # the following method:
        # 
        # 
        # 1. Find the central zone of the entire map. Use this as a starting
        # point.
        # 
        # 2. Create a list of connected zones. At first, the list should only
        # contain the central zone.
        # 
        # 3. Create an empty list of unconnected but adjacent zones.
        # 
        # 4. For each zone next to the central zone, if it is blocked, add it to
        # the list of unconnected but adjacent zones. Otherwise, add it to the
        # list of connected zones. However, ignore zones on the right-hand side
        # of the map.
        # 
        # 5. Repeat step 4 for each of the zones that was just added to the
        # list of connecteds. If ever a zone is added to the list of connecteds,
        # be sure to remove it from the list of unconnected-but-adjacent-zones
        # (if it exists in that list).
        # 
        # 6. Choose a random zone from the list of unconnected and adjacent
        # zones. Connect it to a random zone in the list of connecteds
        # (obviously one to which it is adjacent). Remove it from the list
        # of unconnecteds, and add it to the list of connecteds.
        # 
        # 7. While the list of unconnecteds is not empty, repeat steps 4-6,
        # using this newly connected zone in place of the central zone.

        
        centralRow = self.world.zoneBlocks[len(self.world.zoneBlocks)/2 + 1]
        centralBlock = centralRow[len(centralRow) / 2]
        centralZone = centralBlock.zone

        # lastId will be the largest zone ID that will be accepted; beyond that,
        # they must be on the right hand side of the map. Therefore, lastId
        # must be the ID of the bottom-most zone of the central column.
        btmRow = self.world.zoneBlocks[len(self.world.zoneBlocks) - 1]
        cntrBlk = btmRow[len(btmRow) / 2]
        lastId = cntrBlk.zone.id

        connecteds = []
        newlyConnected = [centralZone]
        unconnecteds = {}

        

        # This exterior loop will be broken out of if, at the end, the list
        # of unconnecteds is empty.
        while True:
            # Go through each of the newly connected zones.
            while len(newlyConnected) != 0:
                aZone = newlyConnected.pop()
                # print "Looking at " + repr(aZone)
                # raw_input("Press enter")
                for adjZone in aZone.adjacentZones:

                    if adjZone.id > lastId:
                        # This zone is on the right hand side of the map.
                        # Ignore it.
                        continue
                    if connecteds.__contains__(adjZone) or \
                       newlyConnected.__contains__(adjZone):
                        # Have already looked at this zone. Ignore it.
                        continue

                    upDown = 0
                    # Special case: if the mapHeight is 1, then it messes up
                    # the calculations for which zones are on top of which.
                    # However, if adjZone is in the middle column, as long
                    # is the middle column is of height 3 (i.e. halfMapWidth
                    # is even), then it will not be an issue.
                    if self.settings['mapHeight'] == 1 and \
                       not (self.settings['halfMapWidth'] % 2 == 0 and \
                            adjZone.id > lastId - 3):
                        
                        if adjZone.id % 3 == 2 and \
                           adjZone.id - aZone.id == 1:
                            # adjZone is just below aZone
                            upDown = 1
                            # print "%d is below %d" % (adjZone.id, aZone.id)
                        
                        elif adjZone.id % 3 == 1 and \
                             adjZone.id - aZone.id == -1:
                            # adjZone is just above adjZone
                            upDown = -1
                            # print "%d is below %d" % (aZone.id, adjZone.id)
                        else:
                            # print "%d is beside %d" % (adjZone.id, aZone.id)
                            pass

                    elif adjZone.id - aZone.id == 1:
                        # adjZone is just below aZone
                        upDown = 1
                        
                    elif adjZone.id - aZone.id == -1:
                        # adjZone is just above adjZone
                        upDown = -1
                        
                    for block in adjZone.mapBlockList:
                        if upDown == 1:
                            if isinstance(block, serverUniverse.TopBodyMapBlock):
                                
                                connect = not block.tempBlocked
                                break
                        elif upDown == -1:
                            if isinstance(block, serverUniverse.BottomBodyMapBlock):
                                connect = not block.tempBlocked
                                break
                        elif block.Zones().__contains__(aZone):
                            connect = not block.tempBlocked
                            break

                    # The two zones have an open connection.
                    if connect:
                        # print "Turns out " + repr(adjZone) + " is connected to " + repr(aZone) + " at block " + repr(block)
                        newlyConnected.append(adjZone)
                        try:
                            del unconnecteds[adjZone]
                        except KeyError:
                            pass
                        
                    # They have a closed connection.
                    else:
                        if not unconnecteds.has_key(adjZone):
                            unconnecteds[adjZone] = [aZone]
                        else:
                            unconnecteds[adjZone].append(aZone)

                            
                connecteds.append(aZone)

            # At this stage, all zones connected to the central one are in the
            # connecteds list.
            if len(unconnecteds) == 0:
                # All zones are connected.
                break

            # There must be unconnected zones left.

            # Choose a random element from unconnecteds
            connectZone = random.sample(unconnecteds, 1)[0]
            connectTo = random.choice(unconnecteds[connectZone])

            # Find the mapBlock(s) to unblock, and unblock it/them

            upDown = 0
            if self.settings['mapHeight'] == 1 and \
               not (self.settings['halfMapWidth'] % 2 == 0 and \
                    connectZone.id > lastId - 3):
                
                if connectZone.id % 3 == 2 and \
                   connectZone.id - connectTo.id == 1:
                    # connectZone is just below connectTo
                    upDown = 1
                
                elif connectZone.id % 3 == 1 and \
                     connectZone.id - connectTo.id == -1:
                    # connectZone is just above adjZone
                    upDown = -1
            elif connectZone.id - connectTo.id == 1:
                # connectZone is just below connectTo
                upDown = 1
                
            elif connectZone.id - connectTo.id == -1:
                # connectZone is just above connectZone
                upDown = -1

            for block in connectZone.mapBlockList:
                if upDown == 1:
                    if isinstance(block, serverUniverse.TopBodyMapBlock):
                        block.tempBlocked = False
                        block.blockAbove.tempBlocked = False
                        break
                elif upDown == -1:
                    if isinstance(block, serverUniverse.BottomBodyMapBlock):
                        block.tempBlocked = False
                        block.blockBelow.tempBlocked = False
                        break
                elif block.Zones().__contains__(connectTo):
                    block.tempBlocked = False
                    break

            newlyConnected.append(connectZone)
            del unconnecteds[connectZone]
            # print repr(connectZone) + " connected to " + repr(connectTo)
            # print "Still Unconnected: ", unconnecteds
        
        # Populate the map blocks with appropriate obstacles.

        for blockList in self.world.zoneBlocks:
            for i in range(len(blockList) / 2 + 1):
                block = blockList[i]
                oppBlock = block.oppositeBlock
                if not block.blocked:
                    block.blocked = block.tempBlocked
                    if not oppBlock == None:
                        oppBlock.blocked = oppBlock.tempBlocked
                if not block.Zones() == []:
                    # If the block contains zones, get a layout for this block.
                    self.layoutDatabase.randomiseBlock(block)
        i = 0
        for blockList in self.world.zoneBlocks:
            i += 1
            j = -1
            for block in blockList:
                j+= 1
                del block.tempBlocked
                del block.oppositeBlock
                
        for zone in self.world.zones:
            del zone.mapBlockList

    ###############################
    # Interface to network manager
    ###############################

    def newConnection(self, connectionId, ipAddr, port):
        '''
        Called by the network manager when a new incoming connection is
        completed.
        '''
        print 'Server: a client has connected.'

        # Send the setting information.
        self.netman.sendTCP(connectionId,
                InitClientMsg(self.getClientSettings()))

        # Remember that this connection's ready for transmission.
        self.connectedClients[connectionId] = ipAddr
        self.players[connectionId] = set()

    def connectionComplete(self, connectionId):
        '''
        Called by the network manager when a connection initiated by this
        handler is completed.
        '''
        # This should never actually happen as no connections are attempted.
        print 'Server: Very unexpected connection event 1'

    def connectionFailed(self, connectionId):
        '''
        Called by the network manager when an attempt to connect fails.
        '''
        # This should never actually happen as no connections are attempted.
        print 'Server: Very unexpected connection event 2'

    def receiveMessage(self, connectionId, msg):
        '''
        Called by the network manager when a message is received on this
        connection.
        '''
        msgType = type(msg).__name__

        # Try to find a procedure to process this mesasge type.
        try:
            proc = getattr(self, 'receive%s' % (msgType,))
        except AttributeError:
            # Unexpected message type for this connection.
            self.receiveUnhandledMessage(msgType)
            return
            
        try:
            # Call the processing for this message.
            proc(connectionId, msg)
        except:
            # So that receiving a network message will never cause a crash.
            logging.writeException()

    def receiveBadString(self, connectionId, line):
        '''
        Called by the network manager when an unrecognised string is received
        on this connection.
        '''
        # Log the error.
        print 'Server: Unrecognised network data: %r' % (line,)
        print '      : Did you invent a new network message and forget to'
        print '      : add it to trosnoth.networkServer.serverMsgs?'

    def connectionLost(self, connectionId):
        '''
        Called by the network manager when a connection is lost.
        '''

        if connectionId in self.connectedClients:
            # Record time of disconnection to enforce delay before rejoin.
            ipAddr = self.connectedClients[connectionId]
            self.delayData[ipAddr] = timeNow()

            # Go through the players owned by this connection.
            del self.connectedClients[connectionId]
            for pId in self.players[connectionId]:
                self.removePlayer(pId)

            del self.players[connectionId]
            print 'Server: lost a client connection'

        # Check for game over and no connectios left.
        if len(self.connectedClients) == 0 and self.world.gameState == GameState.Ended:
            # Shut down the server.
            print 'Server: Last client connection lost after end of game: shutting down.'
            self.shutdown()

    ######################
    # Game data recording
    ######################

    def writeGameData(self):
        try:
            self._writeGameData()
        except app.ApplicationExit:
            raise
        except:
            print 'UNHANDLED ERROR IN writeGameData()'
            print
            logging.writeException()
        
    def _writeGameData(self):
        if json is None:
            return

        gameFile = file(self.gameFilename, 'w')
        statFile = file(self.statFilename, 'w')

        # Generate the server information
        self.serverInformation['saveDateTime'] = ",".join( map(str,time.localtime()) )
        serverInfoString = json.dumps(self.serverInformation, indent = 4)
        infoLines = serverInfoString.count("\n") + 1

        # Generate the statistics file
        statsString = json.dumps(self.stats, indent = 4, sort_keys = True)
        statsLines = statsString.count("\n") + 1

        # Generate the replay data
        if self.recordReplay:
            replayString = "\n".join(self.replayData)
            replayLines = replayString.count("\n") + 1
        else:
            replayLines = 0

        # Create the File Information String
        fileInfoString = ",".join((gameDataProtocol, str(infoLines),
                str(replayLines)))

        # Write everything to file
        print >> gameFile, fileInfoString
        print >> gameFile, serverInfoString
        print >> statFile, statsString

        if self.recordReplay:
            print >> gameFile, replayString

        gameFile.flush()
        gameFile.close()

    def replayAppend(self, datagram, protocol):
        if self.recordReplay:
            datagram = base64.b64encode(datagram)
            string = "ReplayData: %#.3f %s %s" % (timeNow(), protocol, datagram)
            self.replayData.append(string)

    #############
    # Statistics
    #############

    def addPlayerToStats(self, ipAddr, nick):
        if ipAddr not in self.stats:
            self.stats[ipAddr] = {}
            self.streaks[ipAddr] = {}
            self.statTimers[ipAddr] = {}
        if nick not in self.stats[ipAddr]:         
            self.stats[ipAddr][nick] = self.statList.copy()
            self.streaks[ipAddr][nick] = self.streakList.copy()
            self.statTimers[ipAddr][nick] = self.statTimerList.copy()

    def addStat(self, statName, ipAddr, nick, increase = 1, enemy = None):
        if self.statList[statName] is not None:
            if enemy is None:
                self.stats[ipAddr][nick][statName] += increase
                if statName in self.streakMapping:
                    self.streaks[ipAddr][nick][self.streakMapping[statName]] += increase
            else:
                if enemy not in self.stats[ipAddr][nick][statName]:
                    self.stats[ipAddr][nick][statName][enemy] = 0
                    
                self.stats[ipAddr][nick][statName][enemy] += increase

    def updateStreaks(self, ipAddr, nick):
        '''This method will update the appropriate stats for the specified
        player if their current streak is larger than their recorded streak.
        Their current streak will then be reset to zero.'''
        for streakName in self.streakList:
            if self.statList[streakName] is not None:
                if self.streaks[ipAddr][nick][streakName] > self.stats[ipAddr][nick][streakName]:
                    self.stats[ipAddr][nick][streakName] = self.streaks[ipAddr][nick][streakName]

                self.streaks[ipAddr][nick][streakName] = 0

    def updateTimer(self, statName, ipAddr, nick, delete = False, totalDelete = False):
        if self.statList[statName] is not None:
            if totalDelete:
                self.statTimers[ipAddr][nick][statName] = None
                return
            
            if self.statTimers[ipAddr][nick][statName] is None:
                if delete:
                    return
                self.statTimers[ipAddr][nick][statName] = time.time()
            else:
                oldTime = self.statTimers[ipAddr][nick][statName]
                difference = time.time() - oldTime
                self.addStat(statName, ipAddr, nick, difference)
                if delete:
                    self.statTimers[ipAddr][nick][statName] = None
                else:
                    self.statTimers[ipAddr][nick][statName] = time.time()

    ################
    # Other methods
    ################

    def getClientSettings(self):
        '''Returns a string representing the settings which must be sent to
        clients that connect to this server.'''

        result = {
            'serverVersion': serverVersion,
            'serverString': self.serverString,
        }

        # 1. Settings the client needs to know from self.settings.
        for k in ('halfMapWidth', 'mapHeight'):
            result[k] = self.settings[k]

        # 3. Give the client the world.
        worldMap = []
        layouts = {}
        for row in self.world.zoneBlocks:
            curRow = []
            for block in row:
                if block.layout is None:
                    curRow.append(-1)
                else:
                    layoutNum = layouts.setdefault(block.layout.forwardLayout, \
                                                   len(layouts))
                    curRow.append((layoutNum, block.layout.reverse))
            worldMap.append(curRow)

        layoutDefs = [None] * len(layouts)
        for l, i in layouts.iteritems():
            layoutDefs[i] = (l.filename, l.checksum)

        result['worldMap'] = worldMap
        result['layoutDefs'] = layoutDefs

        result['teamName0'] = self.world.teams[0].teamName
        result['teamName1'] = self.world.teams[1].teamName

        result['replay'] = False

        if self.world.gameState == GameState.PreGame:
            result['gameState'] = "PreGame"
        elif self.world.gameState == GameState.InProgress:
            result['gameState'] = "InProgress"
        else:
            result['gameState'] = "Ended"

        if self.world.gameState == GameState.InProgress:
            result['timeRunning'] = timeNow() - self.world.currentTime
            result['timeLimit'] = self.world.gameTimeLimit

        return repr(result)
            
    def removePlayer(self, pId):
        '''Signal that player has been removed.'''
        self.broadcastTcp(RemovePlayerMsg(pId))

        # FIXME: There should never be a KeyError here.
        try:
            player = self.world.playerWithId[pId]
        except KeyError:
            print >> sys.stderr, 'DelP KeyError'
            return
        
        isCaptain = False
        if player.team.isCaptain(player):
            isCaptain = True
        player.team.leave(player)
        if isCaptain:
            self.captainGone(player.team)
        # Stop the pinging of the player.
        if player.reCall is not None:
            player.reCall.cancel()
        
        # Free this player id.
        del self.playerConn[pId]
        del self.world.playerWithId[pId]


    def broadcastTcp(self, msg):
        'Sends the specified message to all clients.'

        # Add the line to the replay file
        self.replayAppend(msg.pack(), 'T')

        for connectionId in self.connectedClients:
            self.netman.sendTCP(connectionId, msg)
            
    def broadcastUdp(self, msg, team=None, nonSending=None):
        '''Sends the specified packet to all clients.'''
        packet = msg.pack()

        # Add the packet to the replay file
        # The replay doesn't seem to like this and it looks like taking it
        # out doesn't present any problems
        if not packet.startswith('ZnCh'):
            self.replayAppend(packet, 'U')
        
        if team is not None:
            # FIXME: this will send to a client twice if there are two players
            # on that one client
            for connId in team.connIds.values():
                if connId != nonSending:
                    self.netman.send(connId, msg)
        else:
            for connId in self.connectedClients:
                if connId != nonSending:
                    self.netman.send(connId, msg)

    def receiveUnhandledMessage(self, msgType):
        # Log the occurrence.
        print 'Server: No handler for %s message' % (msgType,)

    def receiveReadyForDynamicDetailsMsg(self, connId, msg):
        self.sendAllValidation(connId)

    def receiveRequestMapBlock(self, connId, msg):
        layout = self.layoutDatabase.layoutsByFilename[msg.filename]
        filepath = os.path.join(layout.path, layout.filename)
        if (os.path.exists(filepath) and os.path.exists(layout.graphicPath)):
            fMapBlock = open(filepath, 'r')
            contents = fMapBlock.read()
            self.netman.sendTCP(connId, MapBlockMsg(msg.missingID, contents))
            fGraphic = open(layout.graphicPath, 'rb')
            graphicContents = fGraphic.read()
            self.netman.sendTCP(connId, MapBlockGraphicsMsg(msg.missingID,
                    graphicContents))
        else:
            # TODO
            pass

    def receiveJoinRequestMsg(self, connId, msg):
        # FIXME: do it per team
        # Check if we can add another player.
        team = self.world.teamWithId[msg.teamId]
     
        # Too many players, or game ended. Send response.
        if len(team.connIds) >= self.settings['maxPlayers']:
            self.netman.sendTCP(connId, 
                    CannotCreatePlayerMsg('F', msg.teamId, nick=msg.nick))
            return
        elif self.world.gameState == GameState.Ended:
            self.netman.sendTCP(connId,
                    CannotCreatePlayerMsg('O', msg.teamId, nick=msg.nick))
            return

        ipAddr = self.connectedClients[connId]
        # Except in test mode, clients can't rejoin immediately.
        if not self.settings['testMode']:
            try:
                leftTime = self.delayData[ipAddr]
            except KeyError:
                pass
            else:
                timeLeft = REJOIN_DELAY_TIME - (timeNow() - leftTime)
                if timeLeft > 0:
                    self.netman.sendTCP(connId,
                            CannotCreatePlayerMsg('W', msg.teamId, timeLeft, msg.nick))
                    print 'Player blocked from joining; needs to wait ' + str(timeLeft) + ' seconds'
                    return
            
        # Create a player id.
        playerId = self.newPlayerId(connId)
        
        # Select a random zone belonging to that team.
        zone = self.world.getRandomZone(team)

        # First tell everyone that a new player has been added.
        self.broadcastTcp(AddPlayerMsg(playerId, msg.teamId, zone.id, msg.nick))
        
        # Now tell this client that it owns the player.
        self.netman.sendTCP(connId, GivePlayerMsg(playerId))
        
        team.addAddress(playerId, connId)

        self.validateTransaction(team, connId)
        player = serverUniverse.Player(self.world, team, msg.nick.decode(), playerId, \
                                       zone)
        # Start the pinging in 5 seconds the first time; should give them
        # time to receive other messages.
        player.reCall = reactor.callLater(5, self.pingForUpdate, \
                                      player, connId)

        nick = msg.nick.decode()
        self.addPlayerToStats(ipAddr, nick)

        # Just in case there are left-over streaks or timers from the player
        for statName in self.statTimerList:
            self.updateTimer(statName, ipAddr, nick, totalDelete = True)
        self.updateStreaks(ipAddr, nick)
        
        
    def receiveLeaveRequestMsg(self, connId, msg):
        # Check that the player exists.
        try:
            if self.playerConn[msg.playerId] == connId:
                self.removePlayer(msg.playerId)
        except KeyError:
            # Unrecognised player id.
            pass

    def newPlayerId(self, connId):
        '''Creates a new single-character player id.'''

        pId = struct.pack('B', self.lastPlayerId)
        while self.playerConn.has_key(pId):
            self.lastPlayerId = (self.lastPlayerId + 1) % 256
            pId = struct.pack('B', self.lastPlayerId)

        self.playerConn[pId] = connId
        self.players[connId].add(pId)
        return pId

    def receiveRequestTransactionMsg(self, connId, msg):
        team = self.world.teamWithId[msg.teamId]
        self.validateTransaction(team, connId)

    def receiveGrenadeExplodedMsg(self, connId, msg):
        player = self.world.playerWithId[msg.playerId]
        def mkMsg(angle):
            sId = player.newShotId()
            self.broadcastUdp(ShotFiredMsg(msg.playerId, sId, angle,
                    msg.xpos, msg.ypos, 'G'))
            serverUniverse.Shot(sId, player.team, (msg.xpos, msg.ypos), angle, player, \
                                True, False)

        # Fire shots.
        for x in range(0, Grenade.numShots):
            angle = pi*(2*random.random() - 1.0)  # In range (-pi, pi)
            mkMsg(angle)

    def receiveFireShotMsg(self, connId, msg):
        '''Called when a Fire Shot request is received from a client'''
        
        player = self.world.playerWithId[msg.playerId]
        if player.dead:
            # A dead player wants to shoot.
            self.validatePlayers(connId)
            return

        # Validate position.
        try:
            pos = (msg.xpos, msg.ypos)
            i, j = self.world.getMapBlockIndices(*pos)
            block = self.world.zoneBlocks[i][j]
        except IndexError:
            print "Server: Shot off the map"
            return

        sId = player.newShotId()
        type = msg.type
        if player.turret:
            type = 'T'
        elif player.hasRicochet:
            type = 'R'
        turret = type in 'TG'
        ricochet = type == 'R'

        ipAddr = self.connectedClients[connId]
        self.broadcastUdp(ShotFiredMsg(msg.playerId, sId, msg.angle,
                msg.xpos, msg.ypos, type))
        serverUniverse.Shot(sId, player.team, pos, msg.angle, player, \
                            turret, ricochet)
        self.addStat('shotsFired', ipAddr, player.nick)

    def receiveKillingMsg(self, connId, msg):
        '''Received from a client when a player local to it has died'''
        try:
            player = self.world.playerWithId[msg.targetId]
            killer = self.world.playerWithId[msg.killerId]

            victimIP = self.connectedClients[self.playerConn[msg.targetId]]
            killerIP = self.connectedClients[self.playerConn[msg.killerId]]
                
            shot = killer.shots[msg.shotId]
            if player.killable():
                starsBefore = killer.stars
                victimStars = player.stars
                player.killed(killer)
                starsAfter = killer.stars
                if self.world.gameState == GameState.Ended:
                    if killer.team == self.world.winner:
                        self.addStat('rabbitsKilled', killerIP, killer.nick)
                        self.updateTimer('timeRabbit', victimIP, player.nick, delete = True)
                    else:
                        self.addStat('killsAsRabbit', killerIP, killer.nick)
                else:
                    self.addStat('starsWasted', victimIP, player.nick, victimStars)

                    self.addStat('kills', killerIP, killer.nick)
                    self.addStat('deaths', victimIP, player.nick)

                    self.updateTimer('timeAlive', victimIP, player.nick, delete = True)
                    self.updateTimer('timeDead', victimIP, player.nick)

                    self.updateStreaks(victimIP, player.nick)

                    if starsAfter > starsBefore:
                        self.addStat('starsEarned', killerIP, killer.nick)

                self.addStat('shotsHit', killerIP, killer.nick)
                self.addStat('playerKills', killerIP, killer.nick, enemy = player.nick)
                self.addStat('playerDeaths', victimIP, player.nick, enemy = killer.nick)
                             
                self.broadcastUdp(KilledMsg(msg.targetId, msg.killerId,
                        msg.shotId, msg.xPos, msg.yPos, killer.stars))

                if player.team.currentTransaction and \
                   player.team.currentTransaction.purchasingPlayer == player:
                    self.sendTransactionUpdate(player.team, 'a')
                killer.destroyShot(msg.shotId)
            elif player.dead:
                self.validatePlayers(connId)
            elif player.turret or player.shielded:
                self.validateUpgrades(connId)
                self.sendShotDestroyed(msg.killerId, msg.shotId)
                shot.shotDead()
                self.addStat('shotsHit', killerIP, killer.nick)
                if player.shielded:
                    player.upgrade.serverDelete()
                    self.broadcastUdp(DeleteUpgradeMsg(msg.targetId))
                    
        except KeyError:
            # One or more of those things doesn't exist on the server
            # So just don't do anything
            pass
        
    def receiveKillShotMsg(self, connId, msg):
        '''Received in the event that a shot is destroyed other than by hitting
        a player, an obstacle, or by existing too long'''
        # If the shot exists, rebroadcast the message
        shot = self.world.shotWithId(msg.playerId, msg.shotId)
        if shot:
            # Ensure the shot exists
            shooterIP = self.connectedClients[self.playerConn[msg.playerId]]
            shooter = self.world.playerWithId[msg.playerId]
            self.addStat('shotsHit', shooterIP, shooter.nick)
            shot.shotDead()
            self.broadcastUdp(msg)

    def sendShotDestroyed(self, pId, sId):
        self.broadcastUdp(KillShotMsg(pId, sId))

    def receivePlayerUpdateMsg(self, connId, msg):
        # The message is rebroadcast unchanged
        try:
            player = self.world.playerWithId[msg.playerId]
        except KeyError:
	    # TODO: Some sensible processing of this error.
            print >> sys.stderr, 'playerUpdate KeyError'
            return
    
        if player.reCall is not None:
            player.reCall.cancel()
        player.reCall = reactor.callLater(self.pingTime, self.pingForUpdate,
                player, connId)
        
        values = list(expand_boolean(getattr(msg, 'keys')))
        hasUpgrade = values[4]
        ghost = values[5]
        
        if ghost != player.dead:
            # Client is incorrect about their own life situation. 
            self.validatePlayers(connId)

            # Correct the message
            values[4] = player.dead

        # Check that upgrade status is correct.
        if (hasUpgrade and player.upgrade is None) or \
                (player.upgrade is not None and not hasUpgrade):
            self.validateUpgrades(connId)
            print 'Upgrade Wrong for %s' % (player.nick,),
            if hasUpgrade:
                print '(should have upgrade)'
            else:
                print '(should not have upgrade)'

            values[5] = (player.upgrade is not None)

        # Update the contents of the message
        msg.keys = str(compress_boolean(tuple(values)))

        # Broadcast this update.
        self.broadcastUdp(msg)

    def pingForUpdate(self, player, connId):
        '''
        Pings a client; asking for an update for a particular player
        '''
        player.reCall = reactor.callLater(self.pingTime, self.pingForUpdate,
                                          player, connId)
        self.netman.send(connId, RequestPlayerUpdateMsg(player.id))

    def pingForZone(self, player):
        '''Asks a player for what zone they are in.'''
        # Find the address to send it to:
        connId = self.playerConn[player.id]
        self.netman.sendMessage(connId, RequestZoneUpdateMsg(player.id))

    def receiveTaggingZoneMsg(self, connId, msg):
        '''Called when a client says that a player has tagged a zone'''
        wasInProgress = self.world.gameState == GameState.InProgress

        # Check zone ownership.
        zone = self.world.zoneWithId[msg.zoneId]
        # TODO: remove the team attribute from the network message, since it's
        # derivable from player anyway
        team = self.world.teamWithId[msg.teamId]

        # Check player status.
        player = self.world.playerWithId[msg.playerId]
        if player.dead or player.phaseshift:
            # It seems to think that it's alive or not with a phase shift
            self.validatePlayers(connId)
            return
        
        if not zone.canBeTaggedBy(player):
            # The player may have incorrect data; send
            # all data pertaining to zones, to that client.
            self.validateZones(connId)
            return
        

        
        # Check if it kills a turret.
        turretPlayer = zone.turretedPlayer
        turret = turretPlayer is not None
        if turret:
            turretId = turretPlayer.id
        else:
            turretId = '\x00'

        # Perform the tag.
        starsBefore = player.stars
        
        zone.tag(player)

        # Get team's new orb count and player's new star count.
        if team is None:
            teamOrbCount = 0
        else:
            teamOrbCount = team.numOrbsOwned
        playerStarCount = player.stars

        # Update statistics appropriately.
        ipAddr = self.connectedClients[connId]
        # We checked earlier, because this tag could have ended the game, and so should
        # count.

        try:
            if wasInProgress:
                self.addStat('zoneTags', ipAddr, player.nick)
                if playerStarCount > starsBefore:
                    self.addStat('starsEarned', ipAddr, player.nick)

                # Award zone assists to other players in the zone
                for zonePlayer in zone.players:
                    if (zonePlayer.team == player.team and
                            zonePlayer.id != player.id):
                        self.addStat('zoneAssists', 
                                self.connectedClients[self.playerConn[
                                zonePlayer.id]], zonePlayer.nick)

                if turret:
                    turretIP = self.connectedClients[self.playerConn[
                            turretPlayer.id]]
                    self.addStat('starsWasted', turretIP, turretPlayer.nick,
                            turretPlayer.stars)
        except:
            # Don't let errors in statistics distrupt the game.
            logging.writeException()

        # Send the message.
        msg = TaggedZoneMsg(msg.zoneId, msg.playerId, msg.teamId,
                teamOrbCount, playerStarCount, turret, turretId)
        self.broadcastUdp(msg)

    def receiveRespawnMsg(self, connId, msg):
        if self.world.gameState == GameState.PreGame:
            return

        player = self.world.playerWithId[msg.playerId]
        zone = self.world.zoneWithId[msg.zoneId]
        if zone.orbOwner == player.team:
            # Ensure they're recorded as being in the right zone
            player.changeZone(zone)
            player.respawn()
            self.broadcastUdp(msg)

            if self.world.gameState == GameState.InProgress:
                ipAddr = self.connectedClients[connId]
                self.updateTimer('timeAlive', ipAddr, player.nick)
                self.updateTimer('timeDead', ipAddr, player.nick, delete = True)
        else:
            # client has incorrect information: send them zone information
            self.validateZones(connId)

    def receiveStartingTransactionMsg(self, connId, msg):
        team = self.world.teamWithId[msg.teamId]
        if team.currentTransaction is not None:
            # They must not know that there's already a transaction in play.
            self.validateTransaction(team, connId)
        
        else:
            player = self.world.playerWithId[msg.playerId]
            if player.upgrade:
                # That player already has an upgrade. They cannot start a
                # new transaction
                self.validateUpgrades(connId)
            else:
                upgrade = upgrades.upgradeOfType[msg.upgradeType]
                try:
                    trans = ServerTransaction(team, player, upgrade)

                    # Be alerted when the transaction state changes:
                    d = {TransactionState.Completed : 'c',
                         TransactionState.Abandoned : 'a'}
                    def TransactionStateChanged(trans, state):
                        self.sendTransactionUpdate(trans.purchasingTeam, d[state])
                    trans.onStateChanged.addListener(TransactionStateChanged)
                    
                    trans.addStars(player, msg.numStars)
                    
                    # Be alerted when the number of stars changes:
                    def NumStarsChanged(trans, player, stars):
                        self.sendTransactionUpdate(trans.purchasingTeam,'s', player, stars)
                    trans.onNumStarsChanged.addListener(NumStarsChanged)
                        
                    # It may not be open, because it may have been completed in one go.
                    if trans.state == TransactionState.Open:
                        self.broadcastUdp(StartedTransactionMsg(msg.teamId,
                                msg.playerId, msg.numStars, msg.upgradeType,
                                trans.timeLimit))
                    
                except ValueError:
                    # Client must not have valid star counts
                    self.validateStars(connId)

    def receiveAddingStarsMsg(self, connId, msg):
        # The message is not re-broadcast. The transaction itself manages
        # rebroadcasting the message with correct values.
        team = self.world.teamWithId[msg.teamId]
        transaction = team.currentTransaction
        if transaction is None:
            # They think there's a transaction when there's not.
            # Tell them to abandon it.
            self.sendTransactionUpdate(team, 'a', connId = connId)
            # Also, since they probably missed the 'Transaction Complete'
            # message they may have incorrect details about stars and
            # players' upgrades. Send that too.
            self.validateStars(connId)
            self.validateUpgrades(connId)
            return
        player = self.world.playerWithId[msg.playerId]
        transaction.addStars(player, msg.numStars)

    def receiveAbandonTransactionMsg(self, connId, msg):
        # FIXME: do a check to make sure it is the purchasingPlayer
        # that abandons?
        
        team = self.world.teamWithId[msg.teamId]
        transaction = team.currentTransaction
        transaction.abandon()
            
    def sendTransactionUpdate(self, team, update, player = None,
                              stars = None, connId = None):
        '''Should be called with update being:
        'a': abandon transaction
        'c': complete transaction
        's': add stars to transaction
        (removing stars from a transaction is done automatically client-side)'''
        
        transaction = team.currentTransaction
        tId = team.id
        if update == 's':
            msg = AddedStarsMsg(team.id, player.id, stars, transaction.totalStars)
            
        elif update == 'a':
            msg = AbandonTransactionMsg(team.id)
            
            # Send the message to everyone, not just the team.
            team = None

        elif update == 'c':
            # Transaction is complete: send all contribution
            # data to ensure everyone has correct info about it.
            msg = TransactionCompleteMsg(team.id,
                    transaction.purchasingPlayer.id,
                    transaction.upgrade.upgradeType)
                             
            # Update clients on new number of stars each player has.
            # TODO: This should be implemented as client-side calcluations.
            self.validateStars()

            # Record the stats.
            for player in transaction.contributions.iterkeys():
                stars = transaction.contributions[player]
                contributor = self.world.playerWithId[player.id]

                ipAddr = self.connectedClients[self.playerConn[player.id]]
                if self.world.gameState == GameState.InProgress:
                    self.addStat('starsUsed', ipAddr, contributor.nick, increase = stars)

            # Send info to everyone, not just team.
            team = None

        # Send the message.
        if connId is not None:
            self.netman.send(connId, msg)
        else:
            self.broadcastUdp(msg, team)

    def receiveUseUpgradeMsg(self, connId, msg):
        '''Received from a client when their player wants to use an upgrade'''
        player = self.world.playerWithId[msg.playerId]
        if player.dead:
            self.validatePlayers(connId)
            return

        if (player.upgrade and player.upgrade.upgradeType == msg.upgradeType
                and not player.upgrade.inUse):
            if isinstance(player.upgrade, upgrades.Turret):
                zone = self.world.zoneWithId[msg.zoneId]
                player.changeZone(zone)
            if player.upgrade.serverUse():
                # Tell the clients
                self.broadcastUdp(msg)

                if self.world.gameState == GameState.InProgress:
                    ipAddr = self.connectedClients[connId]
                    self.addStat('upgradesUsed', ipAddr, player.nick, enemy = repr(player.upgrade))                
        else:
            self.validateUpgrades(connId)

    def receiveDeleteUpgradeMsg(self, connId, msg):
        # Check that this message comes from an IP address associated with the player.
        if self.playerConn[msg.playerId] != connId:
            return

        player = self.world.playerWithId[msg.playerId]
        if player.upgrade is None:
            self.validateUpgrades(connId)

        player.upgrade.serverDelete()
        self.broadcastUdp(msg)

    def sendDeleteUpgrade(self, playerId):
        self.broadcastUdp(DeleteUpgradeMsg(playerId))

    def validateTransaction(self, team, connId):
        '''Lets the client know all details about the team's transaction'''
        if team.hasAddress(connId):
            transaction = team.currentTransaction
            tId = team.id
            if not transaction:
                # Let client know that there is no transaction in progress
                msg = ValidateTransactionMsg(
                    teamId=team.id,
                    upgradeType='\x00'
                )
            else:
                contributions = ''
                for contribution in transaction.contributions.iteritems():
                    contributions += contribution[0].id
                    contributions += struct.pack('B', contribution[1])

                msg = ValidateTransactionMsg(
                    teamId=team.id,
                    playerId=transaction.purchasingPlayer.id,
                    upgradeType=transaction.upgrade.upgradeType,
                    timeLeft=transaction.age(),
                    contributions=contributions)

            self.netman.send(connId, msg)

    def receiveRequestPlayersMsg(self, connId, msg):
        self.validatePlayers(connId)

    def validatePlayers(self, connId):
        '''Sends a validation of all important data about all players'''
        
        playerIds = ''
        for player in self.world.playerWithId.itervalues():
            msg = ValidatePlayerMsg(player.id, player.team.id, player.stars,
                    player.currentZone.id, player.dead, player.nick.encode())
            if connId is None:
                self.broadcastUdp(msg)
            else:
                self.netman.send(connId, msg)
            playerIds += player.id

        # And also send the string of valid player ids.
        msg = ValidatePlayersMsg(playerIds)
        if connId is None:
            self.broadcastUdp(msg)
        else:
            self.netman.send(connId, msg)

    def receiveRequestZonesMsg(self, connId, msg):
        self.validateZones(connId)

    def validateZones(self, connId):
        '''Sends a validation of zone ownership'''
        for zone in self.world.zoneWithId.itervalues():
            if zone.orbOwner is None:
                orbTeamId = '\x00'
            else:
                orbTeamId = zone.orbOwner.id
            if zone.zoneOwner is None:
                zoneTeamId = '\x00'
            else:
                zoneTeamId = zone.zoneOwner.id
            msg = ValidateZoneMsg(zone.id, orbTeamId, zoneTeamId)

            self.netman.send(connId, msg)
    
    def receiveRequestStarsMsg(self, connId, msg):
        self.validateStars(connId)

    def validateStars(self, connId=None):
        '''Sends a validation of the number of stars each player has'''
        # Already sent in player validation info.
        self.validatePlayers(connId)

    def receiveRequestUpgradesMsg(self, connId, msg):
        self.validateUpgrades(connId)

    def validateUpgrades(self, connId):
        '''Sends all current upgrade details to a player, either over TCP or
        UDP'''

        # Keep track of which players have upgrades.
        playerIds = ''
        for player in self.world.playerWithId.itervalues():
            if player.upgrade is None:
                continue
            playerIds += player.id

            msg = ValidateUpgradeMsg(player.id, player.upgrade.upgradeType,
                    player.upgrade.inUse, player.currentZone.id)
            if (isinstance(player.upgrade, upgrades.Turret) and
                   player.upgrade.inUse):
                zoneId = player.currentZone

            # Send the message about this player's upgrades.
            self.netman.send(connId, msg)

        # Send the message about which players should have upgrades.
        msg = ValidateUpgradesMsg(playerIds)
        self.netman.send(connId, msg)

    def receiveZoneChangeMsg(self, connId, msg):
        '''Received from a player when they change zones'''
        # The message is re-broadcast unaltered
        player = self.world.playerWithId[msg.playerId]
        zone = self.world.zoneWithId[msg.zoneId]
        player.changeZone(zone)
        self.broadcastUdp(msg)

    def sendAllValidation(self, connId):
        self.validatePlayers(connId)
        self.validateZones(connId)
        self.validateUpgrades(connId)
        self.validateGameStatus(connId)
        self.sendGameMode(connId)

    def receiveChatMsg(self, connId, msg):
        player = self.world.playerWithId[msg.senderId]
        text = msg.text.decode()
        try:
            self.filterProfanities(text)
        except Profanity, e:
            # Kick the player based on server settings; or give them a warning?
            print e, 'in message from %s' % (player.nick)
            return

        if text.startswith('@@@') and self.settings['testMode']:
            print 'Got info request via chat from %s' % player.nick
            for teamID in ['A', 'B']:
                team = self.world.teamWithId[teamID]
                transaction = team.currentTransaction
                transText = {
                    TransactionState.Open : 'Open',
                    TransactionState.Abandoned : 'Abandoned',
                    TransactionState.Completed : 'Completed'
                    }
                messages = []
                if transaction is not None:
                    messages.append('Team%s has a transaction:' % teamID)
                    messages.append('- Current state: %s' % transText[transaction.state])
                    messages.append('- %s being purchased by %s' % (repr(transaction.upgrade), transaction.purchasingPlayer.nick))
                    messages.append('- %s/%s stars' % (transaction.totalStars, transaction.requiredStars))
                    messages.append('- Contributions: %s' %   transaction.contributions)
                else:
                    messages.append('Team%s has no transaction.' % teamID)

                print "\n".join(messages)
                
                for messageStr in messages:
                    sendId = self.playerConn[msg.senderId]
                    self.netman.send(sendId, ChatFromServerMsg(messageStr.encode()), sendAddress)
                    
        elif msg.kind == 't':
            team = self.world.teamWithId[msg.targetId]
            self.broadcastUdp(msg, team, connId)
        elif msg.kind == 'p':
            # Find the address to send it to:
            sendId = self.playerConn[msg.targetId]
            self.netman.send(sendId, msg)
        elif msg.kind == 'o':
            self.broadcastUdp(msg, nonSending=connId)

    def filterProfanities(self, message):
        '''Raises an error if there are profanities contained in the message'''
        profanities = ()
        for profanity in profanities:
            if message.__contains__(profanity):
                raise Profanity, 'Profanity Alert'

    def gameStart(self):
        print 'Server: Game Starting Now'
        self.broadcastTcp(GameStartMsg(self.world.gameTimeLimit))

    def gameOver(self, winningTeam = None, timeOver = False):
        self.world.gameState = GameState.Ended
        self.world.winner = winningTeam
        self.world.gameOverTime = timeNow()

        # Tell the log.
        if timeOver:
            print "Game time limit expired."
        else:
            print "Game is over. "
        if winningTeam is not None:
            winnerId = winningTeam.id
            print str(winningTeam) + " has won."

            for player in self.world.playerWithId.values():
                ip = self.connectedClients[self.playerConn[player.id]]
                if player.team == self.world.winner:
                    self.addStat('roundsWon', ip, player.nick)
                else:
                    self.addStat('roundsLost', ip, player.nick)

                if player.dead:
                    self.updateTimer('timeDead', ip, player.nick, delete = True)
                else:
                    self.updateTimer('timeAlive', ip, player.nick, delete = True)
                    if player.team == self.world.winner:
                        self.updateTimer('timeRabbit', ip, player.nick)
            
        else:
            winnerId = '\x00'
            print "The game resulted in a draw"
            
        # Tell the network.
        self.broadcastTcp(GameOverMsg(winnerId, timeOver))

    def receiveTeamIsReadyMsg(self, connId, msg):
        '''Called when a player says their team is ready. Note that if that
        player is not the captain of the team, this method will not change
        anything.'''
        player = self.world.playerWithId[msg.playerId]

        # Check that the message is from the client owning the player.
        if self.playerConn[msg.playerId] != connId:
            return

        if player.team.teamReady(player):
            # Rebroadcast the message.
            self.broadcastTcp(msg)
        else:
            # Player is not captain etc.
            self.validateGameStatus(connId)

        # Check if the both teams are ready.
        if self.world.checkStart():
            self.startSoon()

    def startSoon(self, reason = None, delay = 7):
        self.broadcastTcp(StartingSoonMsg(delay))
        reactor.callLater(delay, self.world.gameStart)
        

    def receiveSetCaptainMsg(self, connId, msg):
        '''Called when a player nominates themself as the captain of a team.
        If that team does not already have a captain, they are made captain
        instantly; all it really means is that they can say when their team
        is ready.'''

        if self.noCaptains:
            return
        
        player = self.world.playerWithId[msg.playerId]
        if player.team.makeCaptain(player):
            # Rebroadcast this message to everyone.
            self.broadcastTcp(msg)
        else:
            # A captain already exists for that team.
            self.validateGameStatus(connId)

    def validateGameStatus(self, connId=None):
        '''Sends a validation of things pertaining to the general running
        of the game at a fairly high level'''
        if self.world.gameState == GameState.PreGame:
            state = 'P'
        elif self.world.gameState == GameState.InProgress:
            state = 'I'
        else:
            state = 'E'

        if self.world.gameTimeLimit != 0:
            timeLeft = self.world.timeLeft()
            if timeLeft is None:
                timeLeft = 0
            msg = ValidateGameStatusMsg(state, True, timeLeft)
        else:
            msg = ValidateGameStatusMsg(state, False, 0)
                
        if connId is not None:
            self.netman.sendTCP(connId, msg)
        else:
            self.broadcastTcp(msg)

        for team in self.world.teams:
            hasCaptain = team.captain is not None
            if hasCaptain:
                captainId = team.captain.id
            else:
                captainId = '\x00'
            
            msg = ValidateTeamStatusMsg(team.id, hasCaptain, captainId,
                    team.ready, team.numOrbsOwned, len(team.connIds),
                    team.currentTransaction is not None)

            if connId is not None:
                self.netman.sendTCP(connId, msg)
            else:
                self.broadcastTcp(msg)

    def receiveRequestUDPStatusMsg(self, connId, msg):
        '''
        Client has requested info as to whether server is sending UDP.
        '''
        self.netman.sendTCP(connId,
            NotifyUDPStatusMsg(
                self.netman.getUDPStatus(connId)
            )
        )

    def sendServerMessage(self, string, connId = None):
        '''Sends a message to all clients, or to a single client'''
        msg = ChatFromServerMsg(string.encode())
        if connId is not None:
            self.netman.sendTCP(connId, msg)
        else:
            self.broadcastTcp(msg)

    def captainGone(self, team):
        '''Called when a team's captain leaves the game'''
        # TODO: send a server message too?
        self.validateGameStatus()

    def setGameMode(self, newMode):
        return self.world.setGameMode(newMode)
        
    def sendGameMode(self, connId=None):
        msg = SetGameModeMsg(self.world.gameMode.encode())
        if connId is not None:
            self.netman.sendTCP(connId, msg)
        else:
            self.broadcastTcp(msg)

    def kick(self, pId):
        if self.world.playerWithId.has_key(pId):
            self.removePlayer(pId)
            
    def disableCaptains(self):
        self.noCaptains = True
        print 'Disabling captains...',
        for team in self.world.teams:
            team.captain = None
        print 'done'
        
    def changeTeamName(self, team, newName):
        '''Called when the name of a team is changed via
        the server admin interface.'''
        print 'Team %s changed name to %s' % (team, newName)
        team.teamName = newName
        self.broadcastTcp(SetTeamNameMsg(team.id, newName.encode()))

    def changeTeamLimit(self, newLimit):
        '''Called when the maximum players per team is changed.'''

        oldLimit = self.settings['maxPlayers']
        self.settings['maxPlayers'] = newLimit
        print "Max players per team changed from %s to %s." % (oldLimit,
                                                               newLimit)

    def shutdown(self):
        if self._alreadyShutdown:
            print 'Server: Already shut down!'
            return
        self._alreadyShutdown = True
        # Send Shutdown message to all clients.
        print 'Server: SHUTTING DOWN'
        self.broadcastTcp(ServerShutdownMsg())

        # Kill server
        self.netman.removeHandler(self)
        self.running = False

        # Write the final data to the game file
        self.writeGameData()
        if self.fileUpdate is not None:
            self.fileUpdate.stop()

        self.onShutdown.execute()

