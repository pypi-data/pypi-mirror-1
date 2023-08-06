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

import twisted.internet
from twisted.internet import defer, reactor
from twisted.internet.protocol import ClientFactory, DatagramProtocol
from twisted.protocols.basic import Int32StringReceiver
from random import choice, random
from math import pi

import struct
import marshal

from trosnoth.src.utils.unrepr import unrepr

import trosnoth.src.universe as universe
from trosnoth.src.upgrades import Turret, upgradeOfType, upgradeNames
from trosnoth.src.universe_base import GameState
from trosnoth.src.networkDefines import *
import trosnoth.src.mapLayout as mapLayout
import trosnoth.src.utils.logging as logging
import trosnoth.src.transaction as transactionModule

from trosnoth.src.utils.utils import timeNow

from trosnoth.src.trosnothgui.ingame import colours

# TODO: Define some exception classes and use them instead of Exception

# TODO: Disable doing anything until all clients have received the TCP message
# indicating that the player has joined. This will ensure that there are no
# keyErrors when for searching for players.
#  * Not sure about that one - requires further discussion. -- JoshBartlett.

# TODO: Try...except around player indexing calls

# TODO: ensure all messages sent to the interface class are relevant to the
# target (such as "transaction completed". maybe interface class can manage
# that.)

class TCPClient(Int32StringReceiver):
    def __init__(self, client, udpPort):
        self.client = client
        self.connected = False
        self.validated = False
        self.waitingPlayers = {}
        self.cancelingPlayers = []
        self.udpPort = udpPort
        
    def connectionMade(self):
        print 'Client: connected to server'
        self.connected = True
        # When we connect tell the server how we can be reached by UDP, what
        # version we are, and ask for the world.
        self.sendString('TrosnothRequestSettings:%s' % (struct.pack('!I', \
                      self.udpPort.getHost().port) + clientVersion))

        

    def connectionLost(self, reason):
        print 'Client: lost connection to server'
        self.connected = False
        self.validated = False
        self.factory.protocol = None
        self.client.tcpConnectionLost()
        
    def stringReceived(self, line):
        try:
            # First check for server response if still connecting.
            if not self.validated:
                if line.startswith('TrosnothBadVersion:'):
                    serverVersion = line[19:]
                    raise Exception, 'Trosnoth server version ' + serverVersion + \
                          ' is not compatible with this client version (' + \
                          clientVersion + ')'
                elif line.startswith('TrosnothInitClient:'):
                    # Settings from the server.
                    settings = line[19:]
                    settings = unrepr(settings)
    ##                try:
    ##                    settings = unrepr(settings)
    ##                except:
    ##                    raise Exception, 'Server sent invalid settings info'

                    # Tell the client that the connection has been made.
                    self.validated = True
                    self.client.gotSettings(settings)

                    # Write the server string for the sake of debug logs.
                    print 'Joined game: <%s>' % settings['serverString']
                else:
                    # Don't recognise reply while connecting.
                    self.transport.loseConnection()
                    raise Exception, 'Server is not Trosnoth server'
            else:
                msg = line[:5]
                world = self.client.world
                if msg == 'NewP:':
                    # Server announcing new player.
                    playerId = line[5]
                    teamId = line[6]
                    zoneId = struct.unpack('!I', line[7:11])[0]
                    nick = marshal.loads(line[11:])

                    team = self.client.world.teamWithId[teamId]
                    zone = self.client.world.zoneWithId[zoneId]
                    # Create the player.
                    universe.Player(self.client.world, nick, team, playerId, zone,
                                    dead = True)
                    if self.client.interface:
                        message = "%s has joined the game" % (nick)
                        self.client.interface.newMessage(message)
                elif msg == 'OwnP:':
                    # Server gives this player to me.
                    playerId = line[5]
                    player = world.playerWithId[playerId]

                    player.makeLocal()

                    # Now check if this player was in our waiting list.
                    if (player.team, player.nick) in self.cancelingPlayers:
                        self.leave(playerId)
                        self.cancelingPlayers.remove((player.team, player.nick))
                    else:
                        try:
                            deferred = self.waitingPlayers[player.team, player.nick]
                            # Fire the deferred's callbacks.
                            deferred.callback(('success', player))
                        except KeyError:
                            logging.writeException()
                        
                elif msg == 'NotP:':
                    print 'Message is',line
                    # Server says that it can't create a player.
                    reasonID = line[5]
                    teamId = line[6]
                    if reasonID == 'W':
                        decimal = line.find(".")
                        nickStart = decimal + 2
                        timeLeft = line[7:nickStart]
                    else:
                        nickStart = 7

                    try:
                        nick = marshal.loads(line[nickStart:])
                    except:
                        logging.writeException()
                        return
                    
                    # Find the deferred and call its ErrBack.
                    
                    try:
                        deferred = self.waitingPlayers[world.teamWithId[teamId], nick]
                    except KeyError:
                        logging.writeException()
                        return
                    
                    if reasonID == 'F':
                        deferred.callback(['full'])
                    elif reasonID == 'O':
                        deferred.callback(['over'])
                    elif reasonID == 'W':
                        deferred.callback(['wait', timeLeft])
                    else:
                        deferred.callback(['unknown reason code: %s' % reasonID])
                    
                elif msg == 'DelP:':
                    # Server says this player has left the game.
                    playerId = line[5]
                    try:
                        player = world.playerWithId[playerId]
                    except KeyError:
                        # TODO: Handle this sensibly.
                        logging.writeException()
                        return
                    
                    player.removeFromGame()
                    if self.client.interface:
                        message = "%s has left the game" % (player.nick)
                        self.client.interface.newMessage(message)

                elif line.startswith('GameStart'):
                    # The game has progressed from its pre-game state, to being
                    # in progress.
                    time = struct.unpack('d', line[9:17])[0]
                    world.gameStart(time)
                    if self.client.interface:
                        message = "The game is now on!!"
                        self.client.interface.newMessage(message)
                        if self.client.interface.gameInterface.gameViewer.timerBar:
                            self.client.interface.gameInterface.gameViewer.timerBar.loop()
                        # Since we're reaching this far in anyway, let's put good design on hold for now.
                        self.client.interface.gameInterface.gameViewer.pregameMessage.setText('')

                elif line.startswith('Winner'):
                    # A team has won the game.
                    tId = line[6]
                    if tId == '\x00':
                        winningTeam = None
                    else:
                        winningTeam = self.client.world.teamWithId[tId]
                    timeOver = line[7] == 'T'
                    if self.client.interface:
                        self.client.interface.gameOver(winningTeam)
                        if timeOver:
                            message2 = "Game Time Limit has expired"
                            self.client.interface.newMessage(message2)
                        if self.client.interface.gameInterface.gameViewer.timerBar:
                            self.client.interface.gameInterface.gameViewer.timerBar.gameFinished()

                    world.gameOver()

                elif line.startswith('GameMode'):
                    mode = line[8:]
                    world.setGameMode(mode)

                elif line.startswith("TeamName"):
                    teamID = int(line[8])
                    newName = line[9:]
                    self.client.world.teams[teamID].teamName = newName

                elif line.startswith("Shutdown"):
                    print "Server shutting down."
                    self.disconnect()
                
                else:
                    # Check to see if the message is recognised by udp
                    # TODO: find a better way to do this
                    self.client.udpClient.datagramReceived(line, None)
        except:
            # So that receiving a network message will never cause a crash.
            logging.writeException()

    def disconnect(self):
        'Call this to disconnect from the server.'
        self.transport.loseConnection()
        self.interface = None

    def join(self, nick, team, deferred):
        'Call this to request that the server add a new player to the game.'
        if not self.validated:
            # FIXME: (maybe) shouldn't result be initialised? I could be wrong.
            result.errback(Exception('Cannot join before connection is in place'))
        else:
            self.sendString('Join:%s%s' % (team.id, marshal.dumps(nick)))
            # TODO: Maybe check if we've already got a waiting request for this
            # team and nick.
            self.waitingPlayers[team, nick] = deferred

    def leave(self, playerId):
        if not self.validated:
            result.errback(Exception('Cannot leave before connection is in place'))
        else:
            self.sendString('Leev:%s' % playerId)
    
    def cancelJoin(self, nick, team):
        try:
            deferred = self.waitingPlayers[team, nick]
        except KeyError:
            # Can't cancel player.
            logging.writeException()
            return

        self.cancelingPlayers.append((team, nick))
        reactor.callLater(1, self.justCancelJoin, deferred, (team, nick))
        
        del self.waitingPlayers[team, nick] 

    def justCancelJoin(self, joinDeferred, key):
        # If callback has not already been fired, do so now.
        joinDeferred.callback(['cancel'])
        try:
            self.cancelingPlayers.remove(key)
        except ValueError:
            pass

        
