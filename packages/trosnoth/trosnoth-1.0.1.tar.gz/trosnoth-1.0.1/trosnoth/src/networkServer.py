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
import socket
import time
import os
import base64

from twisted.internet.protocol import Factory, DatagramProtocol
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet import reactor, task

import trosnoth.src.serverUniverse as serverUniverse
import trosnoth.src.serverLayout as serverLayout
import trosnoth.src.upgrades as upgrades
from trosnoth.src.universe_base import GameState
from trosnoth.src.networkDefines import *
from trosnoth.src.utils.unrepr import unrepr
from trosnoth.src.utils.utils import timeNow
from trosnoth.src.transaction import TransactionState, ServerTransaction

from trosnoth.data import getPath, user, makeDirs

REJOIN_DELAY_TIME = 8.1
# TODO: Server should check that there's no server with the same alias before
# begining.

class Profanity(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class UDPMulticastServer(DatagramProtocol):
    '''This protocol listens for and responds to queries as to what Trosnoth
    servers are on the network.

    Since this protocol listens on the local network multicast group, there
    may be other programs using this group. The Trosnoth messages therefore
    should all begin with the identifier 'Trosnoth:'.
    '''
    
    def __init__(self, server, tcpPort):
        '''tcpPort and udpPort are the details of this server. These must be
        included in the message when this server announces itself to clients.
        The actual details can be got using port.getHost()
        '''
        self.server = server
        self.serverString = struct.pack('!I', tcpPort.getHost().port) + \
                                        server.alias.encode('ascii')
        
    def startProtocol(self):
        # Join the correct multicast group.
        self.transport.joinGroup(multicastGroup)

    def datagramReceived(self, datagram, address):
        # Respond to Trosnoth requests.
        if datagram.startswith('Trosnoth:'):
            message = datagram[9:]
            if message == 'ServerList?':
                # TODO: Could send current game stats (players per team,
                # who is winning, time remaining)
                if self.server.world.gameState != GameState.Ended \
                    and not self.server.replay:
                # Request for list of server aliases.
                    self.transport.write('Trosnoth:Server:%s' % \
                                         self.serverString,
                                     address)
            elif message == 'UnknownRequest':
                # We shouldn't really get this on the multicast.
                pass
            else:
                # Tell the client we don't understand.
                self.transport.write('Trosnoth:UnknownRequest')

class CmdServer(DatagramProtocol):
    '''This protocol is used to receive datagrams containing server commands.'''
    
    def __init__(self, server, port):
        self.server = server

        # Ask the system for a UDP port.
        self.port = reactor.listenUDP(port, self)

    def datagramReceived(self, datagram, address):
        # Check that it comes from me.
        if not validServerAdminSender(address[0]):
            print 'Command received from IP %s - expecting one of %s' % \
                  (address[0], ', '.join(validServerAdminIPs))
            return

        # Console spam prevention
        if not datagram.startswith('GameStatus'):
            print 'Server got command: ' + datagram

        # Now process the command.
        if datagram.startswith('GameMode='):
            if self.server.setGameMode(datagram[9:]) == False:
                self.sendResponse("Result:InvalidGameMode", address)
            else:
                self.sendResponse("Result:Success", address)
        elif datagram.startswith('Kick '):
            pIdString = datagram[5:]
            try:
                pIdNum = int(pIdString)
            except ValueError:
                pass
            else:
                if pIdNum < 0 or pIdNum > 255:
                    pass
                else:
                    pId = struct.pack('B', pIdNum)
                    self.server.kick(pId)
        elif datagram.startswith('Outcome='):
            team = datagram[8:]
            if team == 'blue':
                self.server.gameOver(self.server.world.teams[0])
            elif team == 'red':
                self.server.gameOver(self.server.world.teams[1])
            elif team == 'draw':
                self.server.gameOver()
        elif datagram == 'StartGame':
            self.server.world.gameStart()
        elif datagram.startswith('NoCaptains'):
            self.server.disableCaptains()
        elif datagram.startswith('TeamName'):
            if (datagram[8] == "0") or (datagram[8] == "1"):
                self.server.changeTeamName(datagram[8], datagram[10:20])
        elif datagram.startswith('Shutdown'):
            self.server.shutdown()
        elif datagram.startswith('GameStatus'):
            # GameStatus:I7.7
            line = 'GameStatus:'
            currentGameState = self.server.world.gameState
            if currentGameState == GameState.PreGame:
                line += 'P'
            elif currentGameState == GameState.InProgress:
                line += 'I'
            elif currentGameState == GameState.Ended:
                winningTeam = self.server.world.winner
                if winningTeam is None:
                    line += 'D'
                elif winningTeam.id < winningTeam.opposingTeam.id:
                    line += 'B'
                else:
                    line += 'R'
            else:
                line += '?'
            line += str(self.server.world.teamWithId['A'].numOrbsOwned)
            line += "."
            line += str(self.server.world.teamWithId['B'].numOrbsOwned)
            self.sendResponse(line, address)

            # TeamNames:Team 1    Team 2    GameMode
            #           12345678901234567890...
            blueTeamName = self.server.world.teams[0].teamName.ljust(10)
            redTeamName = self.server.world.teams[1].teamName.ljust(10)
            gameMode = self.server.world.gameMode
            line = "TeamNames:"+blueTeamName+redTeamName+gameMode
            self.sendResponse(line, address)
        elif datagram.startswith('StatCheck'):
            print self.server.stats

    def sendResponse(self, command, address):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        n = s.sendto(command, (address[0], defaultServerAdminResponsePort))

class UDPServer(DatagramProtocol):
    '''This protocol is used to send and receive datagrams about the game in
    progress. It is used for regular updates, because they need to be delivered
    quickly and it doesn't matter too much if packets are occasionally lost
    because another update packet will follow shortly.'''
    
    def __init__(self, server, port):
        self.server = server

        # Ask the system for a UDP port.
        self.port = reactor.listenUDP(port, self)

    def datagramReceived(self, datagram, address):
                
        if datagram.startswith('Shot'):
            self.server.newShot(datagram, address)

        elif datagram.startswith('Kill'):
            self.server.killPlayer(datagram, address)

        elif datagram.startswith('KShot'):
            self.server.destroyShot(datagram, address)
        
        elif datagram.startswith('PlUpd'):
            self.server.playerUpdate(datagram, address)

        elif datagram.startswith('TagZone'):
            self.server.zoneTagged(datagram, address)

        elif datagram.startswith('Resp'):
            self.server.respawn(datagram, address)

        elif datagram.startswith('Trans'):
            self.server.startTransaction(datagram, address)
            
        elif datagram.startswith('AddStars'):
            self.server.addStars(datagram, address)

        elif datagram.startswith('Abandon'):
            self.server.abandonTransaction(datagram, address)

        elif datagram.startswith('UseUpgr'):
            self.server.useUpgrade(datagram, address)

        elif datagram == 'reqPlayers':
            self.server.validatePlayers(address)

        elif datagram == 'reqZones':
            self.server.validateZones(address)

        elif datagram.startswith('reqTrans'):
            team = self.server.world.teamWithId[datagram[8]]
            self.server.validateTransaction(team, address)

        elif datagram == 'reqStars':
            self.server.validateStars(address = address)

        elif datagram == 'reqUpgrades':
            self.server.validateUpgrades(address)

        elif datagram.startswith('DelUpgr'):
            self.server.receiveDeleteUpgrade(datagram, address)

        elif datagram.startswith('ZoneCh'):
            self.server.receiveZoneChange(datagram, address)

        elif datagram.startswith('Chat'):
            self.server.receiveChat(datagram, address)

        elif datagram.startswith('reqGameStat'):
            self.server.validateGameStatus(address)

    def send(self, datagram, address):
        self.transport.write(datagram, address)
                

class TCPServer(Int32StringReceiver):
    '''This protocol is used for important information that will only be
    transmitted once, and isn't supremely important for instant-by-instant
    gameplay.'''

    def __init__(self):
        self.players = set()
        
    def connectionMade(self):
        print 'Server: a client has connected.'
        self.validated = False
        self.udpPortString = struct.pack('!I', self.factory.server. \
                                        udpProtocol.port.getHost().port)
        self.sentTransaction = {}
        for team in self.factory.server.world.teamWithId.values():
            self.sentTransaction[team] = False
        
    def connectionLost(self, reason):
        print 'Server: a client connection was lost.'
        self.factory.server.connectionLost(self)

    def stringReceived(self, line):
        
        # Note: NetworkServer instance is self.factory.server
        print 'Server: Got line: ', line

        if not self.validated:
            # We haven't yet told this client about the server settings.
            if line.startswith('TrosnothRequestSettings:'):
                # Check the version number.
                if line[28:] not in validClientVersions:
                    # Invalid version.
                    self.sendString('TrosnothBadVersion:' + serverVersion)
                    print 'Server: Connecting client has bad version. Disconnecting.'
                    self.transport.loseConnection()
                else:
                    # Valid version. Get the UDP address.
                    self.ipAddr = self.transport.getPeer().host
                    self.clientUdpPort = struct.unpack('!I', line[24:28])[0]
                    print 'Server: Connecting client has IP %s / port %d' % (self.ipAddr, self.clientUdpPort)

                    #print 'DEBUG: IP %s joining at time %f' % (self.ipAddr, time.time())
                    # Send the setting information.
                    data = 'TrosnothInitClient:%s' % \
                           self.factory.server.getClientSettings()

                    self.sendString(data)

                    # Remember that this connection's ready for transmission.
                    self.validated = True
                    self.factory.server.connectionValidated(self,
                                                    self.clientUdpPort)
                    self.factory.server.sendAllValidation(self)
            else:
                # Who knows what tried to connect. Kick it off.
                print 'Server: Connecting client is not Trosnoth client. Disconnecting.'
                self.transport.loseConnection()
        else:
            # Pass message on to server class.
            self.factory.server.gotTcpMessage(self, line)

class TCPFactory(Factory):
    protocol = TCPServer
    def __init__(self, server, port=0):
        self.server = server
        self.port = reactor.listenTCP(port, self)
        
class NetworkServer(object):
    '''Once created, this object acts as a server.'''

    pingTime = 0.75

    def __init__(self, alias, tcpPort=0, udpPort=None, cmdPort=None,
                 settings = {}):
        'A port of 0 asks the system for a port.'
        # First initialise state variables.
        self.connectedClients = {}
        self.lastPlayerId = 41

        self.noCaptains = False     # Does not allow captains - start from server interface.
        self.replay = False

        self.players = {}
        self.stats = {}
        
        if udpPort == None:
            udpPort = tcpPort
        if cmdPort == None:
            cmdPort = udpPort + 1

        self.delayData = {}

        if 'replayFile' in settings:
            self.replay = True
            replayPath = getPath(user, 'replays')
            makeDirs(replayPath)
            self.replayFile = open(os.path.join(replayPath, settings['replayFile']), 'r')
            self.replayInfo = {}
            line = ""
            looking = None
            while line.strip() != "InfoOver":
                line = self.replayFile.readline()
                if line == '' or line.strip() == 'InfoOver':
                    break
                if line[:6] == 'Info: ' and line[10:12] == ': ':
                    identifier = line[6:10]
                    self.replayInfo[identifier] = line[12:]
                    looking = identifier
                elif looking:
                    self.replayInfo[identifier] += line

            unpickle = ['Sett', 'Okay', 'CStr']
            unRepr = ['CStr']
            for (k, v) in self.replayInfo.iteritems():
                if k in unpickle:
                    v = pickle.loads(base64.b64decode(v))
                if k in unRepr:
                    v = unrepr(v)
                try:
                    if v[-1:] == '\n':
                        v = v[:-1]
                except TypeError:
                    pass
                self.replayInfo[k] = v

            settings = self.replayInfo['Sett']
            alias = "REPLAY: " + self.replayInfo['Name']
            self.start = float(self.replayInfo['Time'])

            # How this is structured:
            # replayTimes is an ordered list of timestamps.
            # replayData is a dictionary: the keys are the timestamps
            # and the values are a list of packets that need to be sent
            # at that time.

            self.replayTimes = []
            self.replayData = {}

            # How many lines should be read at a time?
            self.linesAtATime = 500
            self.totalLinesRead = 0
            self.totalLinesPlayedBack = 0
            self.keepReading = True

            for lineNumber in range(0, self.linesAtATime):
                line = self.replayFile.readline()
                self.totalLinesRead += 1
                if line.strip() == "":
                    self.keepReading = False
                    break
                if line[:12] == "ReplayData: ":
                    timestamp = float(line[12:26]) - self.start
                    if timestamp not in self.replayTimes:
                        self.replayTimes.append(timestamp)
                        self.replayData[timestamp] = []
                    packet = line[27:]
                    self.replayData[timestamp].append(packet[:2] + base64.b64decode(packet[2:]))

            # Up to [x] lines will be read by this point, but there still might be more!

        # Server alias.
        self.alias = alias
        self.serverString = alias + ' - ' + time.asctime()
        
        # Set up the protocols for the game.
        if not self.replay:
            self.cmdProtocol = CmdServer(self, cmdPort)
        else:
            self.cmdProtocol = None

        self.udpProtocol = UDPServer(self, udpPort)
        self.tcpFactory = TCPFactory(self, tcpPort)
        if not 'replayFile' in settings:
            # Set up the multicast protocol and tell it the port details.
            self.udpMulticaster = UDPMulticastServer(self, self.tcpFactory.port)
            reactor.listenMulticast(multicastPort, self.udpMulticaster)
        else:
            self.udpMulticaster = None

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
        else:
            self.recordReplay = False

        # Don't make a replay of the replay!
        if not self.replay:
            
            # Initialize the replay file
            if self.recordReplay:
                curDate = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
                fname = self.alias + ' (0).replay'
                replayPath = getPath(user, 'replays')
                makeDirs(replayPath)
                fname = os.path.join(replayPath, fname)
                copyCount = 0
                while os.path.exists(fname):
                    copyCount += 1
                    fname = self.alias + ' (' + str(copyCount) + ').replay'
                    fname = os.path.join(replayPath, fname)
                    
                self.replayFile = file(fname, 'w')

                # Add the server name
                self.replayAppendInfo("Name", self.alias)
                # Add the current date / time
                self.replayAppendInfo("Date", curDate)
                # Add the server version
                self.replayAppendInfo("SVer", serverVersion)
                # Add the list of valid client versions
                self.replayAppendInfo("Okay", base64.b64encode(pickle.dumps(validClientVersions)))
                # Add the current replay version
                self.replayAppendInfo("RVer", replayVersion)
                # Add the server settings
                self.replayAppendInfo("Sett", base64.b64encode(pickle.dumps(self.settings)))

            # Set up the universe.
            self.initWorld()

            if self.recordReplay:
                # Add the information that is sent to the client
                self.replayAppendInfo("CStr", base64.b64encode(pickle.dumps(self.getClientSettings())))
                # Add the current time
                self.replayAppendInfo("Time", "%#.3f" % time.time())
                # Add a line to signify that the information is over
                print >> self.replayFile, "InfoOver"

                self.replayFile.flush()
            
        else:
            # Set up the universe (based on the replay info)
            self.initReplayWorld()
        
        # TODO: put the constant for 'maximum team name length' somewhere else
        # since it is used in at least two places
        if self.settings['teamNames']:
            self.changeTeamName("0", settings['teamNames'][0][0:10])
            self.changeTeamName("1", settings['teamNames'][1][0:10])

        if self.settings['beginNow']:
            self.world.gameStart()
        del self.settings['beginNow']

        if self.replay:
            self.startTime = time.time()
            self.replayPlayback = task.LoopingCall(self.tick)
            self.replayPlayback.start(0, False)

            if self.keepReading:
                self.replayReading = task.LoopingCall(self.readSomeMore)
                self.replayReading.start(10, False)

        self.running = True

        fname = self.alias + ' (0).stat'
        statPath = getPath(user, 'stats')
        makeDirs(statPath)
        fname = os.path.join(statPath, fname)
        copyCount = 0
        while os.path.exists(fname):
            copyCount += 1
            fname = self.alias + ' (' + str(copyCount) + ').stat'
            fname = os.path.join(statPath, fname)
            
        self.statFilename = fname

        self.statWrite = task.LoopingCall(self.writeStats)
        self.statWrite.start(1, False)

    def writeStats(self):
        statFile = file(self.statFilename, 'w')
        pickle.dump(self.stats, statFile)
        statFile.flush()
        statFile.close()

    def readSomeMore(self):
        for lineNumber in range(0, self.linesAtATime):
            line = self.replayFile.readline()
            self.totalLinesRead += 1
            if line.strip() == "":
                self.keepReading = False
                self.replayReading.stop()
                break
            if line[:12] == "ReplayData: ":
                timestamp = float(line[12:26]) - self.start
                if timestamp not in self.replayTimes:
                    self.replayTimes.append(timestamp)
                    self.replayData[timestamp] = []
                packet = line[27:]
                self.replayData[timestamp].append(packet[:2] + base64.b64decode(packet[2:]))
        print "%d lines now read" % self.totalLinesRead
        print "%d lines now played back" % self.totalLinesPlayedBack

    def tick(self):
        curTime = time.time() - self.startTime
        if len(self.replayTimes) > 0:
            while self.replayTimes[0] < curTime:
                timestamp = self.replayTimes[0]
                for data in self.replayData[timestamp]:
                    self.totalLinesPlayedBack += 1
                    protocol = data[0]
                    packet = data[2:]
                    if packet[-1] == "\n":
                        packet = packet[:-1]
                    if protocol == "T":
                        self.broadcastTcp(packet)
                        #print "Broadcasting on TCP [%s][%s]" % (str(timestamp), packet[:4])
                    elif protocol == "U":
                        self.broadcastUdp(packet)
                        #print "Broadcasting on UDP [%s][%s]" % (str(timestamp), packet[:4])
                    else:
                        print "Unrecognized protocol: " + protocol
                del self.replayTimes[0]
                if len(self.replayTimes) == 0:
                    self.replayPlayback.stop()
                    print "GAME OVER MAN, GAME OVER"
                    print "%d LINES READ" % self.totalLinesRead
                    print "%d LINES PLAYED BACK" % self.totalLinesPlayedBack
                    self.shutdown()
                    break

    def replayAppend(self, datagram, protocol):
        if self.recordReplay:
            datagram = base64.b64encode(datagram)
            string = "ReplayData: %#.3f %s %s" % (time.time(), protocol, datagram)
            print >> self.replayFile, string
            self.replayFile.flush()

    def replayAppendInfo(self, identifier, string):
        if self.recordReplay:
            string = "Info: %s: %s" % (identifier, string)
            print >> self.replayFile, string

    def initReplayWorld(self):
        # Create a universe object.
        self.world = serverUniverse.Universe(self, \
                                             self.settings['gameDuration'])
    
        # Initialise layout database.
        self.layoutDatabase = serverLayout.LayoutDatabase()
        layouts = []
        # Check if we know of all the map block layout files.
        for filename, checksum in self.replayInfo['CStr']['layoutDefs']:
            try:
                layouts.append(self.layoutDatabase.getLayout(filename,
                                                             checksum))
            except ValueError:
                # TODO: Checksum is wrong: request correct layout from server.
                self.connectingDeferred.errback(
                    Exception('server and client versions of %s differ' % \
                              filename))
                return
            except KeyError:
                # TODO: Filename not found: request layout from server.
                self.connectingDeferred.errback(
                    Exception('client does not have file %s' % filename))
                return
        self.layoutDefs = layouts

        for zone in self.world.zones: 
            zone.mapBlockList = [] 
            zone.unBlockedCount = 0 
        
        # Populate the map blocks with obstacles.
        worldMap = self.replayInfo['CStr']['worldMap']
        for i in range(len(self.world.zoneBlocks)):
            curBlockRow = self.world.zoneBlocks[i]
            curDefRow = worldMap[i]
            for j in range(len(curBlockRow)):
                curBlock = curBlockRow[j]
                blockDetails = curDefRow[j]
                if blockDetails != -1:
                    blockIndex, reverse = blockDetails
                    layout = self.layoutDefs[blockIndex]
                    if reverse:
                        layout.mirrorLayout.applyTo(curBlock)
                    else:
                        layout.applyTo(curBlock)
        
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
                    elif random.Random().random() < blockRatio:
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

    def getClientSettings(self):
        '''Returns a string representing the settings which must be sent to
        clients that connect to this server.'''

        result = {}

        result['serverString'] = self.serverString
        
        # 1. Settings the client needs to know from self.settings.
        for k in ('halfMapWidth', 'mapHeight'):
            result[k] = self.settings[k]

        # 2. The udp port to connect to.
        result['udpPort'] = self.udpProtocol.port.getHost().port

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

        result['replay'] = self.replay

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

    def addPlayerToStats(self, ipAddr, nick):
        if ipAddr not in self.stats:
            self.stats[ipAddr] = {}
        if nick not in self.stats[ipAddr]:
            self.stats[ipAddr][nick] = {"kills": 0,           # Number of kills they've made
                                        "deaths": 0,          # Number of times they've died
                                        "zoneTags": 0,        # Number of zones they've tagged
                                        "shotsFired": 0,      # Number of shots they've fired
                                        "shotsHit": 0,        # Number of shots that have hit a target
                                        "starsEarned": 0,     # Aggregate total of stars earned
                                        "starsUsed": 0,       # Aggregate total of stars used
                                        "starsWasted": 0,     # Aggregate total of stars died with
                                        "playerKills": {},    # Number of kills against individual people
                                        "playerDeaths": {},   # Number of deaths from individual people
                                        }

    def addStat(self, statName, ipAddr, nick, increase = 1, enemy = None):
        if statName not in disabledStats:
            if enemy is None:
                self.stats[ipAddr][nick][statName] += increase
            else:
                if enemy not in self.stats[ipAddr][nick][statName]:
                    self.stats[ipAddr][nick][statName][enemy] = 0
                    
                self.stats[ipAddr][nick][statName][enemy] += increase
            
    def connectionValidated(self, tcpConnection, udpPort):
        '''Called by a tcp protocol instance to say it's received a valid
        world request from a client.'''
        # Update a mapping from udp port to tcp connection.
        ipAddr = tcpConnection.transport.getPeer().host
        udpAddress = (ipAddr, udpPort)

        self.connectedClients[udpAddress] = tcpConnection

    def connectionLost(self, tcpConnection):
        # Forget about this connection.
        if tcpConnection.validated:
            try:
                ipAddr = tcpConnection.transport.getPeer().host
                udpPort = tcpConnection.clientUdpPort
                #print 'DEBUG: IP %s leaving at time %f' % (ipAddr, time.time())
                if tcpConnection.players:
                    self.delayData[ipAddr] = time.time()
                del self.connectedClients[(ipAddr, udpPort)]
            except KeyError:
                pass

            # Go through the players owned by this connection.
            for pId in tcpConnection.players:
                self.removePlayer(pId)

        # Check for game over and no connectios left.
        if len(self.connectedClients) == 0 and self.world.gameState == GameState.Ended:
            # Shut down the server.
            print 'Server: Last client connection lost after end of game: shutting down.'
            self.shutdown()

    def removePlayer(self, pId):
        '''Signal that player has been removed.'''
        # Network Protocol for removePlayer:
        #
        # First 5 characters: "DelP:"
        # 6th character: Player ID to remove from the game
        
        self.broadcastTcp('DelP:' + pId)

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
        if player.reCall:
            player.reCall.cancel()
        
        # Free this player id.
        del self.players[pId]
        del self.world.playerWithId[pId]


    def broadcastTcp(self, line):
        '''Sends the specified line to all clients.'''

        # Add the line to the replay file
        if not self.replay:
            self.replayAppend(line, "T")

        for tCon in self.connectedClients.itervalues():
            tCon.sendString(line)

    def broadcastUdp(self, packet, team = None, nonSending = None):
        '''Sends the specified packet to all clients.'''

        # Add the packet to the replay file
        if not self.replay:
            # The replay doesn't seem to like this and it looks like taking it
            # out doesn't present any problems
            if not packet.startswith("ZoneCh"):
                self.replayAppend(packet, "U")
        
        if team:
            # FIXME: this will send to a client twice if there are two players
            # on that one client
            for uPort in team.udpAddrs.values():
                if uPort != nonSending or not nonSending:
                    self.udpProtocol.port.write(packet, uPort)
        else:
            for uPort in self.connectedClients.iterkeys():
                if uPort != nonSending or not nonSending:
                    self.udpProtocol.port.write(packet, uPort)

    def gotTcpMessage(self, tcpConnection, line):
        '''Called by a tcp connection instance when it gets a message.'''
        
        # Network Protocols:
        #
        # Join:
        # First 5 characters: "Join:"
        # 6th Character: ID of team they want to join
        # 7th character onwards: the player's nick
        # 
        # If the player is allowed to join:
        #   New Player:
        #   First 5 characters: "NewP:"
        #   6th character: An unique ID allocated to this player
        #   7th character: Team for that player to join
        #   Characters 8-11: Zone that the player is starting in
        #   Characters 12 onwards: the player's nick
        #
        #   Tell the client who sent the join request, that they own the 
        #   player (make it a local player):
        #     First 5 characters: "OwnP:"
        #     6th Character: ID of player to own
        # 
        # Otherwise:
        #   Let the client know they have been denied:
        #   First 5 Characters: "NotP:"
        #   6th character: single character giving the reason
        #                  why they couldn't join:
        #                  F = Full
        #                  O = Game Over
        #                  W = Need to wait short time before rejoining
        #   7th Character: ID of team they want to join
        #   8th character onwards: the player's nick
        #
        # Leave the Game:
        # First 5 characters: "Leev:"
        # 6th character: The ID of the player leaving
        # RemovePlayer is called (the network is informed from there)
        
        
        msg = line[:5]
        if msg == 'Join:':
            # FIXME: do it per team
            # TODO: disallow rejoining after a while
            # Check if we can add another player.
            teamId = line[5]
            team = self.world.teamWithId[teamId]
            # print len(team.udpAddrs), self.settings['maxPlayers']
         
            # Too many players, or game ended. Send response.
            if len(team.udpAddrs) >= self.settings['maxPlayers']:
                tcpConnection.sendString('NotP:F' + line[5:])
                return
            elif self.world.gameState == GameState.Ended:
                tcpConnection.sendString('NotP:O' + line[5:])
                return

            ipAddr = tcpConnection.transport.getPeer().host
            # Except in test mode, clients can't rejoin immediately.
            if not self.settings['testMode']:
                if ipAddr in self.delayData:
                    waitTime = REJOIN_DELAY_TIME
                    leftTime = self.delayData[ipAddr]
                    curTime = time.time()
                    if curTime - leftTime < waitTime:
                        timeLeft = round(waitTime - (curTime - leftTime), 1)
                        #tcpConnection.sendString('NotP:W' + teamID + str(timeLeft))
                        tcpConnection.sendString('NotP:W' + line[5] + str(timeLeft) + line[6:])
                        print 'Player blocked from joining; needs to wait ' + str(timeLeft) + ' seconds'
                        return
                
            # Get the player nick.
            nick = marshal.loads(line[6:])

            # Create a player id.
            playerId = self.newPlayerId(tcpConnection)
            
            zone = self.world.getRandomZone(team)
            zoneId = struct.pack('!I', zone.id)
            # First tell everyone that a new player has been added.
            self.broadcastTcp('NewP:%s%s%s%s' % (playerId, teamId, zoneId,      
                                                 marshal.dumps(nick)))
            
            # Now tell this client that it owns the player.
            tcpConnection.sendString('OwnP:' + playerId)
            
            udpPort = tcpConnection.clientUdpPort
            udpAddress = (tcpConnection.transport.getPeer().host, udpPort)
            team.addAddress(playerId, udpAddress)
            # TODO: do we really need this extra code to save a bit of
            # tcp-sending?
            # Ensure that transaction info is only sent once to this client.
            if tcpConnection.sentTransaction[team] == False:
                self.validateTransaction(team, tcpConnection, tcp = True)
                tcpConnection.sentTransaction[team] = True
            player = serverUniverse.Player(self.world, team, nick, playerId, \
                                           zone)
            # Start the pinging in 5 seconds the first time; should give them
            # time to receive other messages.
            player.reCall = reactor.callLater(5, self.pingForUpdate, \
                                          player, udpAddress)

            ipAddr = tcpConnection.transport.getPeer().host
            
            self.addPlayerToStats(ipAddr, nick)
                
        elif msg == 'Leev:':
            pId = line[5]
            
            # Check that the player exists.
            if self.players.has_key(pId):
                self.removePlayer(pId)
                
        elif line.startswith("Captain"):
            self.makeCaptain(line, tcpConnection)
            
        elif line.startswith("Ready"):
            self.teamReady(line, tcpConnection)

    def newPlayerId(self, tcpConnection):
        '''Creates a new single-character player id.'''

        pId = struct.pack('B', self.lastPlayerId)
        while self.players.has_key(pId):
            self.lastPlayerId = (self.lastPlayerId + 1) % 256
            pId = struct.pack('B', self.lastPlayerId)

        self.players[pId] = tcpConnection
        tcpConnection.players.add(pId)
        return pId

    def newShot(self, message, address):
        '''Called when a Fire Shot request is received from a client'''
        # Protocol for newShot
        #
        # First 4 characters: "Shot"
        # 5th character: ID of player doing the shooting
        # characters 5-8: angle of firing
        # characters 9-16: position the shot originated from
        # character 17: G if this is a grenade shot
        #
        # Re-broadcasts the message, but with slight changes. Protocol:
        # First 4 characters: "Shot"
        # 5th character: ID of the player doing the shooting
        # 6th character: shot ID that is unique to the player
        # characters 7-10: angle of firing
        # characters 11-18: position the shot originated from
        # character 19: If the player is a turret, then 'Y', otherwise 'N'

        
        pId = message[4]
        angle = struct.unpack('f', message[5:9])
        pos = struct.unpack('ff', message[9:17])
        turret = message[17]
        
        player = self.world.playerWithId[pId]
        if player.dead:
            self.validatePlayers(address)
            return
        sId = player.newShotId()
        if player.turret or turret == 'G':
            turret = 'Y'
            tShot = True
        else:
            turret = 'N'
            tShot = False
        try:
            i, j = self.world.getMapBlockIndices(*pos)
            block = self.world.zoneBlocks[i][j]
        except IndexError:
            print "Server: Shot off the map"
        else:
            if turret != 'G':
                self.addStat('shotsFired', address[0], player.nick)
            self.broadcastUdp('Shot' + pId + sId + message[5:17] + turret)
            serverUniverse.Shot(sId, player.team, pos, angle[0], player, \
                                tShot)

    def killPlayer(self, message, address):
        '''Received from a client when a player local to it has died'''
        # Protocol for killPlayer:
        #
        # First 4 characters: "Kill"
        # 5th Character: ID of the player-to-be-dead
        # 6th character: ID of the killer
        # 7th character: ID of the shot that killed the player
        # Characters 8-15: Position of the dead player
        #
        # If the data received is valid, it is rebroadcast with the killer's
        # current number of stars appended to the end
        # Otherwise, validation occurs.
        
        pId = message[4]
        kId = message[5]
        sId = message[6]

        try:
            player = self.world.playerWithId[pId]
            killer = self.world.playerWithId[kId]

            victimIP = self.players[pId].transport.getPeer().host
            killerIP = self.players[kId].transport.getPeer().host
                
            shot = killer.shots[sId]
            if player.killable():
                starsBefore = killer.stars
                self.addStat('starsWasted', victimIP, player.nick, player.stars)
                player.killed(killer)
                stars = struct.pack('B', killer.stars)
                starsAfter = killer.stars

                self.addStat('deaths', victimIP, player.nick)
                self.addStat('playerDeaths', victimIP, player.nick, enemy = killer.nick)
                
                self.addStat('kills', killerIP, killer.nick)
                self.addStat('playerKills', killerIP, killer.nick, enemy = player.nick)
                
                self.addStat('shotsHit', killerIP, killer.nick)

                if starsAfter > starsBefore:
                    self.addStat('starsEarned', killerIP, killer.nick)
                             
                self.broadcastUdp(message + stars)
                if player.team.currentTransaction and \
                   player.team.currentTransaction.purchasingPlayer == player:
                    self.sendTransactionUpdate(player.team, 'a')
                killer.destroyShot(sId)
            elif player.dead:
                self.validatePlayers(address)
            elif player.turret or player.shielded:
                self.validateUpgrades(address)
                self.sendShotDestroyed(kId, sId)
                shot.shotDead()
                self.addStat('shotsHit', killerIP, killer.nick)
                if player.shielded:
                    player.upgrade.serverDelete()
                    self.sendDeleteUpgrade(pId)
                    
        except KeyError:
            # One or more of those things doesn't exist on the server
            # So just don't do anything
            pass
        
    def destroyShot(self, message, address):
        '''Received in the event that a shot is destroyed other than by hitting
        a player, an obstacle, or by existing too long'''
        # Protocol for destroyShot:
        #
        # First 5 characters: "KShot"
        # 6th character: ID of the originating shot's player
        # 7th character: ID of the shot
        #
        # If the shot exists, rebroadcast the message
        pId = message[5]
        sId = message[6]
        shot = self.world.shotWithId(pId, sId)
        if shot:
            # Ensure the shot exists
            shooterIP = self.players[pId].transport.getPeer().host
            shooter = self.world.playerWithId[pId]
            self.addStat('shotsHit', shooterIP, shooter.nick)
            shot.shotDead()
            self.broadcastUdp(message)

    def sendShotDestroyed(self, pId, sId):
        # Protocol for sendShotDestroyed:
        #
        # Same as for destroyShot
        self.broadcastUdp('KShot' + pId + sId)

    def playerUpdate(self, message, address):
        # Protocol for playerUpdate
        #
        # First 5 characters: "PlUpd"
        # 6th Character: ID of player being updated
        # Characters 7-14: the player's position
        # Characters 15-18: the player's x-Velocity
        # Characters 19-22: the player's y-Velocity
        # Characters 23-30: the player's current MapBlockIndices
        # Characters 31-34: the angle that the player is viewing at
        # Character 35: If the player is holding the left key, 'T', otherwise 'F'
        # Character 36: If the player is holding the right key, 'T', otherwise 'F'
        # Character 37: If the player is holding the jump key, 'T', otherwise 'F'
        # Character 38: If the player is holding the down key, 'T', otherwise 'F'
        # Character 39: If the player currently has an upgrade, 'T', otherwise 'F'
        # Character 40: If the player is dead, 'T', otherwise 'F'
        #
        # The message is rebroadcast unchanged
        
        # TODO: Perhaps do a timestamp check?
        # TODO: note that it doesn't currently follow protocol; xVel isn't sent
        # yet. But I shall get to that.
        pId = message[5]

	try:
            player = self.world.playerWithId[pId]
	except KeyError:
	    # TODO: Some sensible processing of this error.
	    print >> sys.stderr, 'playerUpdate KeyError'
	    return
    
        if player.reCall:
            player.reCall.cancel()
        player.reCall = reactor.callLater(self.pingTime, self.pingForUpdate, \
                                          player, address)
        dead = message[35] == 'T'
        if dead != player.dead:
            # Client is incorrect about their own life situation. 
            self.validatePlayers(address)
            # Correct the message
            if message[35] == 'T':
                message = message[:35] + 'F' + message[36:]
            else:
                message = message[:35] + 'T' + message[36:]
        upgradeExists = message[34] == 'T'
        if (upgradeExists and player.upgrade is None) or \
            (player.upgrade is not None and not upgradeExists):
            self.validateUpgrades(address = address)
            print 'Upgrade Wrong for %s' % (player.nick,),
            if upgradeExists:
                print '(should have upgrade)'
            else:
                print '(should not have upgrade)'
            # Correct the message
            if message[34] == 'T':
                message = message[:34] + 'F' + message[35:]
            else:
                message = message[:34] + 'T' + message[35:]
        self.broadcastUdp(message)

    def pingForUpdate(self, player, address = None):
        '''Pings a client; asking for an update for a particular player'''
        # Protocol for pingForUpdate
        #
        # First 7 characters: "PingUpd"
        # 8th character: The ID of the player being requested
           
        player.reCall = reactor.callLater(self.pingTime, self.pingForUpdate, \
                                          player, address)
        message = 'PingUpd' + player.id
        self.udpProtocol.send(message, address)

    def pingForZone(self, player):
        '''Asks a player for what zone they are in.'''
        # Protocol for pingZone
        #
        # First 7 characters: "PingZne"
        # 8th character: ID of player being... um... pung?

        
        # Find the address to send it to:
        address = (self.players[player.id].transport.getPeer().host, \
                       self.players[player.id].clientUdpPort)
        message = 'PingZne' + player.id
        self.udpProtocol.send(message, address)
        

    def zoneTagged(self, message, address):
        '''Called when a client says that a player has tagged a zone'''
        # Protocol for zoneTagged
        #
        # First 7 characters: "TagZone"
        # Characters 8-11: ID of the zone being tagged
        # 12th Character: Tagging Player's ID
        # 13th Character: Tagging team
        #
        # The message is rebroadcast with the following changes:
        # Characters 14-17: The number of zones owned by the tagging team now
        # Character 18: The number of stars the tagger now has
        # Character 19: If there was a turreted player in the zone, 'T'; else 'F'
        # Character 20: If there was a turreted player, that player's ID

        zId = struct.unpack('!I', message[7:11])[0]
        pId = message[11]
        tId = message[12]
        zone = self.world.zoneWithId[zId]

        if tId == '\x00':
            # Zone rendered neutral
            turret = "F"
            if zone.turretedPlayer:
                turret = "T" + zone.turretedPlayer.id
            zone.tag(None, None)
            message += turret
            self.broadcastUdp(message)
            
        else:
            
            team = self.world.teamWithId[tId]
            player = self.world.playerWithId[pId]

            if zone.orbOwner == team:
                # The player may have incorrect data; send
                # all data pertaining to zones, to that client.
                self.validateZones(address)
            elif player.dead:
                # It seems to think that it's alive.
                self.validatePlayers(address)

            else:
                turret = "F"
                if zone.turretedPlayer:
                    turret = "T" + zone.turretedPlayer.id
                    turretPlayer = self.world.playerWithId[zone.turretedPlayer.id]
                    turretIP = self.players[zone.turretedPlayer.id].ipAddr
                    self.addStat('starsWasted', turretIP, turretPlayer.nick, turretPlayer.stars)                    
                starsBefore = player.stars
                if zone.tag(team, player):
                    starsAfter = player.stars
                    # Validate total number of team's zones:
                    message += struct.pack('!I', team.numOrbsOwned)
                    
                    # Validate tagger's total number of stars
                    message += struct.pack('B', player.stars)
                    
                    message += turret

                    self.addStat('zoneTags', address[0], player.nick)
                    if starsAfter > starsBefore:
                        self.addStat('starsEarned', address[0], player.nick)
                    
                    self.broadcastUdp(message)
                else:
                    # Zone tagging failed due to incorrect number of players
                    # within. Ask all players for a zone update; the zone tag
                    # request will probably be sent again anyway if it is valid.
                    for player in self.world.playerWithId.values():
                        self.pingForZone(player)
                        

    def respawn(self, message, address):
        # Protocol for respawn
        #
        # First 4 characters: "Resp"
        # 5th Character: ID of player wanting to respawn
        # 6th Character: Zone that the player is currently in
        #
        # If all data is valid, the message is re-broadcast, unaltered
        
        if self.world.gameState == GameState.PreGame:
            return
        pId = message[4]
        player = self.world.playerWithId[pId]
        
        zId = struct.unpack('!I', message[5:9])[0]
        zone = self.world.zoneWithId[zId]
        if zone.orbOwner == player.team:
            # Ensure they're recorded as being in the right zone
            player.changeZone(zone)
            player.respawn()
            self.broadcastUdp(message)
        else:
            # client has incorrect information: send them zone information
            self.validateZones(address)
            pass

    def startTransaction(self, message, address):
        # Protocol for startTransaction
        #
        # First 5 Characters: "Trans"
        # 6th Character: Team for which to start the transaction
        # 7th Character: Purchasing player
        # 8th Character: Number of stars to start off with
        # 9th Character: ID of type of upgrade being purchased
        #
        # If all data checks out, the message is re-broadcast, with the
        # time remaining for the upgrade appended onto the end.
        
        tId = message[5]
        pId = message[6]
        stars = struct.unpack('B', message[7])[0]
        upgradeType = message[8]
        team = self.world.teamWithId[tId]
        if team.currentTransaction is not None:
            # They must not know that there's already a transaction in play.
            self.validateTransaction(team, address)
        
        else:
            player = self.world.playerWithId[pId]
            if player.upgrade:
                # That player already has an upgrade. They cannot start a
                # new transaction
                self.validateUpgrades(address)
            else:
                upgrade = upgrades.upgradeOfType[upgradeType]
                try:
                    trans = ServerTransaction(team, player, upgrade)
                    # Be alerted when the number of stars changes:
                    def NumStarsChanged(trans, player, stars):
                        self.sendTransactionUpdate(trans.purchasingTeam,'s', player,stars)
                    trans.onNumStarsChanged.addListener(NumStarsChanged)

                    # Be alerted when the transaction state changes:
                    def TransactionStateChanged(trans, state):
                        d = {TransactionState.Completed : 'c',
                             TransactionState.Abandoned : 'a'}
                        self.sendTransactionUpdate(trans.purchasingTeam, d[state])
                    trans.onStateChanged.addListener(TransactionStateChanged)
                        
                    timeLeft = struct.pack('f', trans.timeLimit)
                    datagram = message + timeLeft
                    trans.addStars(player, stars)
                    # It may not be open, because it may have been completed in one go.
                    if trans.state == TransactionState.Open:
                        self.broadcastUdp(datagram, team)
                    
                except ValueError:
                    # Client must not have valid star counts
                    self.validateStars(address)
    # Fixme: need that xVel bit added

    def addStars(self, message, address):
        # Protocol for addStars
        #
        # First 8 Characters: "AddStars"
        # 9th Character: Team for which to add the star
        # 10th Character: Contributing Player's ID
        # 11th Character: Number of stars being contributed
        #
        # The message is not re-broadcast. The transaction itself manages
        # rebroadcasting the message with correct values.
        tId = message[8]
        team = self.world.teamWithId[tId]
        transaction = team.currentTransaction
        if not transaction:
            # They think there's a transaction when there's not.
            # Tell them to abandon it.
            self.sendTransactionUpdate(team, 'a', address = address)
            # Also, since they probably missed the 'Transaction Complete'
            # message they may have incorrect details about stars and
            # players' upgrades. Send that too.
            self.validateStars(address = address)
            self.validateUpgrades(address = address)
            return
        pId = message[9]
        player = self.world.playerWithId[pId]
        stars = struct.unpack('B', message[10])[0]
        transaction.addStars(player, stars)

    def abandonTransaction(self, message, address):
        # FIXME: should we do a check to make sure it is the purchasingPlayer
        # that abandons?
        
        # Protocol for abandonTransaction
        # 
        # First 7 Characters: "Abandon"
        # 8th Character: Team ID for which to abandon the transaction
        tId = message[7]
        team = self.world.teamWithId[tId]
        transaction = team.currentTransaction
        transaction.abandon()
            
    def sendTransactionUpdate(self, team, update, player = None,
                              stars = None, address = None):
        '''Should be called with update being:
        'a': abandon transaction
        'c': complete transaction
        's': add stars to transaction
        (removing stars from a transaction is done automatically client-side)'''
        # Protocols for sendTransactionUpdate
        #
        # Add Stars:
        #   First 8 characters: "AddStars"
        #   9th character: Team ID for which to add stars to the transaction
        #   10th character: ID of the contributing player
        #   11th character: the number of stars that this player contributed
        #   12th character: the number of stars contributed to this transaction
        #                   in total
        # 
        # Abandon:
        #   First 7 characters: "Abandon"
        #   8th character: Team ID for which to abandon the transaction
        # 
        # Complete:
        #   First 8 characters: "Complete"
        #   9th character: Team ID for which to complete the transaction
        #   10th character: ID of the purchasing player
        #   11th character: upgrade ID
        #   12th character: the number of contributions that have been made
        #   13th onwards: For each player that has contributed to this
        #                 transaction
        #     1st Character: The player's ID
        #     2nd Character: The number of stars that this player currently has
        
        transaction = team.currentTransaction
        tId = team.id
        if update == 's':
            numStars = struct.pack('B', stars)
            pId = player.id
            totalStars = struct.pack('B', transaction.totalStars)
            message = 'AddStars' + tId + pId + numStars + totalStars
            
        elif update == 'a':
            message = 'Abandon' + tId
            
        elif update == 'c':
            # Transaction is complete: send all contribution
            # data to ensure everyone has correct info about it.
            numItems = struct.pack('B', len(transaction.contributions))
            message = 'Complete' + tId + transaction.purchasingPlayer.id + \
                      transaction.upgrade.upgradeType + numItems
                             
            for player in transaction.contributions.iterkeys():
                ipAddr = self.players[player.id].transport.getPeer().host
                stars = transaction.contributions[player]
                contributor = self.world.playerWithId[player.id]

                self.addStat('starsUsed', ipAddr, contributor.nick, increase = stars)
                
                message += player.id
                # Send player's current number of stars to avoid propogating
                # errors in calculation
                message += struct.pack('B', player.stars)

        # Send the message
        if address:
            self.udpProtocol.send(message, address)
        else:
            self.broadcastUdp(message, team)
            # Send completion messages to enemy as well
            if update in ('c', 'a'):
                self.broadcastUdp(message, team.opposingTeam)

    def useUpgrade(self, message, address):
        '''Received from a client when their player wants to use an upgrade'''
        # Protocol for useUpgrade
        #
        # First 7 characters: "UseUpgr"
        # 8th character: ID of player wanting to use their upgrade
        # Characters 9-16: position of the player as they use it
        # Characters 17-20: the player's current Zone
        # Character 21: the ID of the type of upgrade
        # If the data received from the client checks out, then the message is
        # re-broadcast to all clients; otherwise an upgrade validation is sent
        # to the originating player.
        
        pId = message[7]
        player = self.world.playerWithId[pId]
        pos = struct.unpack('ff', message[8:16])
        upgradeType = message[20]
        if player.dead:
            self.validatePlayers(address)
        if player.upgrade and player.upgrade.upgradeType == upgradeType and \
           not player.upgrade.inUse:
            if isinstance(player.upgrade, upgrades.Turret):
                zId = struct.unpack('!I', message[16:20])[0]
                zone = self.world.zoneWithId[zId]
                player.changeZone(zone)
            if player.upgrade.serverUse():
                # Tell the clients
                self.broadcastUdp(message)
        else:
            self.validateUpgrades(address)

    def receiveDeleteUpgrade(self, message, address):
        # Protocol for receiveDeleteUpgrade
        #
        # First 7 characters: "DelUpgr"
        # 8th character: ID of the player whose upgrade is to be deleted
        # 9th character: ID of the type of upgrade being deleted
        #
        # If the information about the upgrade being sent is valid, then
        # sendDeleteUpgrade; otherwise validate the upgrades for that player.
        
        pId = message[7]
        player = self.world.playerWithId[pId]
        upgradeType = message[8]
        if player.upgrade and player.upgrade.upgradeType == upgradeType:
            player.upgrade.serverDelete()
            self.sendDeleteUpgrade(pId)
        else:
            self.validateUpgrades(address)

    def sendDeleteUpgrade(self, pId):
        # Protocol for sendDeleteUpgrade
        #
        # First 7 characters: "DelUpgr"
        # 8th character: ID of the player whose upgrade should be deleted

        self.broadcastUdp('DelUpgr' + pId)
        
    
    def validateTransaction(self, team, address, tcp = False):
        '''Lets the client know all details about the team's transaction'''
        # Protocol for validateTransaction
        #
        # First 7 characters: "ValTran"
        # If there is a transaction in progress:
        #   Character 8: The ID of the team
        #   Character 9: The ID of the purchasing player
        #   Character 10: The ID of the type of upgrade being purchased
        #   Characters 11-14: The amount of time left before the transaction is
        #                     automatically abandoned
        #   Character 15: The number of contributions to the transaction
        #   For each contribution:
        #     Character 1: Contributor's ID
        #     Character 2: Number of stars contributed

        # TODO: work out why I wrote "if tcp" - AshleyDonaldson
        if tcp or team.hasAddress(address):
            transaction = team.currentTransaction
            tId = team.id
            if not transaction:
                # Let client know that there is no transaction in progress
                message = 'ValTran' + '\x00' + tId
            else:
                totalStars = struct.pack('B', transaction.totalStars)
                pId = transaction.purchasingPlayer.id
                upgrade = transaction.upgrade.upgradeType
                timeLeft = struct.pack('f', transaction.age())
                numItems = struct.pack('B', len(transaction.contributions))
                message = 'ValTran' + tId + pId + totalStars + numItems + \
                          timeLeft + upgrade
                          
                for contribution in transaction.contributions.iteritems():
                    message += contribution[0].id
                    message += struct.pack('B', contribution[1])
            if tcp:
                address.sendString(message)
            else:
                self.udpProtocol.send(message, address)

    def validatePlayers(self, address, tcp = False):
        '''Sends a validation of all important data about all players'''
        # Protocol for validatePlayers:
        #
        # First 10 characters: "ValPlayers"
        # 11th character: number of players in the game
        # 12th character onwards:
        #     For each player in the game:
        #         Characters 1-4: how many bytes this individual player's
        #                        validation is going to take
        #         5th character: the player's ID
        #         6th character: The player's team's ID
        #         7th character: The player's number of stars
        #         Characters 8-11: The player's current zone
        #         12th Character: If the player is dead, then 'T', otherwise 'F'
        #         Characters 13-16: The number of bytes used to send the player's
        #                          nick
        #         Characters 17->: The player's nick
        
        numPlayers = struct.pack('B', len(self.world.playerWithId))
        message = 'ValPlayers' + numPlayers
        for player in self.world.playerWithId.itervalues():
            pMsg = player.id
            pMsg += player.team.id
            pMsg += struct.pack('B', player.stars)
            pMsg += struct.pack('!I', player.currentZone.id)
            if player.dead:
                pMsg += 'T'
            else:
                pMsg += 'F'
            pMsg += marshal.dumps(player.nick)

            # Add this to the message with an identifier for length.
            message += struct.pack('!I', len(pMsg)) + pMsg
            
        if tcp:
            address.sendString(message)
        else:
            self.udpProtocol.send(message, address)

    def validateZones(self, address = None, player = None, tcp = False):
        '''Sends a validation of zone ownership'''
        # Protocol for validateZones
        #
        # First 8 characters: "ValZones"
        # Characters 9-12: the number of zones in existance
        # Characters 13 onwards:
        #     For each zone, the following information is sent:
        #         Characters 1-4: The ID of the zone
        #         Character 5: either 'A', 'B', or '\x00', depending on who
        #         owns the orb
        #         Character 6: either 'A', 'B', or '\x00', depending on who
        #         owns the zone
        
        numZones = struct.pack('!I', len(self.world.zoneWithId))
        message = 'ValZones' + numZones
        for zone in self.world.zoneWithId.itervalues():
            message += struct.pack('!I', zone.id)
            if zone.orbOwner == None:
                message += '\x00'
            else:
                message += zone.orbOwner.id
            if zone.zoneOwner == None:
                message += '\x00'
            else:
                message += zone.zoneOwner.id
                
        # Find the address to send it to:
        if not address:
            address = (self.players[player.id].transport.getPeer().host, \
                       self.players[player.id].clientUdpPort)
        if tcp:
            address.sendString(message)
        else:
            self.udpProtocol.send(message, address)
    
    def validateStars(self, player = None, address = None):
        '''Sends a validation of the number of stars each player has'''
        # Protocol for validateStars
        #
        # First 8 characters: "ValStars"
        # 9th character: the number of players currently in the game
        # 10th character onwards:
        #     For each player, send data thus:
        #         1st Character: The ID of the player
        #         2nd Character: The number of stars this player has
        
        numPlayers = struct.pack('B', len(self.world.playerWithId))
        message = 'ValStars' + numPlayers
        for player in self.world.playerWithId.itervalues():
            message += player.id
            message += struct.pack('B', player.stars)


        # Find the address to send it to:
        if not address:
            address = (self.players[player.id].transport.getPeer().host, \
                       self.players[player.id].clientUdpPort)
        self.udpProtocol.send(message, address)

    def validateUpgrades(self, address = None, player = None, tcp = False):
        '''Sends all current upgrade details to a player, either over TCP or
        UDP'''
        # Protocol for validateUpgrades
        #
        # First 7 characters: "ValUpgr"
        # 8th character: the current number of upgrades in play
        # 9th character onwards: Each upgrade's details in order
        # 
        # For each upgrade, information is sent thus:
        #    1st Character: The ID of the player with the upgrade
        #    2nd Character: The character representing which upgrade it is
        #                   (i.e. 's' = Shield, 't' = Turret)
        #    3rd Character: If the upgrade is in use, then 'T', otherwise 'F'
        #    If the upgrade is a Turret, and it is in use, then also send the
        #       Zone to which the turret is attributed (4 more characters)
        
        numUpgrades = 0
        upgradeMsg = ''
        for player in self.world.playerWithId.values():
            if player.upgrade:
                numUpgrades += 1
                upgradeMsg += player.id
                upgradeMsg += player.upgrade.upgradeType
                if player.upgrade.inUse:
                    upgradeMsg += 'T'
                else:
                    upgradeMsg += 'F'
                if isinstance(player.upgrade, upgrades.Turret) and \
                   player.upgrade.inUse:
                    upgradeMsg += struct.pack('!I', player.currentZone.id)
        message = 'ValUpgr' + struct.pack('B', numUpgrades) + upgradeMsg
        
        # Find the address to send it to:
        if not address:
            address = (self.players[player.id].transport.getPeer().host, \
                       self.players[player.id].clientUdpPort)
        if tcp:
            address.sendString(message)
        else:
            self.udpProtocol.send(message, address)

    def receiveZoneChange(self, message, address):
        '''Received from a player when they change zones'''
        # Protocol for receiveZoneChange:
        # First 6 characters: "ZoneCh"
        # 7th character: ID of the player this update concerns
        # Characters 8-11: ID of the zone the player is in
        # 
        # The message is re-broadcast unaltered
        
        pId = message[6]
        zId = struct.unpack('!I', message[7:11])[0]
        player = self.world.playerWithId[pId]
        zone = self.world.zoneWithId[zId]
        player.changeZone(zone)
        self.broadcastUdp(message)

    def sendAllValidation(self, tcpConnection):
        self.validatePlayers(tcpConnection, tcp = True)
        self.validateZones(tcpConnection, tcp = True)
        self.validateUpgrades(tcpConnection, tcp = True)
        self.validateGameStatus(tcpConnection)
        self.sendGameMode(tcpConnection)

    def receiveChat(self, message, address):
        # Protocol for receiveChat:
        # First 4 characters: "Chat"
        # 5th character: player ID sending the chat
        # Characters 6-9: either "Team", "Priv" or "Open", designating
        #                 the privacy of the message; either to the entire team,
        #                 a private message between 2 people, or a chat to
        #                 everyone
        # 10th character: If the chat is to a team, it will designate the team
        #                 to which it should be sent
        #                 If the chat is a private message, it will designate
        #                 the player to whom the message is being sent
        # Subsequent characters: The message being sent
        #
        # Assuming the profanities filter doesn't pick up anything, the message
        # is sent unaltered to anyone it concerns

        player = self.world.playerWithId[message[4]]
        messageType = message[5:9]
        try:
            self.filterProfanities(message[9:])
        except Profanity, e:
            # Kick the player based on server settings; or give them a warning?
            print e, 'in message from %s' % (player.nick)
        else:
            if message[9:12] == "```" or message[10:13] == "```":
                if message[9:12] == "```":
                    command = message[12:]
                else:
                    command = message[13:]
                print "Got server command via chat from %s: %s" % (player.nick, command)
                self.cmdProtocol.datagramReceived(command, ("127.0.0.1", 0))
            elif message[9:12] == "@@@" or message[10:13] == "@@@":
                if message[9:12] == "@@@":
                    command = message[12:]
                else:
                    command = message[13:]
                print "Got info request via chat from %s" % player.nick
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
                        messages.append("Team%s has a transaction:" % teamID)
                        messages.append("- Current state: %s" % transText[transaction.state])
                        messages.append("- %s being purchased by %s" % (repr(transaction.upgrade), transaction.purchasingPlayer.nick))
                        messages.append("- %s/%s stars" % (transaction.totalStars, transaction.requiredStars))
                        messages.append("- Contributions: %s" %   transaction.contributions)
                    else:
                        messages.append("Team%s has no transaction." % teamID)

                    print "\n".join(messages)
                    
                    playerId = message[4]
                    for messageStr in messages:
                        sendAddress = (self.players[playerId].transport.getPeer().host, \
                        self.players[playerId].clientUdpPort)
                        self.udpProtocol.send("Chat" + playerId + "Open@@@" + messageStr, sendAddress)    
                        
            elif messageType == 'Team':
                teamId = message[9]
                team = self.world.teamWithId[teamId]
                self.broadcastUdp(message, team, address)
            elif messageType == 'Priv':
                playerId = message[9]
                # Find the address to send it to:
                sendAddress = (self.players[playerId].transport.getPeer().host, \
                           self.players[playerId].clientUdpPort)
                self.udpProtocol.send(message, sendAddress)
            elif messageType == 'Open':
                self.broadcastUdp(message, nonSending = address)

    def filterProfanities(self, message):
        '''Raises an error if there are profanities contained in the message'''
        profanities = ()
        for profanity in profanities:
            if message.__contains__(profanity):
                raise Profanity, 'Profanity Alert'

    def gameStart(self):

        # Protocol for gameStart
        #
        # First 9 characters: "GameStart"
        # Characters 10-17: The duration of the game
        
        print 'Game Starting Now'
        message = 'GameStart' + struct.pack('d', self.world.gameTimeLimit)
        self.broadcastTcp(message)

    def gameOver(self, winningTeam = None, timeOver = False):
        # Protocol for gameOver
        #
        # First 6 Characters: "Winner"
        # Character 7: The ID of the winning Team ('\x00' if a draw)
        # Character 8: If the game time expired, 'T', otherwise 'F'
        self.world.gameState = GameState.Ended
        self.world.winner = winningTeam

        if timeOver:
            print "Game time limit expired."
        else:
            print "Game is over. "
        if winningTeam is not None:
            print winningTeam, "has won."
        else:
            print "The game resulted in a draw"
            
        message = 'Winner'
        if winningTeam is not None:
            message += winningTeam.id
        else:
            message += '\x00'
        if timeOver:
            message += 'T'
        else:
            message += 'F'

        self.world.gameOverTime = timeNow()
        
        self.broadcastTcp(message)

    def teamReady(self, datagram, address):
        '''Called when a player says their team is ready. Note that if that
        player is not the captain of the team, this method will not change
        anything.'''
        # Protocol for teamReady:
        # First 5 characters: "Ready"
        # 6th character: player ID of the person saying their team is ready
        pId = datagram[5]
        player = self.world.playerWithId[pId]
        if player.team.teamReady(player):
            self.broadcastTcp(datagram)
        else:
            self.validateGameStatus(address)
        if self.world.checkStart():
            self.startSoon()

    def startSoon(self, reason = None, delay = 7):
        self.sendGameStarting(delay)
        reactor.callLater(delay, self.world.gameStart)
        

    def makeCaptain(self, datagram, address):
        '''Called when a player nominates themself as the captain of a team.
        If that team does not already have a captain, they are made captain
        instantly; all it really means is that they can say when their team
        is ready.'''
        # Protocol for makeCaptain:
        # First 7 characters: "Captain"
        # 8th character: player ID of the captain nominee
        if self.noCaptains:
            return
        
        pId = datagram[7]
        player = self.world.playerWithId[pId]
        if player.team.makeCaptain(player):
            self.broadcastTcp(datagram)
        else:
            self.validateGameStatus(address)

    def validateGameStatus(self, address = None):
        '''Sends a validation of things pertaining to the general running
        of the game at a fairly high level'''
        # Protocol for validateGameStatus
        #
        # First 8 Characters: "ValGStat"
        # 9th character: 'P' if in pre-game state, 'I' if game is in progress,
        #                'E' if the game has ended.
        # 10th character: 'T' if the game is time-limited, 'F' otherwise
        # Next 8 Characters: The time left in the game (only if game is In
        #                    Progress and time-limited)
        # For each team:
        #   -> The team's ID
        #   -> If the team has a captain, then 'T'; otherwise 'F'
        #   -> If the team has a captain, then the ID of that player
        #   -> If the team is ready, 'T'; otherwise 'F'
        #   -> Next 4 bytes: The number of orbs owned by this team
        #   -> The number of players on this team
        #   -> If the team is in a transaction, then 'T'; otherwise 'F'
        
        message = 'ValGStat'
        if self.world.gameState == GameState.PreGame:
            char = 'P'
        elif self.world.gameState == GameState.InProgress:
            char = 'I'
        else:
            char = 'E'
        message += char
        if self.world.gameTimeLimit == 0:
            message += 'T'
        else:
            message += 'F'
        if self.world.timeLeft() != None:
            message += struct.pack('d', self.world.timeLeft())

            ## Some stuff to help testing:
            if char != 'I':
                print "networkServer.py: validateGameStatus"
                print "Game Countdown is on (%f left), yet gameState is '%s'" % (self.world.timeLeft(), char)
        #else:
            #if char == 'I':
                #print "networkServer.py: validateGameStatus"
                # This state is usually because a game has no time limit set.
                #print "TimeLeft is None, yet game in 'in progress'?"
                
        for team in self.world.teams:
            message += team.teamString()

        if address:
            address.sendString(message)
        else:
            self.broadcastTcp(message)

    def sendGameStarting(self, time):
        message = 'About2Start' + struct.pack('!d', time)
        self.broadcastTcp(message)

    def sendServerMessage(self, string, tcpAddress = None, ):
        '''Sends a message to all clients, or to a single client'''
        # Protocol for sendServerMessage:
        #
        # First 6 characters: "SvrMsg"
        # Onwards: the message to send
        
        message = "SvrMsg" + string
        if tcpAddress:
            tcpAddress.sendString(message)
        else:
            self.broadcastTcp(message)

    def captainGone(self, team):
        '''Called when a team's captain leaves the game'''
        # TODO: send a server message too?
        self.validateGameStatus()

    def setGameMode(self, newMode):
        return self.world.setGameMode(newMode)
        
    def sendGameMode(self, address = None):
        message = "GameMode" + self.world.gameMode
        if address:
            address.sendString(message)
        else:
            self.broadcastTcp(message)

    def kick(self, pId):
        if self.world.playerWithId.has_key(pId):
##            # Their connection:
##            (self.players[pId].transport.getPeer().host, \
##                       self.players[pId].clientUdpPort)
            self.removePlayer(pId)
            
    def disableCaptains(self):
        self.noCaptains = True
        print 'Disabling captains...',
        for team in self.world.teams:
            team.captain = None
        print 'done'
        
    def changeTeamName(self, team, newName):
        '''Received when the name of a team is changed via
        the server admin interface.'''
        # Protocol for changeTeamName:
        #
        # First 8 characters: "TeamName"
        # 9th character: ID of the team
        # 10th character onwards: New name of the team
        
        message = "TeamName" + team + newName
        print "Team" + team + "'s name is now " + newName
        self.world.teams[int(team)].teamName = newName
        self.broadcastTcp(message)

    def shutdown(self):
        # Send Shutdown message to all clients.
        self.broadcastTcp("Shutdown")
        # Fixes an odd bug in which a single extra packet gets broadcast
        # after closing a replay
        if self.replay:
            self.replayTimes = []

        # Stop CmdServer. Server should no longer respond to admin commands.
        if self.cmdProtocol is not None:
            self.cmdProtocol.port.stopListening()

        if self.udpMulticaster is not None:
            # Stop UDPMulticastServer. Server should disappear from server list.
            self.udpMulticaster.transport.leaveGroup(multicastGroup)
            self.udpMulticaster.transport.stopListening()
            self.udpMulticaster = None

        # Stop UDPServer. Server should no longer respond to UDP.
        self.udpProtocol.port.stopListening()
        # Stop TCPFactory. Server should no longer respond to TCP.
        self.tcpFactory.port.stopListening()
        # Kill server
        #reactor.stop()
        self.running = False

if __name__ == '__main__':
    print 'Starting Trosnoth server.'
    # TODO: argv stuff?
    ns = NetworkServer('Trosnoth Server', 6789)
    try:
        reactor.run()
    finally:
        print "Server crashed"
    