class TCPClientFactory(ClientFactory):
    def __init__(self, client, udpPort):
        self.client = client
        self.protocol = None
        self.udpPort = udpPort
        
    def startedConnecting(self, connector):
        pass

    def buildProtocol(self, addr):
        if self.protocol:
            raise Exception, 'Client TCP factory only supports single connection'
        result = TCPClient(self.client, self.udpPort)
        result.factory = self
        self.protocol = result
        return result
        
    def clientConnectionLost(self, connector, reason):
        pass
        
    def clientConnecitonFailed(self, connector, reason):
        pass
    
class UDPClient(DatagramProtocol):
    def __init__(self, client, port=0):
        self.client = client
        self.port = reactor.listenUDP(port, self)
        
    def datagramReceived(self, datagram, address):
        '''This method is called when a datagram is received. It will interpret
        the message, and instruct the networkClient object'''

        # print "receive: " + datagram
        
        # A server tells us that it exists
        if datagram.startswith('Trosnoth:Server:'):
            tcpPort = struct.unpack('!I', datagram[16:20])[0]
            self.client.addServer(datagram[20:], tcpPort, address)

        # Shot fired
        elif datagram.startswith('Shot'):
            
            pId = datagram[4]
            sId = datagram[5]
            angle = struct.unpack('f', datagram[6:10])[0]
            pos = struct.unpack('ff', datagram[10:18])
            turret = datagram[18] == 'Y'

            self.client.receiveShotFired(pos, angle, pId, sId, turret)
            # FIXME: Once the grenade no longer uses the Shot message, this
            #       line can be put back in. Currently this line will cause
            #       an apparent glitch when a grenade explodes.
            # self.client.positionUpdate(pId, pos, angle = angle)                        


        # Player Killed
        elif datagram.startswith('Kill'):
            pId = datagram[4]
            kId = datagram[5]
            sId = datagram[6]
            pos = struct.unpack('ff', datagram[7:15])
            stars = struct.unpack('B', datagram[15])[0]
            
            self.client.receivePlayerKilled(pId, kId, sId)
            self.client.positionUpdate(pId, pos)
            killer = self.client.world.playerWithId[kId]
            self.client.world.updateStars(killer, stars)


        # Shot has been destroyed
        elif datagram.startswith('KShot'):
            pId = datagram[5]
            sId = datagram[6]
            shot = self.client.world.shotWithId(pId, sId)
            
            if shot:
                shot.kill()


        # Receive a player update
        elif datagram.startswith('PlUpd'):
            pId = datagram[5]
            try:
                player = self.client.world.playerWithId[pId]
            except:
                # Mustn't have that info yet
                return
            if not player.local:
                pos = struct.unpack('ff', datagram[6:14])
                yVel = struct.unpack('f', datagram[14:18])[0]
                indices = list(struct.unpack('!II', datagram[18:26]))
                angle = struct.unpack('f', datagram[26:30])[0]
                inc = 30
                for i in ('left', 'right', 'jump', 'down'):
                    value = (datagram[inc] == "T")
                    player.updateState(i, value)
                    inc += 1
                upgr = datagram[inc] == 'T'
                if not ((upgr and player.upgrade) or \
                   not (upgr or player.upgrade)):
                    self.client.requestUpgrades()
                dead = datagram[inc + 1] == 'T'
                if dead != player.ghost:
                    if player.ghost:
                        player.respawn()
                    else:
                        player.die()
                self.client.positionUpdate(pId, pos, indices, yVel, \
                                           angle = angle)


        # Zone has been tagged
        elif datagram.startswith('TagZone'):
            zId = struct.unpack('!I', datagram[7:11])[0]
            pId = datagram[11]
            tId = datagram[12]

            zone = self.client.world.zoneWithId[zId]
            if tId == '\x00':
                self.client.receiveZoneTagged(None, None, zone)
            else:
                team = self.client.world.teamWithId[tId]
                player = self.client.world.playerWithId[pId]
                self.client.receiveZoneTagged(team, player, zone)
                numOrbs = struct.unpack('!I', datagram[13:17])[0]
                team.validate(numOrbs, self.client)
                stars = struct.unpack('B', datagram[17])[0]
                turret = datagram[18]
                if turret == "T":
                    deadPlayer = datagram[19]
                    self.client.receivePlayerKilled(deadPlayer, pId, None)
                    
                self.client.world.updateStars(player, stars)


        # Player has respawned
        elif datagram.startswith('Resp'):
            pId = datagram[4]
            zId = struct.unpack('!I', datagram[5:9])[0]
            self.client.receivePlayerRespawn(pId, zId)


        # A transaction has begun
        elif datagram.startswith('Trans'):
            tId = datagram[5]
            pId = datagram[6]
            stars = struct.unpack('B', datagram[7])[0]
            upgradeType = datagram[8]
            timeLeft = struct.unpack('f', datagram[9:13])[0]
            team = self.client.world.teamWithId[tId]
            player = self.client.world.playerWithId[pId]
            upgrade = upgradeOfType[upgradeType]
            transaction = transactionModule.Transaction(team, player,
                                                       upgrade, timeLeft)
            self.client.interface.transactionStarted(transaction)
            transaction.addStars(player, stars)

            # Prompt the player, seeing if they want to contribute
            interface = self.client.interface
            if isinstance(interface.player, universe.Player) and \
               interface.player.team == team and interface.player != player:
                message = '%s wants to buy a %s. Contribute?' % (player.nick, upgradeNames[upgrade])
                interface.getStars(message, interface.player.addStarsNow)
            
            


        # Receive a validation of all in-play players. Does not give any info
        # about their position, upgrades or state. Simply gives id, team, and
        # nick.
        elif datagram.startswith('ValPlayers'):
            # TODO: send zone verification with this
            numPlayers = struct.unpack('B', datagram[10])[0]
            i = 0
            index = 11
            tempPlayers = []
            while i < numPlayers:
                # Get the message about this current player.
                msgLen = struct.unpack('!I', datagram[index:index+4])[0]
                index += 4
                pMsg = datagram[index:index+msgLen]
                index += msgLen

                # Interpret the message.
                pId = pMsg[0]
                if self.client.world.playerWithId.has_key(pId):
                    dead = (pMsg[7] == 'T')
                    self.client.world.playerWithId[pId].ghost = dead
                    # TODO: It might be worth checking that the other
                    # information is correct too.
                else:
                    tId = pMsg[1]
                    team = self.client.world.teamWithId[tId]
                    stars = struct.unpack('B', pMsg[2])[0]
                    # FIXME: there still seems to be a bug here.
                    zId = struct.unpack('!I', pMsg[3:7])[0]
                    assert isinstance(zId, (int, long))
                    zone = self.client.world.zoneWithId[zId]
                    dead = (pMsg[7] == 'T')
                    # TODO: Fix this for unicode.
                    nick = marshal.loads(pMsg[8:])
                    player = universe.Player(self.client.world, nick, team,\
                                             pId, zone, dead = dead)
                    self.client.world.updateStars(player, stars)
                tempPlayers.append(pId)
                i+= 1
	    
            # Get rid of any non-existant players
            for item in list(self.client.world.playerWithId.iteritems()):
                if not tempPlayers.__contains__(item[0]):
                    item[1].removeFromGame()


        # Receive a validation of the ownership of every zone.
        elif datagram.startswith('ValZones'):
            numZones = struct.unpack('!I', datagram[8:12])[0]
            i = 0
            index = 12
            orbs = {'A': 0, 'B': 0}
            while i < numZones:
                zId = struct.unpack('!I', datagram[index:index+4])[0]
                zone = self.client.world.zoneWithId[zId]
                teamID = datagram[index + 4]
                orbOwner = self.client.world.teamWithId[teamID]
                zoneOwner = self.client.world.teamWithId[datagram[index + 5]]
                zone.orbOwner = orbOwner
                zone.zoneOwner = zoneOwner
                i += 1
                index += 6
                if teamID in orbs.keys():
                    orbs[teamID] += 1
            for team, orbCount in orbs.iteritems():
                self.client.world.teamWithId[team].numOrbsOwned = orbCount

        # Receive a validation of how many stars each player has
        elif datagram.startswith('ValStars'):
            numPlayers = struct.unpack('B', datagram[8])[0]
            i = 0
            index = 9
            while i < numPlayers:
                pId = datagram[index]
                player = self.client.world.playerWithId[pId]
                stars = struct.unpack('B', datagram[index + 1])[0]
                if player.stars != stars:
                    self.client.world.updateStars(player, stars)
                i += 1
                index += 2

        # Receive a validation of the current state of a transaction
        elif datagram.startswith('ValTran'):
            if datagram[7] == '\x00':
                tId = datagram[8]
                team = self.client.world.teamWithId[tId]
                self.client.world.updateTransaction(team, 'a')
                return
            tId = datagram[7]
            team = self.client.world.teamWithId[tId]
            pId = datagram[8]
            player = self.client.world.playerWithId[pId]
            totalStars = struct.unpack('B', datagram[9])[0]
            numItems = struct.unpack('B', datagram[10])[0]
            timeLeft = struct.unpack('f', datagram[11:15])[0]
            upgrade = upgradeOfType[datagram[15]]
            contributors = {}
            i = 0
            index = 16
            while i < numItems:
                pId = datagram[index]
                numStars = struct.unpack('B', datagram[index + 1])[0]
                player = self.client.world.playerWithId[pId]
                contributors[player] = numStars
                i += 1
                index += 2
            self.client.validateTransaction(team, contributors, totalStars,
                                            player, timeLeft, upgrade)

        # Receive a validation of all current upgrade details.
        elif datagram.startswith('ValUpgr'):
            numUpgrades = struct.unpack('B', datagram[7])[0]
            index = 8
            upgrades = {}
            i = 0
            turretType = Turret.upgradeType
            while i < numUpgrades:
                pId = datagram[index]
                player = self.client.world.playerWithId[pId]
                upgType = datagram[index + 1]
                inUse = datagram[index + 2] == 'T'
                i += 1
                index += 3

                # Take into account that we need a turret's zone
                zId = None
                if upgType == turretType and inUse:
                    zId = struct.unpack('!I', datagram[index:index + 4])[0]
                    index += 4
                upgrades[player] = (upgType, inUse, zId)
            # Check to ensure they're all right, fix if not:
            for upgrade in upgrades.iteritems():
                player = upgrade[0]
                upgType = upgrade[1][0]
                inUse = upgrade[1][1]
                zId = upgrade[1][2]
                if player.upgrade and player.upgrade.upgradeType == upgType:
                    if not player.upgrade.inUse == inUse:
                        if inUse:
                            # Make sure we are in the right zone
                            if isinstance(player.upgrade, Turret):
                                newZone = self.client.world.zoneWithId[zId]
                                if player.currentZone != newZone:
                                    player.currentZone.removePlayer(player)
                                    newZone.addPlayer(player)
                                    
                            player.upgrade.clientUse()
                        else:
                            # They think it's in use when it's not. Delete it
                            # and start again.
                            player.upgrade.clientDelete()
                            player.upgrade = upgradeOfType[upgType](player)
                            
                else:
                    player.upgrade = upgradeOfType[upgType](player)
                    if inUse:
                        # Make sure we are in the right zone
                        if isinstance(player.upgrade, Turret):
                            newZone = self.client.world.zoneWithId[zId]
                            if player.currentZone != newZone:
                                player.currentZone.removePlayer(player)
                                newZone.addPlayer(player)
                                player.currentZone = newZone
                        player.upgrade.clientUse()
            
            # Get rid of any non-existant upgrades
            for player in self.client.world.playerWithId.values():
                if player.upgrade and not upgrades.has_key(player):
                    player.upgrade.clientDelete()
                
            

        # A player has added star(s) to a transaction
        elif datagram.startswith('AddStars'):
            tId = datagram[8]
            team = self.client.world.teamWithId[tId]
            pId = datagram[9]
            player = self.client.world.playerWithId[pId]
            stars = struct.unpack('B', datagram[10])[0]
            totalStars = struct.unpack('B', datagram[11])[0]
            self.client.world.updateTransaction(team, 's', totalStars,
                                                player, stars)

        # A transaction has been completed
        elif datagram.startswith('Complete'):
            # Double checks that all the transaction info is correct, then
            # completes the transaction.
            tId = datagram[8]
            team = self.client.world.teamWithId[tId]
            transaction = team.currentTransaction
            if not transaction:
                # Get the correct data
                pId = datagram[9]
                try:
                    player = self.client.world.playerWithId[pId]
                except KeyError:
                    logging.writeException()
                    self.client.requestPlayers()
                    return
                else:
                    uId = datagram[10]
                    upgrade = upgradeOfType[uId]
                    team.currentTransaction = transaction = \
                                    transactionModule.Transaction(team,
                                    player, upgrade)
                    self.client.interface.transactionStarted(transaction)
                    # Add the full complement of stars
                    transaction.addStars(player, upgrade.requiredStars)
                
            numItems = struct.unpack('B', datagram[11])[0]
            i = 0
            index = 12
            # The network message will have simply sent all the new values
            # for number of stars for each player. Get these and set them.
            # TODO: should this go in Transaction code instead of much verification?
            while i < numItems:
                pId = datagram[index]
                numStars = struct.unpack('B', datagram[index + 1])[0]
                player = self.client.world.playerWithId[pId]
                self.client.world.updateStars(player, numStars)
                i += 1
                index += 2
            self.client.world.updateTransaction(team, 'c')

        # A transaction has been abandoned
        elif datagram.startswith('Abandon'):
            tId = datagram[7]
            team = self.client.world.teamWithId[tId]
            self.client.world.updateTransaction(team, 'a')
            


        # A player is using an upgrade
        elif datagram.startswith('UseUpgr'):
            pId = datagram[7]
            player = self.client.world.playerWithId[pId]
            pos = struct.unpack('ff', datagram[8:16])
            self.client.positionUpdate(pId, pos)
            upgradeType = datagram[20:]
            if not (player.upgrade and player.upgrade.upgradeType == upgradeType and \
               not player.upgrade.inUse):
                # Correct our known data
                player.upgrade = upgradeOfType[upgradeType](player)
            if isinstance(player.upgrade, Turret):
                zId = struct.unpack('!I', datagram[16:20])[0]
                zone = self.client.world.zoneWithId[zId]
                if zone.turretedPlayer:
                    # We think there's already a turreted player within.
                    self.client.requestUpgrades()
            player.upgrade.clientUse()
            if self.client.interface:
                message = "%s is using %s" % (player.nick, \
                                              repr(player.upgrade))
                self.client.interface.newMessage(message)


        # A player's upgrade is deleted
        elif datagram.startswith('DelUpgr'):
            pId = datagram[7]
            player = self.client.world.playerWithId[pId]
            if player.upgrade:
                if self.client.interface:
                    message = "%s's %s upgrade is gone" % (player.nick, \
                                                           repr(player.upgrade))
                    self.client.interface.newMessage(message)
                player.upgrade.clientDelete()

        # Received from the server when it wants this client to send a player
        # update
        elif datagram.startswith('PingUpd'):
            pId = datagram[7]
            player = self.client.world.playerWithId[pId]
            if player.local:
                self.client.sendPlayerUpdate(player)
            else:
                raise ValueError, 'Player is not local'

        # Received from the server when it wants to know the player's
        # currentZone
        elif datagram.startswith('PingZne'):
            pId = datagram[7]
            player = self.client.world.playerWithId[pId]
            if player.local:
                self.client.sendZoneChange(player, player.currentZone)
            else:
                raise ValueError, 'Player is not local'

        # A player has changed their currentZone
        elif datagram.startswith('ZoneCh'):
            pId = datagram[6]
            player = self.client.world.playerWithId[pId]
            if not player.local:
                zId = struct.unpack('!I', datagram[7:11])[0]
                zone = self.client.world.zoneWithId[zId]
                player.changeZone(zone)

        # A chat is received
        elif datagram.startswith('Chat'):
            pId = datagram[4]
            sender = self.client.world.playerWithId[pId]
            messageType = datagram[5:9]
            if messageType == 'Team':
                teamId = datagram[9]
                team = self.client.world.teamWithId[teamId]
                self.client.receiveChat(datagram[10:], sender, team)
            elif messageType == 'Priv':
                playerId = datagram[9]
                receiver = self.client.world.playerWithId[playerId]
                # Find the address to send it to:
                self.client.receiveChat(datagram[10:], sender, receiver)
            elif messageType == 'Open':
                self.client.receiveChat(datagram[9:], sender, None)

        elif datagram.startswith("Ready"):
            playerId = datagram[5]
            player = self.client.world.playerWithId[playerId]
            player.team.ready = True
            self.client.interface.newMessage("Team %s is Ready" %
                                      (player.team.id),
                                      player.team.chatColour)

        elif datagram.startswith("Captain"):
            pId = datagram[7]
            player = self.client.world.playerWithId[pId]
            player.team.captain = player
            self.client.interface.newMessage("%s is Team %s's Captain" %
                                      (player.nick, player.team.id),
                                      player.team.chatColour)

        elif datagram.startswith("ValGStat"):
            self.client.validateGame(datagram)

        elif datagram.startswith("SvrMsg"):
            # TODO: better colour?
            self.client.interface.newMessage(datagram[6:])
        elif datagram.startswith('About2Start'):
            delay = struct.unpack('!d', datagram[11:19])[0]
            self.client.interface.newMessage('Both teams are ready. Game starting in %d seconds' % delay)
            self.client.interface.gameInterface.gameViewer.pregameMessage.setText('Prepare yourself...')

        # We don't recognise this command
        else:
            print "Don't understand: ", datagram
            
    def askForServers(self):
        # Ask the network for trosnoth servers.
        try:
            self.port.write('Trosnoth:ServerList?', (multicastGroup, multicastPort))
        except:
            # If we can't access the network, we can't ask for servers.
            pass

    def connect(self, udpPort, ipAddr):
        '''Note: Connected UDP does not imply a connection'''
        self.transport.connect(ipAddr, udpPort)

    def sendDatagram(self, message):
        # Requires the connect function to have already been called.
        # print "Send: " + message
        self.transport.write(message)

class NetworkClient(object):
    '''Talks to the network as a client.'''

    def __init__(self, mainInterface):
        self.udpClient = UDPClient(self, UDPClientPort)
        self.udpTransmitter = None
        self.tcpFactory = None
        self.serverDetails = {}
        self.mainInterface = mainInterface
        self.interface = None

        # Initialise layout database.
        self.layoutDatabase = mapLayout.LayoutDatabase()

    ######### Updating server list

    def refreshServerList(self, delay=1.):
        '''Calculates a mapping of server alias to server details, and update
        the object's serverList attribute accordingly.

        delay is the number of seconds to wait before assuming that we've
        heard from all servers on the local network.'''
        # First, we broadcast to the local network asking for servers.
        self.udpClient.askForServers()
        self.serverDetails = {}

        serverListDeferred = defer.Deferred()
        reactor.callLater(delay, self.serverListComplete, serverListDeferred)
        
        return serverListDeferred

    def addServer(self, name, tcpPort, address):
        '''Called by udp broadcast protocol when it gets a server to add to
        the list.'''
        self.serverDetails[name] = (address[0], tcpPort)

    def serverListComplete(self, deferred):
        '''Called by the reactor when enough time has passed to assume that
        the server list is complete.'''
        deferred.callback(None)

    def getServerList(self):
        result = self.serverDetails.keys()
        result.sort()
        return result
    
    serverList = property(getServerList)
    
    ######### Connecting to server.

    def connect(self, server):
        '''Connects to the server specified by its alias, and sets up a
        Universe object containing all world details received by the server.
        Returns a deferred, whose callback is passed the Universe object.'''
        result = defer.Deferred()
        if self.tcpFactory:
            result.errback(Exception('Already connected'))
            return result

        # Look up the server and begin connection.
        ipAddr, tcpPort = self.serverDetails[server]
        try:
            self.tcpFactory = TCPClientFactory(self, self.udpClient.port)
            reactor.connectTCP(ipAddr, tcpPort, self.tcpFactory)
        except Exception, e:
            logging.writeException()
            result.errback(e)
            return result
        
        self.connectingDeferred = result

        return result

    def connectByPort(self, hostName, port):
        '''Connects to the server specified by its hostname (or ip addr)
        and port.'''
        # Resolve the ip address.
        print 'Resolving host address...'
        reactor.resolve(hostName).addCallbacks(self.gotHostIPAddress,
                                               self.errorGettingHostIP,
                                               [port])
        result = defer.Deferred()
        print 'Ok.'
        self.connectingDeferred = result

        return result

    def gotHostIPAddress(self, ipAddr, port):
        print 'Host name resolved to %s' % ipAddr
        try:
            self.tcpFactory = TCPClientFactory(self, self.udpClient.port)
            reactor.connectTCP(ipAddr, port, self.tcpFactory)
        except Exception, e:
            logging.writeException()
            self.connectingDeferred.errback(e)

    def errorGettingHostIP(self, error):
        print 'Error getting host IP address.'
        self.connectingDeferred.errback(error)
        
    def gotSettings(self, settings):
        'Called when the server initially sends its settings.'
        self.serverSettings = settings

        layouts = []
        # Check if we know of all the map block layout files.
        for filename, checksum in settings['layoutDefs']:
            try:
                layouts.append(self.layoutDatabase.getLayout(filename,
                                                             checksum))
            except ValueError, E:
                # TODO: Checksum is wrong: request correct layout from server.
                print 'ValueError: %s - assume incorrect checksum' % E
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

        self.connected(settings)

    def gotMapBlock(self, mapBlock):
        'Called when the server sends map block information.'
        pass
    
    def connected(self, settings):
        'Called when connection has been made and validated.'

        try:
            ipAddr = self.tcpFactory.protocol.transport.addr[0]
            self.udpTransmitter = UDPClient(self)

            # Create a new universe based on the settings.
            halfMapWidth = self.serverSettings['halfMapWidth']
            mapHeight = self.serverSettings['mapHeight']

            self.world = universe.Universe(self, halfMapWidth, mapHeight)
            
            for zone in self.world.zones: 
                zone.mapBlockList = [] 
                zone.unBlockedCount = 0 
            
            # Populate the map blocks with obstacles.
            worldMap = self.serverSettings['worldMap']
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

            # Listen for udp messages.
            self.udpTransmitter.connect(self.serverSettings['udpPort'], ipAddr)
        except Exception, e:
            logging.writeException()
            self.connectingDeferred.errback(e)
            return

        self.world.teams[0].teamName = settings['teamName0']
        self.world.teams[1].teamName = settings['teamName1']

        self.world.replay = settings['replay']
        if settings['gameState'] == "PreGame":
            self.world.gameState = GameState.PreGame
        elif settings['gameState'] == "InProgress":
            self.world.gameState = GameState.InProgress
        if settings['gameState'] == "Ended":
            self.world.gameState = GameState.Ended

        if 'timeRunning' in settings:
            self.world.startTime = timeNow() - settings['timeRunning']
            self.world.gameDuration = settings['timeLimit']
        
        # Connection made successfully. Call callback.
        print 'Client: Connection established and validated.'
        self.connectingDeferred.callback(self.world)

    def disconnect(self):
        '''Disconnects from the server. Returns a deferred.'''
        print 'Client: disconnecting from server.'
        if self.tcpFactory == None:
            return defer.fail(Exception('Not connected'))
        self.tcpFactory.protocol.disconnect()
        return defer.succeed(None)

    def tcpConnectionLost(self):
        '''Called when the tcp connection to the server is lost.'''
        self.tcpFactory.protocol = None
        self.tcpFactory = None
        if self.udpClient is not None:
            self.udpClient.port.stopListening()
        self.udpClient = UDPClient(self, UDPClientPort)

        # Tell the main interface that connection was lost.
        self.mainInterface.connectionLost()
        
    def join(self, nick, team):
        '''Creates a player for you, and joins the game with the specified nick
        and on the specified team. Returns a deferred, whose callback is
        passed the player object. This method can be called multiple times
        for the same connection and will create a new player object for each
        time it's called. This is so that bots can be supported.'''
        result = defer.Deferred()

        if not self.tcpFactory or not self.tcpFactory.protocol or \
                   not self.tcpFactory.protocol.validated:
            result.callback(('noserver',))
        else:
            self.tcpFactory.protocol.join(nick, team, result)

        return result

    def cancelJoin(self, nick, team):
        'Cancels an attempt to join the game.'
        if self.tcpFactory is not None and self.tcpFactory.protocol is not None and \
                self.tcpFactory.protocol.validated:
            self.tcpFactory.protocol.cancelJoin(nick, team)

    def leave(self, player):
        '''Removes the specified player from the game. The player should have
        been created using the join() method.'''
        if not self.tcpFactory or not self.tcpFactory.protocol or \
               not self.tcpFactory.protocol.validated:
            return defer.fail(Exception('Not connected to server yet'))
        if not player:
            return defer.fail(Exception('No player specified'))
        self.tcpFactory.protocol.leave(player.id)

        # TODO: Remove all player's stars from any current transaction
        return defer.succeed(None)
    
    def sendUDP(self, message):
        self.udpTransmitter.sendDatagram(message)

    def setDetailsInterface(self, interface):
        self.interface = interface

    def sendPlayerUpdate(self, player):
        '''Sends the server an update of the player's current state. Player
        should be a locally-controlled player - that is, a player created using
        the join() method. An update only needs to be sent when the player
        changes state (which keys are being pressed), because actual position
        of the player is predicted by each client.'''


        pos = struct.pack('ff', *player.pos)
        yVel = struct.pack('f', player.yVel)
        indices = struct.pack('!II', *player.currentMapBlock.defn.indices)
        angle = struct.pack('f', player.angleFacing)
        message = 'PlUpd' + player.id + pos + yVel + indices + angle

        for i in (player._state['left'], player._state['right'], \
                  player._state['jump'], player._state['down']):
            if i:
                message += "T"
            else:
                message += "F"
        if player.upgrade:
            message += 'T'
        else:
            message += 'F'
        if player.ghost:
            message += 'T'
        else:
            message += 'F'
        self.sendUDP(message)
        return defer.succeed(None)

    def positionUpdate(self, pId, pos, indices=None, yVel = None, angle = None):
        player = self.world.playerWithId[pId]
        if not player.local:
            player.pos = [pos[0], pos[1]]
            if yVel is not None:
                player.yVel = yVel
            # Validation to ensure they're in the right mapBlock and such.
            if indices is not None:
                i, j = indices
                player.currentMapBlock = self.world.zoneBlocks[i][j]
            if angle is not None:
                player.lookAt(angle)
    
    def sendShotFired(self, player, turret):
        '''Sends the server a message indicating that the player wants to
        fire a shot, and giving the player's current location and viewing
        angle. Client does not assume shot has been fired until it receives
        a response from the server.'''

        angle = struct.pack('f', player.angleFacing)
        pos1 = struct.pack('f', player.pos[0])
        pos2 = struct.pack('f', player.pos[1])
        message = 'Shot' + player.id + angle + pos1 + pos2 + 'N'
        self.sendUDP(message)

        
        return defer.succeed(None)
    
    def sendGrenadeExploded(self, grenade):
        def mkMsg(angle):
            angle = struct.pack('f', angle)
            pos1 = struct.pack('f', grenade.gr.pos[0])
            pos2 = struct.pack('f', grenade.gr.pos[1])
            message = 'Shot' + grenade.player.id + angle + pos1 + pos2 + 'G'
            self.sendUDP(message)

        #fire shots
        for x in range(0, grenade.numShots):
            angle = pi*(2*random() - 1.0)  # In range (-pi, pi)
            mkMsg(angle)
    
    def receiveShotFired(self, pos, angle, pId, sId, turret):
        '''Tells the universe object that a shot has been fired.'''
        player = self.world.playerWithId[pId]
        team = player.team
        if self.world:
            self.world.shotFired(sId, team, pos, angle, player, turret)

    def sendZoneTagged(self, zone, player, team):
        '''Sends the server a message indicating that the zone has been tagged
        by the given player'''
        zId = struct.pack('!I', zone.id)
        if player:
            pId = player.id
        else:
            pId = '\x00'
        if team:
            tId = team.id
        else:
            tId = '\x00'
        message = 'TagZone' + zId + pId + tId
        self.sendUDP(message)

    def receiveZoneTagged(self, team, player, zone):
        '''Tells the universe object that a zone has been tagged'''
        # TODO: receive turret deaths even when zone is rendered neutral
        owner = ""
        if zone.orbOwner == None:
            owner = "neutral "
        zone.tag(team, player)

        if self.interface:
            if player:
                message = "%s tagged %szone %3d" % (player.nick, owner, zone.id)
            else:
                message = "Zone %3d rendered neutral" % (zone.id)
            self.interface.newMessage(message)

    def sendPlayerKilled(self, player, killer, shot = None):
        '''Sends the server a message indicating that a player has been
        killed by a certain shot'''

        pos1 = struct.pack('f', player.pos[0])
        pos2 = struct.pack('f', player.pos[1])
        message = 'Kill' + player.id + killer.id + shot.id + pos1 + pos2
        self.udpTransmitter.sendDatagram(message)

    def receivePlayerKilled(self, pId, kId, sId):
        '''Tells the universe that a certain player has been killed, who they
        were killed by, using which shot'''
        player = self.world.playerWithId[pId]
        killer = self.world.playerWithId[kId]
        if sId:
            try:
                shot = killer.shots[sId]
            except KeyError:
                logging.writeException()
                shot = None
        else:
            shot = None
        self.world.killPlayer(player, killer, shot)
        if self.interface:
            message = "%s killed %s" % (killer.nick, player.nick)
            self.interface.newMessage(message)

    def shotDestroyed(self, shot):
        '''Tells the network that a shot has been destroyed (likely by
        colliding with a turretted player)'''
        message = 'KShot' + shot.originatingPlayer.id + shot.id
        self.udpTransmitter.sendDatagram(message)
    
    def sendPlayerRespawn(self, ghost):
        '''Tells the network that a player has respawned at the given
        position'''
        if self.world.gameState == GameState.PreGame:
            return
        pId = ghost.id
        zId = struct.pack('!I', ghost.currentZone.id)
        message = 'Resp' + pId + zId
        self.udpTransmitter.sendDatagram(message)
        
    def receivePlayerRespawn(self, pId, zId):
        player = self.world.playerWithId[pId]
        zone = self.world.zoneWithId[zId]
        self.world.respawn(player, zone)
        if self.interface:
            message = player.nick + " is back in the game"
            self.interface.newMessage(message)

    def StartTransaction(self, upgrade, player, stars):
        '''Initiates a transaction to purchase an upgrade'''
        tId = player.team.id
        pId = player.id
        numStars = struct.pack('B', stars)
        upgradeType = upgrade.upgradeType
        message = 'Trans' + tId + pId + numStars + upgradeType
        self.udpTransmitter.sendDatagram(message)
        

    def addStars(self, team, player, stars):
        '''Informs the network of a player's star-adding'''
        tId = team.id
        numStars = struct.pack('B', stars)
        pId = player.id
        message = 'AddStars' + tId + pId + numStars
        self.udpTransmitter.sendDatagram(message)

    def abandonTransaction(self, team):
        '''Informs the network that a transaction has been abandoned by the
        initiating player.'''
        tId = team.id
        self.udpTransmitter.sendDatagram('Abandon' + tId)

    def useUpgrade(self, player):
        '''Informs the network that an update has expired, or that
        its owning player has died'''
        pos = struct.pack('ff', *player.pos)
        zId = struct.pack('!I', player.currentZone.id)
        message = 'UseUpgr' + player.id  + pos + zId + \
                  player.upgrade.upgradeType
        self.udpTransmitter.sendDatagram(message)

    def upgradeDelete(self, player):
        '''Informs the server that the upgrade has been prematurely deleted'''
        pos = struct.pack('ff', *player.pos)
        message = 'DelUpgr' + player.id  + player.upgrade.upgradeType
        self.udpTransmitter.sendDatagram(message)

    def receiveUpgradeUse(self, player):
        '''Tells the player in question that its upgrade has been deleted'''
        # TODO: um... what?

    def requestTransactionInfo(self, team):
        self.udpTransmitter.sendDatagram('reqTrans' + team.id)
    
    def validateTransaction(self, team, contributors, totalStars,
                            player, timeLeft, upgrade):
        '''Validates a current transaction, making sure that the player
        has the correct details.'''
        transaction = team.currentTransaction
            
        if not transaction:
            transaction = transactionModule.Transaction(team, player,
                                                       upgrade, timeLeft)
            self.interface.transactionStarted(transaction)
            transaction.addStars(player, contributors[player])
        else:
            if contributors == transaction.contributions and \
               player == transaction.purchasingPlayer:
                # We're happy
                pass
            else:
                transaction.contributions = contributors
                self.interface.transactionChanged(transaction)
                
    def requestPlayers(self):
        '''Request the list of players currently in the game.'''
        self.udpTransmitter.sendDatagram('reqPlayers')
        
    def requestZones(self):
        '''Request the current ownership of all zones'''
        self.udpTransmitter.sendDatagram('reqZones')

    def requestStars(self):
        '''Request the current number of stars that each player has.'''
        self.udpTransmitter.sendDatagram('reqStars')

    def requestUpgrades(self):
        '''Request the current upgrades that all players have.'''
        self.udpTransmitter.sendDatagram('reqUpgrades')

    def sendZoneChange(self, player, zone):
        '''Inform the server that a local player has changed zones.'''
        zoneId = struct.pack('!I', zone.id)
        message = 'ZoneCh' + player.id + zoneId
        self.udpTransmitter.sendDatagram(message)            
        
    def sendChat(self, text, sendingPlayer, chatMode = "team"):
        '''Send a chat message to the server. The server will send it out
        to the appropriate address(es)'''
        if not text:
            return
        message = 'Chat'
        message += sendingPlayer.id

        if chatMode == "all":
            privacy = None
        else:
            privacy = sendingPlayer.team
            
        if text.startswith('#'):
            inc = 1
            try:
                while text[inc] <= '9' and text[inc] >= '0':
                    inc += 1
            except IndexError:
                # Message must only contain numbers
                return
            if inc == 1:
                # No leading numbers: let it pass unchanged as a team message
                privacy = sendingPlayer.team
            else:
                numString = text[1:inc]
                pId = int(numString)
                if pId < 0 or pId > 255:
                    self.interface.newMessage("No player with that ID", colours.errorMessageColour)
                    return
                pId = struct.pack('B', pId)
                try:
                    player = self.world.playerWithId[pId]
                except KeyError:
                    self.interface.newMessage("No player with that ID", colours.errorMessageColour)
                    return
                else:
                    if player.team != sendingPlayer.team:
                        self.interface.newMessage("You cannot send a private message to a member of the enemy", colours.errorMessageColour)
                        return
                    elif player == sendingPlayer:
                        msg = choice(["Good work discussing team strategy... with yourself",
                                      "Talking to yourself isn't going to convince others that you have friends"
                                      ])
                        self.interface.newMessage(msg, colours.errorMessageColour)
                        return
                    else:
                        privacy = player
                        text = text[inc:]
                        # Get rid of the first space
                        if text.startswith(' '):
                            text = text[1:]

        if text.replace(' ', '') == '':
            # Whitespace-only (or empty) message: ignore it
            return
        if isinstance(privacy, universe.Team):
            message += 'Team'
            message += privacy.id
        elif isinstance(privacy, universe.Player):
            message += 'Priv'
            message += privacy.id
        else:
            message += 'Open'
        message += text
        self.udpTransmitter.sendDatagram(message)
        if self.interface:
            self.interface.sentChat(text, sendingPlayer.team, privacy)

    
    def receiveChat(self, text, sender, private):
        '''We have received a chat from someone in the game.'''
        if self.interface is not None:
            self.interface.newChat(text, sender, private)

    def setAsCaptain(self, player):
        if player.team.captain:
            return
        message = "Captain"
        message += player.id
        self.tcpFactory.protocol.sendString(message)

    def teamReady(self, player):
        if player.team.captain == player and not player.team.ready:
            self.tcpFactory.protocol.sendString("Ready" + player.id)

    def madeCaptain(self, pId):
        player = self.world.playerWithId[pId]
        player.team.captain = player

    def validateGame(self, datagram):
        state = datagram[8]
        if state == 'P':
            self.world.gameState = GameState.PreGame
        elif state == 'I':
            self.world.gameState = GameState.InProgress
        elif state == 'E':
            self.world.gameState = GameState.Ended
        index = 9
        if datagram[index] == 'F' and state == 'I':
            time = struct.unpack('d', datagram[index+1:index + 9])[0]
            print "Time: ", time
            self.world.setTimeLeft(time)
            index+= 8
        index += 1
        for i in 0,1:
            team = self.world.teamWithId[datagram[index]]
            index += 1
            if datagram[index] == 'T':
                captain = self.world.playerWithId[datagram[index + 1]]
                # TODO: if the captain isn't the same, tell the user
                team.captain = captain
                index += 1
            else:
                team.captain = None
            index += 1
            team.ready = datagram[index] == 'T'
            index += 1
            numOwned = struct.unpack('I', datagram[index: index + 4])[0]
            if numOwned != team.numOrbsOwned:
                self.requestZones()
            index += 4
            numPlayers = struct.unpack('B', datagram[index])[0]
            # TODO: implement the following team-side
            # if numPlayers != team.numberOfPlayers:
            #     self.requestPlayers()
            index += 1
            flag = datagram[index] == 'T'
            if (flag and team.currentTransaction) or \
                not (flag or team.currentTransaction):
                # We are correct
                pass
            else:
                # FIXME: players won't know about enemy transactions currently
                # so this shouldn't be called in that case.
                # Note that the server just won't send it in any case; but
                # there's no point in wasting the server's time
                self.requestTransactionInfo(team)
            index += 1
            
            

        
