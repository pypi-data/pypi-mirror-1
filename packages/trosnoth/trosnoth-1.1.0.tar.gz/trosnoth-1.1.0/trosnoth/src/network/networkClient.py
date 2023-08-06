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
import os
import re

import struct
import marshal

from trosnoth.src.utils.unrepr import unrepr
from trosnoth.src.utils.event import Event

from trosnoth.src.network.networkDefines import *

from trosnoth.src.model import universe, mapLayout
from trosnoth.src.network.networkServer import serverMsgs
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

from trosnoth.src.utils import logging
from trosnoth.src.model.upgrades import Turret, upgradeOfType, upgradeNames
from trosnoth.src.model.universe_base import GameState
import trosnoth.src.model.transaction as transactionModule

from trosnoth.src.utils.utils import timeNow

from trosnoth.src.trosnothgui.ingame import colours

from trosnoth.data import getPath, user

# Component message passing
from trosnoth.src.utils.components import Component, handler, Plug
from trosnoth.src.messages.chat import *
from trosnoth.src.messages.connection import *
from trosnoth.src.messages.game import *
from trosnoth.src.messages.gameplay import *
from trosnoth.src.messages.players import *
from trosnoth.src.messages.shot import *
from trosnoth.src.messages.transactions import *
from trosnoth.src.messages.validation import NotifyUDPStatus

from trosnoth.src.model.player import Player

# TODO: Define some exception classes and use them instead of Exception

# TODO: ensure all messages sent to the interface class are relevant to the
# target (such as "transaction completed". maybe interface class can manage
# that.)

# The set of messages that the client expects to receive.
clientMsgs = netmsg.MessageCollection(
    # trosnoth.src.network.players
    AddPlayerMsg,
    GivePlayerMsg,
    RemovePlayerMsg,
    CannotCreatePlayerMsg,
    
    # trosnoth.src.network.game
    GameStartMsg,
    GameOverMsg,
    SetGameModeMsg,
    SetTeamNameMsg,
    ServerShutdownMsg,
    StartingSoonMsg,
    SetCaptainMsg,
    TeamIsReadyMsg,

    # trosnoth.src.network.shot
    ShotFiredMsg,

    # trosnoth.src.network.chat 
    ChatFromServerMsg, 
    ChatMsg,

    # trosnoth.src.network.validation 
    ValidateGameStatusMsg,
    ValidateTeamStatusMsg, 
    ValidateUpgradesMsg,
    ValidateUpgradeMsg,
    ValidatePlayersMsg,
    ValidatePlayerMsg,
    ValidateZoneMsg,
    RequestPlayerUpdateMsg,
    RequestZoneUpdateMsg,
    ValidateTransactionMsg,
    NotifyUDPStatusMsg,

    # trosnoth.src.network.gameplay 
    KilledMsg,
    KillShotMsg,
    TaggedZoneMsg,
    PlayerUpdateMsg,
    RespawnMsg,
    ZoneChangeMsg,

    # trosnoth.src.network.map
    MapBlockGraphicsMsg,
    MapBlockMsg,

    # trosnoth.src.network.transactions
    StartedTransactionMsg, 
    DeleteUpgradeMsg,
    AddedStarsMsg,
    AbandonTransactionMsg,
    TransactionCompleteMsg,
    UseUpgradeMsg,

    # trosnoth.src.network.setup
    InitClientMsg,
)

class ClientNetHandler(Component):
    '''
    A network message handler designed for use with trosnoth.network.netman.
    '''
    greeting = 'Trosnoth1'
    messages = clientMsgs

    plug = Plug()

    def __init__(self, netman, host, port=6789):
        Component.__init__(self)
        self.netman = netman
        self.netman.connect(self, host, port)

        self.connId = None
        self.validated = False

        # udpWorks keeps track of whether the server is sending UDP messages
        # to the client. It is assumed to be true initially, and is updated
        # if other information comes to light.
        self.udpWorks = True

    def disconnect(self):
        'Call this to disconnect from the server.'
        print 'Client: Disconnecting due to command interface'
        self.netman.closeConnection(self.connId)

    #################################
    # Interface with network manager
    #################################

    def newConnection(self, connId, ipAddr, port):
        '''
        Called by the network manager when an incoming connection is completed.
        '''
        # Should never happen since we're not registered as a handler.
        print 'Client: Unexpected connection event'

    def connectionComplete(self, connId):
        '''
        Called by the network manager when the connection is complete.
        '''
        # Should only ever happen once.
        print 'Client: connected to server'
        self.connId = connId

    def receiveMessage(self, connId, msg):
        '''
        Called by the network manager when a message is received.
        '''
        if isinstance(msg, InitClientMsg):
            self._receiveInitClientMsg(msg)
        elif isinstance(msg, NotifyUDPStatusMsg):
            self._receiveNotifyUDPStatusMsg(msg)
        elif not self.validated:
            print 'Client: got %s while connecting' % (msgType,)
            self.netman.closeConnection(connId)
            self.plug.send(ErrorConnecting('Unexpected server response'))
        else:
            self.plug.send(msg)

    def receiveBadString(self, connId, line):
        '''
        Called by the network manager when an unrecognised string is received.
        '''
            
        if not self.validated:
            # If we receive a bad string before being validated, this may not
            # be a Trosnoth server (or majorly incorrect version).
            print 'Client: unexpected server message before validation'
            self.netman.closeConnection(self.connId)

            self.plug.send(ErrorConnecting('Game is not behaving like '
                    'a valid Trosnoth server.'))
            return

        # We don't recognise this command
        print 'Client: Unknown message: %r' % (line,)
        print '      : Did you invent a new network message and forget to'
        print '      : add it to trosnoth.networkClient.clientMsgs?'

    def connectionLost(self, connId):
        '''
        Called by the network manager when the connection is lost.
        '''
        print 'Client: lost connection to server'
        self.connId = None
        if self.validated:
            self.validated = False
            self.plug.send(ConnectionLost())
        else:
            self.plug.send(ErrorConnecting('not a running Trosnoth server'))

    def connectionFailed(self, connId):
        '''
        Called by the network manager if the attempt to connect fails.
        '''
        self.plug.send(ErrorConnecting('could not connect to server'))

    ###################
    # Other methods
    ###################
        
    def sendMessage(self, msg):
        if self.connId is None:
            return
        self.netman.send(self.connId, msg)
    # sendMessage must be a handler for everything that networkServer can
    # receive.
    for _msg in serverMsgs:
        sendMessage = handler(_msg)(sendMessage)
    del _msg        

    def _receiveInitClientMsg(self, msg):
        # Settings from the server.
        settings = unrepr(msg.settings)

        # Check that we recognise the server version.
        svrVersion = settings.get('serverVersion', 'server.v1.0.0+')
        if svrVersion not in validServerVersions:
            print 'Client: bad server version %s' % (svrVersion,)
            self.netman.closeConnection(self.connId)
            self.plug.send(ErrorConnecting('Trosnoth server '
                    'version %s is not compatible with this client version (%s)'
                    % (svrVersion, clientVersion)))
            return

        # Tell the client that the connection has been made.
        self.validated = True
        self.plug.send(GotSettings(settings))

        # Wait 10 seconds then check if UDP is working.
        reactor.callLater(10, self._checkUDP)

        # Write the server string for the sake of debug logs.
        print 'Connected to game: <%s>' % settings['serverString']


    def _receiveNotifyUDPStatusMsg(self, msg):
        '''
        The server is sending notification as to whether or not UDP messages
        from the server can get through to the client.
        '''
        udpWorks = bool(msg.connected)
        if not udpWorks:
            # Check again in 10 seconds.
            reactor.callLater(10, self._checkUDP)

        # Notify the client.
        if udpWorks != self.udpWorks:
            self.plug.send(NotifyUDPStatus(udpWorks))

        self.udpWorks = udpWorks

    def _checkUDP(self):
        '''
        Sends a message to the server asking whether UDP works or not.
        To prevent this message from flying around out of control, this method
        should only be called once after the connection is validated, and then
        from the receiveNotifyUDPStatusMsg method as need be.
        '''
        if self.connId is not None:
            self.netman.send(self.connId, RequestUDPStatusMsg())
        
class Client(Component):

    gamePlug = Plug()
    viewPlug = Plug()    

    def __init__(self, app):
        Component.__init__(self)
        self.app = app

        self.world = None

        self.onClosed = Event()     # reason
    
        self.layoutDatabase = mapLayout.LayoutDatabase()

        self.cancelingPlayers = []
        self.waitingPlayers = {}

    def join(self, nick, team):
        '''Creates a player for you, and joins the game with the specified nick
        and on the specified team. Returns a deferred, whose callback is
        passed the player object. This method can be called multiple times
        for the same connection and will create a new player object for each
        time it's called. This is so that bots can be supported.'''
        result = defer.Deferred()

        self.gamePlug.send(JoinRequestMsg(team.id, nick.encode()))

        # TODO: Maybe check if we've already got a waiting request for this
        # team and nick.
        self.waitingPlayers[team, nick] = result

        return result

    def cancelJoin(self, nick, team):
        'Cancels an attempt to join the game.'
        try:
            deferred = self.waitingPlayers[team, nick]
        except KeyError:
            # Can't cancel player.
            logging.writeException()
            return

        self.cancelingPlayers.append((team, nick))
        reactor.callLater(1, self.justCancelJoin, deferred, (team, nick))
        
        del self.waitingPlayers[team, nick] 

    def leave(self, player):
        '''Removes the specified player from the game. The player should have
        been created using the join() method.'''
        self._leave(player.id)

        # TODO: Remove all player's stars from any current transaction
    
    def sendPlayerUpdate(self, player):
        '''Sends the server an update of the player's current state. Player
        should be a locally-controlled player - that is, a player created using
        the join() method. An update only needs to be sent when the player
        changes state (which keys are being pressed), because actual position
        of the player is predicted by each client.'''
        i, j = player.currentMapBlock.defn.indices
        
        values = compress_boolean( (player._state['left'], player._state['right'],
                player._state['jump'], player._state['down'],
                player.upgrade is not None, player.ghost ) )
        
        msg = PlayerUpdateMsg(player.id, player.pos[0], player.pos[1],
                player.yVel, player.angleFacing, player.ghostThrust,
                str(values))

        self.gamePlug.send(msg)
        return defer.succeed(None)

    def positionUpdate(self, pId, pos, yVel=None,
            angle=None, thrust=None):
        player = self.world.playerWithId[pId]
        if not player.local:
            if yVel is not None:
                player.yVel = yVel

            if angle is not None:
                player.lookAt(angle, thrust)

            player.setPos((pos[0], pos[1]))
    
    def sendShotFired(self, player, type):
        '''Sends the server a message indicating that the player wants to
        fire a shot, and giving the player's current location and viewing
        angle. Client does not assume shot has been fired until it receives
        a response from the server.'''
        self.gamePlug.send(FireShotMsg(player.id, player.angleFacing, player.pos[0],
                player.pos[1], type))
        
        return defer.succeed(None)
    
    def sendGrenadeExploded(self, grenade):
        self.gamePlug.send(GrenadeExplodedMsg(grenade.player.id, grenade.gr.pos[0], grenade.gr.pos[1]))
    
    def receiveShotFired(self, pos, angle, pId, sId, turret, ricochet):
        '''Tells the universe object that a shot has been fired.'''
        player = self.world.playerWithId[pId]
        team = player.team
        if self.world is not None:
##            if not self.world.validateTurretVal(player, turret):
##                self.requestUpgrades()
##                return
            self.world.shotFired(sId, team, pos, angle, player, turret, ricochet)
            # A bit messy
            self.viewPlug.send(ShotFired(player, self.world.shotWithId(pId, sId)))

    def sendZoneTagged(self, zone, player, team):
        '''Sends the server a message indicating that the zone has been tagged
        by the given player'''
        if team is None:
            teamId = '\x00'
        else:
            teamId = team.id
        msg = TaggingZoneMsg(zone.id, player.id, teamId)
        self.gamePlug.send(msg)

    def receiveZoneTagged(self, team, player, zone):
        '''Tells the universe object that a zone has been tagged'''
        # TODO: receive turret deaths even when zone is rendered neutral
        zone.tag(team, player)
        self.viewPlug.send(TaggedZone(zone, player))

    def sendPlayerKilled(self, player, killer, shot):
        '''Sends the server a message indicating that a player has been
        killed by a certain shot'''
        self.gamePlug.send(KillingMsg(player.id, killer.id, shot.id,
                player.pos[0], player.pos[1]))

    def receivePlayerKilled(self, pId, kId, sId):
        '''Tells the universe that a certain player has been killed, who they
        were killed by, using which shot'''
        # NOTE: This is also called when a turret is killed due to zone capture
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
        self.viewPlug.send(PlayerKilled(player, killer))

    def shotDestroyed(self, shot):
        '''Tells the network that a shot has been destroyed (likely by
        colliding with a turretted player)'''
        msg = KillShotMsg(shot.originatingPlayer.id, shot.id)
        self.gamePlug.send(msg)
    
    def sendPlayerRespawn(self, ghost):
        '''Tells the network that a player has respawned at the given
        position'''
        if self.world.gameState == GameState.PreGame:
            return
        self.gamePlug.send(RespawnMsg(ghost.id, ghost.currentZone.id))
        
    @handler(RespawnMsg, gamePlug)
    def receiveRespawnMsg(self, msg):
        player = self.world.playerWithId[msg.playerId]
        zone = self.world.zoneWithId[msg.zoneId]
        self.world.respawn(player, zone)
        self.viewPlug.send(PlayerRespawn(player, zone))

    def startTransaction(self, upgrade, player, stars):
        '''Initiates a transaction to purchase an upgrade'''
        self.gamePlug.send(StartingTransactionMsg(player.team.id,
                player.id, stars, upgrade.upgradeType))
        

    def addStars(self, team, player, stars):
        '''Informs the network of a player's star-adding'''
        self.gamePlug.send(AddingStarsMsg(team.id, player.id, stars))

    def abandonTransaction(self, team):
        '''Informs the network that a transaction has been abandoned by the
        initiating player.'''
        self.gamePlug.send(AbandonTransactionMsg(team.id))

    def useUpgrade(self, player):
        '''Informs the network that an update has expired, or that
        its owning player has died'''
        self.gamePlug.send(UseUpgradeMsg(player.id, player.pos[0],
                player.pos[1], player.currentZone.id,
                player.upgrade.upgradeType))

    def upgradeDelete(self, player):
        '''Informs the server that the upgrade has been prematurely deleted'''
        self.gamePlug.send(DeleteUpgradeMsg(player.id))

    def requestTransactionInfo(self, team):
        self.gamePlug.send(RequestTransactionMsg(team.id))
    
    def validateTransaction(self, team, contributors, totalStars,
                            player, timeLeft, upgrade):
        '''Validates a current transaction, making sure that the player
        has the correct details.'''
        transaction = team.currentTransaction
            
        if transaction is None:
            transaction = transactionModule.Transaction(team, player,
                                                       upgrade, timeLeft)
            self.viewPlug.send(StartedTransaction(transaction))
            transaction.addStars(player, contributors[player])
        else:
            if contributors == transaction.contributions and \
               player == transaction.purchasingPlayer:
                # We're happy
                pass
            else:
                transaction.contributions = contributors
                self.viewPlug.send(TransactionChanged(transaction))
                
    def requestPlayers(self):
        '''Request the list of players currently in the game.'''
        self.gamePlug.send(RequestPlayersMsg())
        
    def requestZones(self):
        '''Request the current ownership of all zones'''
        self.gamePlug.send(RequestZonesMsg())

    def requestStars(self):
        '''Request the current number of stars that each player has.'''
        self.gamePlug.send(RequestStarsMsg())

    def requestUpgrades(self):
        '''Request the current upgrades that all players have.'''
        self.gamePlug.send(RequestUpgradesMsg())

    def sendZoneChange(self, player, zone):
        '''Inform the server that a local player has changed zones.'''
        self.gamePlug.send(ZoneChangeMsg(player.id, zone.id))
        
    def sendChat(self, text, sendingPlayer, target=None):
        '''Send a chat message to the server. The server will send it out
        to the appropriate address(es)'''

        if text.strip() == '':
            return

        if isinstance(target, Player):
            kind = 'p'  # Private message.
            targetId = target.id
        elif isinstance(target, universe.Team):
            kind = 't'  # Team message.
            targetId = target.id
        else:
            if target is not None:
                print 'Unknown message target: %s' % (target,)

            kind = 'o'  # Open message.
            targetId = '\x00'

        self.gamePlug.send(ChatMsg(sendingPlayer.id, kind, targetId,
            text.encode()))
        self.viewPlug.send(OwnChat(sendingPlayer.team, target, text))

    
    def receiveChat(self, text, sender, private):
        '''We have received a chat from someone in the game.'''
        self.viewPlug.send(Chat(sender, private, text))

    def setAsCaptain(self, player):
        if player.team.captain:
            return
        self.gamePlug.send(SetCaptainMsg(player.id))

    def teamReady(self, player):
        if player.team.captain == player and not player.team.ready:
            self.gamePlug.send(TeamIsReadyMsg(player.id))

    def madeCaptain(self, pId):
        player = self.world.playerWithId[pId]
        player.team.captain = player

    #########################
    # Message handling.

    @handler(NotifyUDPStatus, gamePlug)
    def sendToView(self, msg):
        self.viewPlug.send(msg)
        
    @handler(AddPlayerMsg, gamePlug)
    def receiveAddPlayerMsg(self, msg):
        'Server announcing new player.'
        team = self.world.teamWithId[msg.teamId]
        zone = self.world.zoneWithId[msg.zoneId]

        # Create the player.
        nick = msg.nick.decode()
        
        self.world.addPlayer(nick, team, msg.playerId, zone, dead = True)

    @handler(GivePlayerMsg, gamePlug)
    def receiveGivePlayerMsg(self, msg):
        # Server gives this player to me.
        player = self.world.playerWithId[msg.playerId]

        player.makeLocal()

        # Now check if this player was in our waiting list.
        if (player.team, player.nick) in self.cancelingPlayers:
            self._leave(msg.playerId)
            self.cancelingPlayers.remove((player.team, player.nick))
        else:
            try:
                deferred = self.waitingPlayers[player.team, player.nick]
                # Fire the deferred's callbacks.
                deferred.callback(('success', player))
            except KeyError:
                logging.writeException()
                
    @handler(RemovePlayerMsg, gamePlug)
    def receiveRemovePlayerMsg(self, msg):
        # Server says this player has left the game.
        try:
            player = self.world.playerWithId[msg.playerId]
        except KeyError:
            # TODO: Handle this sensibly.
            logging.writeException()
            return
        
        player.removeFromGame()
        self.viewPlug.send(RemovePlayer(player))

    @handler(CannotCreatePlayerMsg, gamePlug)
    def receiveCannotCreatePlayerMsg(self, msg):
        # Find the deferred and call its ErrBack.
        try:
            deferred = self.waitingPlayers[
                self.world.teamWithId[msg.teamId], msg.nick]
        except KeyError:
            logging.writeException()
            return
        
        if msg.reasonId == 'F':
            deferred.callback(['full'])
        elif msg.reasonId == 'O':
            deferred.callback(['over'])
        elif msg.reasonId == 'W':
            deferred.callback(['wait', str(round(msg.waitTime, 1))])
        else:
            deferred.callback(['unknown reason code: %s' % msg.reasonId])
        
    @handler(GameStartMsg, gamePlug)
    def receiveGameStartMsg(self, msg):
        # The game has progressed from its pre-game state, to being
        # in progress.
        self.world.gameStart(msg.timeLimit)
        self.viewPlug.send(GameStart(msg.timeLimit))
        
    @handler(GameOverMsg, gamePlug)
    def receiveGameOverMsg(self, msg):
        if msg.teamId == '\x00':
            winningTeam = None
        else:
            winningTeam = self.world.teamWithId[msg.teamId]

        self.viewPlug.send(GameOver(winningTeam, msg.timeOver))

        self.world.gameOver()
        
    @handler(SetGameModeMsg, gamePlug)
    def receiveSetGameModeMsg(self, msg):
        self.world.setGameMode(msg.gameMode.decode())

    @handler(SetTeamNameMsg, gamePlug)
    def receiveSetTeamNameMsg(self, msg):
        self.world.teamWithId[msg.teamId].teamName = msg.name.decode()

    def _leave(self, playerId):
        self.gamePlug.send(LeaveRequestMsg(playerId))
    
    def justCancelJoin(self, joinDeferred, key):
        # If callback has not already been fired, do so now.
        joinDeferred.callback(['cancel'])
        try:
            self.cancelingPlayers.remove(key)
        except ValueError:
            pass

    @handler(ShotFiredMsg, gamePlug)
    def receiveShotFiredMsg(self, msg):
        # Shot fired.
        pos = (msg.xpos, msg.ypos)
        self.receiveShotFired(pos, msg.angle,
                msg.playerId, msg.shotId, msg.type in ('T', 'G'), msg.type == 'R')
        
        # FIXME: Once the grenade no longer uses the Shot message, this
        #       line can be put back in. Currently this line will cause
        #       an apparent glitch when a grenade explodes.
        # self.positionUpdate(msg.playerId, pos, angle = msg.angle)
        
    @handler(KillShotMsg, gamePlug)
    def receiveKillShotMsg(self, msg):
        shot = self.world.shotWithId(msg.playerId, msg.shotId)
        if shot is not None:
            shot.kill()

    @handler(SetCaptainMsg, gamePlug)
    def receiveSetCaptainMsg(self, msg):
        player = self.world.playerWithId[msg.playerId]
        player.team.captain = player
        self.viewPlug.send(SetCaptain(player))

    @handler(TeamIsReadyMsg, gamePlug)
    def receiveTeamIsReadyMsg(self, msg):
        player = self.world.playerWithId[msg.playerId]
        player.team.ready = True
        self.viewPlug.send(TeamIsReady(player))

    @handler(KilledMsg, gamePlug)
    def receiveKilledMsg(self, msg):
        # Player killed.
        self.receivePlayerKilled(msg.targetId, msg.killerId, msg.shotId)
        self.positionUpdate(msg.targetId, (msg.xPos, msg.yPos))
        killer = self.world.playerWithId[msg.killerId]
        self.world.updateStars(killer, msg.stars)

    @handler(PlayerUpdateMsg, gamePlug)
    def receivePlayerUpdateMsg(self, msg):
        # Receive a player update
        try:
            player = self.world.playerWithId[msg.playerId]
        except:
            # Mustn't have that info yet
            return
        if not player.local:            
            values = expand_boolean(getattr(msg, 'keys'))
            opts = ['left', 'right', 'jump', 'down']
            
            for i in range(4):
                player.updateState(opts[i], bool(values[i]))
                
            hasUpgrade = values[4]
            ghost = values[5]
            
            if (not ((hasUpgrade and player.upgrade) or
                   not (hasUpgrade or player.upgrade))):
                self.requestUpgrades()
                
            if ghost != player.ghost:
                if player.ghost:
                    player.respawn()
                else:
                    player.die()
            
            self.positionUpdate(msg.playerId, (msg.xPos, msg.yPos),
                    msg.yVel, angle=msg.angle, thrust=msg.ghostThrust)

    @handler(TaggedZoneMsg, gamePlug)
    def receiveTaggedZoneMsg(self, msg):
        # Zone has been tagged.

        zone = self.world.zoneWithId[msg.zoneId]
        team = self.world.teamWithId[msg.teamId]
        if team is None:
            self.receiveZoneTagged(None, None, zone)
        else:
            player = self.world.playerWithId[msg.playerId]
            self.receiveZoneTagged(team, player, zone)
            if not team.validate(msg.teamOrbCount):
                self.requestZones()
            if msg.killedTurret:
                self.receivePlayerKilled(msg.turretId, msg.playerId, None)
                
            self.world.updateStars(player, msg.playerStarCount)

    @handler(StartedTransactionMsg, gamePlug)
    def receiveStartedTransactionMsg(self, msg):
        # A transaction has begun
        team = self.world.teamWithId[msg.teamId]
        player = self.world.playerWithId[msg.playerId]
        upgrade = upgradeOfType[msg.upgradeType]
        transaction = transactionModule.Transaction(team, player,
                                                   upgrade, msg.timeLeft)
        transaction.addStars(player, msg.numStars)
        self.viewPlug.send(StartedTransaction(transaction))
            
    @handler(DeleteUpgradeMsg, gamePlug)
    def receiveDeleteUpgradeMsg(self, msg):
        # A player's upgrade is deleted
        player = self.world.playerWithId[msg.playerId]
        if player.upgrade is not None:
            self.viewPlug.send(DeleteUpgrade(player))
            player.upgrade.clientDelete()

    @handler(AddedStarsMsg, gamePlug)
    def receiveAddedStarsMsg(self, msg):
        # A player has added star(s) to a transaction
        team = self.world.teamWithId[msg.teamId]
        player = self.world.playerWithId[msg.playerId]
        if not self.world.validateTransaction(team, 's', msg.totalStars - msg.numStars):
            self.requestTransactionInfo(team)
            return
        self.world.addStarsToTransaction(team, player, msg.numStars)

    @handler(AbandonTransactionMsg, gamePlug)
    def receiveAbandonTransactionMsg(self, msg):
        # A transaction has been abandoned
        team = self.world.teamWithId[msg.teamId]
        if not self.world.validateTransaction(team, 'a', None):
            self.requestTransactionInfo(team)
            return
        self.world.abandonTransaction(team)
            
    @handler(UseUpgradeMsg, gamePlug)
    def receiveUseUpgradeMsg(self, msg):
        # A player is using an upgrade
        player = self.world.playerWithId[msg.playerId]
        self.positionUpdate(msg.playerId, (msg.xPos, msg.yPos))
        if not (player.upgrade and player.upgrade.upgradeType ==
                msg.upgradeType and not player.upgrade.inUse):
            # Correct our known data
            player.upgrade = upgradeOfType[msg.upgradeType](player)
        if isinstance(player.upgrade, Turret):
            zone = self.world.zoneWithId[msg.zoneId]
            if zone.turretedPlayer:
                # We think there's already a turreted player within.
                self.requestUpgrades()
        player.upgrade.clientUse()
        self.viewPlug.send(UseUpgrade(player))

    @handler(ValidateTransactionMsg, gamePlug)
    def receiveValidateTransactionMsg(self, msg):
        # Receive a validation of the current state of a transaction
        if msg.upgradeType == '\x00':
            team = self.world.teamWithId[msg.teamId]
            if team.currentTransaction:
                team.currentTransaction.abandon()
            return
        team = self.world.teamWithId[msg.teamId]
        player = self.world.playerWithId[msg.playerId]
        upgrade = upgradeOfType[msg.upgradeType]

        totalStars = 0
        contributors = {}
        index = 0
        while index+2 <= len(msg.contributions):
            pId = msg.contributions[index]
            numStars = struct.unpack('B', msg.contributions[index + 1])[0]
            plr = self.world.playerWithId[pId]
            contributors[plr] = numStars
            index += 2

        self.validateTransaction(team, contributors, totalStars,
                                        player, msg.timeLeft, upgrade)

    @handler(TransactionCompleteMsg, gamePlug)
    def receiveTransactionCompleteMsg(self, msg):
        # A transaction has been completed
        # Double checks that all the transaction info is correct, then
        # completes the transaction.
        team = self.world.teamWithId[msg.teamId]
        transaction = team.currentTransaction

        if transaction is None:
            # Get the correct data
            try:
                player = self.world.playerWithId[msg.playerId]
            except KeyError:
                logging.writeException()
                self.requestPlayers()
                return

            upgrade = upgradeOfType[msg.upgradeType]
            team.currentTransaction = transaction = \
                            transactionModule.Transaction(team,
                            player, upgrade)
            
            # Add the full complement of stars
            # TODO: I'm not sure whether this is right:
            transaction.addStars(player, upgrade.requiredStars)
            # We don't know for certain who donated how many stars.
            self.viewPlug.send(StartedTransaction(transaction))

        self.world.completeTransaction(team)

    @handler(RequestPlayerUpdateMsg, gamePlug)
    def receiveRequestPlayerUpdateMsg(self, msg):
        # Received from the server when it wants this client to send a player
        # update
        player = self.world.playerWithId[msg.playerId]
        if player.local:
            self.sendPlayerUpdate(player)

    @handler(RequestZoneUpdateMsg, gamePlug)
    def receiveRequestZoneUpdateMsg(self, msg):
        # Received from the server when it wants to know the player's
        # currentZone
        player = self.world.playerWithId[msg.playerId]
        if player.local:
            self.sendZoneChange(player, player.currentZone)

    @handler(ZoneChangeMsg, gamePlug)
    def receiveZoneChangeMsg(self, msg):
        # A player has changed their currentZone
        player = self.world.playerWithId[msg.playerId]
        if not player.local:
            zone = self.world.zoneWithId[msg.zoneId]
            player.changeZone(zone)

    @handler(ValidateZoneMsg, gamePlug)
    def receiveValidateZoneMsg(self, msg):
        zone = self.world.zoneWithId[msg.zoneId]
        orbOwner = self.world.teamWithId[msg.orbTeamId]
        zoneOwner = self.world.teamWithId[msg.zoneTeamId]

        zone.zoneOwner = zoneOwner
        if zone.orbOwner != orbOwner:
            # Keep track of correct orb counts when adjusting orb ownership.
            if zone.orbOwner is not None:
                zone.orbOwner.numOrbsOwned -= 1
            if orbOwner is not None:
                orbOwner.numOrbsOwned += 1
            zone.orbOwner = orbOwner

    @handler(ValidatePlayersMsg, gamePlug)
    def receiveValidatePlayersMsg(self, msg):
        # Get rid of any non-existant players
        playersToKick = []
        for player in list(self.world.playerWithId.itervalues()):
            if player.id not in msg.playerIds:
                player.removeFromGame()

    @handler(ValidatePlayerMsg, gamePlug)
    def receiveValidatePlayerMsg(self, msg):
        if self.world.playerWithId.has_key(msg.playerId):
            player = self.world.playerWithId[msg.playerId]
            player.ghost = bool(msg.isDead)
            # TODO: It might be worth checking that the other
            # information is correct too (current zone)
        else:
            team = self.world.teamWithId[msg.teamId]
            zone = self.world.zoneWithId[msg.zoneId]
            self.world.addPlayer(msg.nick.decode(),
                    team, msg.playerId, zone, dead=msg.isDead)
            player = self.world.playerWithId[msg.playerId]
        self.world.updateStars(player, msg.stars)

    @handler(ValidateUpgradesMsg, gamePlug)
    def receiveValidateUpgradesMsg(self, msg):
        # Get rid of any non-existant upgrades
        for player in self.world.playerWithId.itervalues():
            if player.upgrade and player.id not in msg.playerIds:
                player.upgrade.clientDelete()

    @handler(ValidateUpgradeMsg, gamePlug)
    def receiveValidateUpgradeMsg(self, msg):
        player = self.world.playerWithId[msg.playerId]
        if (player.upgrade is not None and 
                player.upgrade.upgradeType == msg.upgradeType):
            if msg.inUse and not player.upgrade.inUse:
                # Make sure we are in the right zone.
                if isinstance(player.upgrade, Turret):
                    newZone = self.world.zoneWithId[msg.zoneId]
                    if player.currentZone != newZone:
                        player.currentZone.removePlayer(player)
                        newZone.addPlayer(player)

                player.upgrade.clientUse()
            elif player.upgrade.inUse and not msg.inUse:
                # We think it's in use, but it's not. Delete and start over.
                player.upgrade.clientDelete()
                player.upgrade = upgradeOfType[msg.upgrateType](player)
        else:
            player.upgrade = upgradeOfType[msg.upgradeType](player)
            if msg.inUse:
                # Make sure we are in the right zone
                if isinstance(player.upgrade, Turret):
                    newZone = self.world.zoneWithId[msg.zoneId]
                    if player.currentZone != newZone:
                        player.currentZone.removePlayer(player)
                        newZone.addPlayer(player)
                        player.currentZone = newZone
                player.upgrade.clientUse()
        
    @handler(ValidateGameStatusMsg, gamePlug)
    def receiveValidateGameStatusMsg(self, msg):
        # Server is double-checking that we know the game status.
        if msg.state == 'P':
            self.world.gameState = GameState.PreGame
        elif msg.state == 'I':
            self.world.gameState = GameState.InProgress
            if msg.timed:
                self.world.setTimeLeft(msg.timeRemaining)
        elif msg.state == 'E':
            self.world.gameState = GameState.Ended

    @handler(ValidateTeamStatusMsg, gamePlug)
    def receiveValidateTeamStatusMsg(self, msg):
        # Server is double-checking that we know this team's status.
        team = self.world.teamWithId[msg.teamId]
        if msg.hasCaptain:
            team.captain = self.world.playerWithId[msg.captainId]
            # TODO: if the captain isn't the same, tell the user
        else:
            team.captain = None

        team.ready = bool(msg.ready)
        if msg.orbCount != team.numOrbsOwned:
            self.requestZones()

        if (msg.hasTransaction and team.currentTransaction) or \
                not (msg.hasTransaction or team.currentTransaction):
            # We are correct.
            pass
        else:
            # FIXME: players won't know about enemy transactions currently
            # so this shouldn't be called in that case.
            # Note that the server just won't send it in any case; but
            # there's no point in wasting the server's time
            self.requestTransactionInfo(team)

    @handler(ChatMsg, gamePlug)
    def receiveChatMsg(self, msg):
        # A chat is received
        sender = self.world.playerWithId[msg.senderId]
        if msg.kind == 't':     # Team
            team = self.world.teamWithId[msg.targetId]
            self.receiveChat(msg.text.decode(), sender, team)
        elif msg.kind == 'p':   # Private
            print 'Received private chat for player %d' % (ord(msg.targetId))
            receiver = self.world.playerWithId[msg.targetId]
            # Find the address to send it to:
            self.receiveChat(msg.text.decode(), sender, receiver)
        elif msg.kind == 'o':   # Open
            self.receiveChat(msg.text.decode(), sender, None)
        else:
            print 'Client: received unknown chat kind: %r' % (msg.kind,)

    @handler(ChatFromServerMsg, gamePlug)
    def receiveChatFromServerMsg(self, msg):
        self.viewPlug.send(ChatFromServer(msg.text.decode()))

    @handler(StartingSoonMsg, gamePlug)
    def receiveStartingSoonMsg(self, msg):
        self.viewPlug.send(StartingSoon(msg.delay))

    @handler(GotSettings, gamePlug)
    def gotSettings(self, msg):
        'Called when the server initially sends its settings.'
        self.serverSettings = settings = msg.settings

        layouts = []
        # Check if we know of all the map block layout files.
        for filename, checksum in settings['layoutDefs']:
            try:
                layouts.append(self.layoutDatabase.getLayout(filename,
                                                             checksum))
            except mapLayout.ChecksumError, E:
                self.requestMapBlock(filename,len(layouts))
                # Put a placeholder in
                layouts.append(None)
            except KeyError:
                self.requestMapBlock(filename,len(layouts))
                # Put a placeholder in
                layouts.append(None)
                
        self.layoutDefs = layouts
        if self.weKnowEnoughToBeConnected():
            self.connected(settings)

    def requestMapBlock(self, filename, id):
        raise UnknownMapBlock('Map block %r not found' % (filename,))

    def weKnowEnoughToBeConnected(self):
        return True

    def connected(self, settings):
        'Called when connection has been made and validated.'
        try:
            # Create a new universe based on the settings.
            halfMapWidth = self.serverSettings['halfMapWidth']
            mapHeight = self.serverSettings['mapHeight']

            self.world = universe.Universe(halfMapWidth, mapHeight)
            self.world.onZoneTagged.addListener(self.sendZoneTagged)
            self.world.onPlayerKilled.addListener(self.sendPlayerKilled)
            self.world.onShotDestroyed.addListener(self.shotDestroyed)
            self.world.onZoneChanged.addListener(self.sendZoneChange)
            self.world.onPlayerUpdate.addListener(self.sendPlayerUpdate)
            self.world.onShotFired.addListener(self.sendShotFired)
            self.world.onPlayerRespawn.addListener(self.sendPlayerRespawn)
            self.world.onAbandonTransaction.addListener(self.abandonTransaction)
            self.world.onUpgradeReqDel.addListener(self.upgradeDelete)
            self.world.onUpgradeReqUse.addListener(self.useUpgrade)
            self.world.onGrenadeExploded.addListener(self.sendGrenadeExploded)
            
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

        except Exception, e:
            logging.writeException()
            self._errorConnecting(e.args[0])
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
        
    def disconnect(self):
        self.onClosed.execute()

    @handler(ServerShutdownMsg, gamePlug)
    def receiveServerShutdownMsg(self, msg):
        pass

class UnknownMapBlock(Exception):
    pass

class UnableToConnect(Exception):
    pass

# TODO: This is set up as a subclass of Client for convenience, but it would
# be better design to have it as a separate component.
class NetworkClient(Client):

    def __init__(self, app):
        Client.__init__(self, app)
        self.nethandler = None
        self.netman = app.netman
        self.intentionalDisconnect = False

        # Initialise layout database.
        self.missingMapBlocks = {}
        self.missingGraphics = {}
        self.nonRetrievedMapBlocks = []

    ######### Connecting to server.

    def connectByPort(self, ipAddr, port):
        result = defer.Deferred()
        try:
            self.nethandler = ClientNetHandler(self.netman, ipAddr, port)
            self.gamePlug.connectPlug(self.nethandler.plug)
        except Exception, e:
            logging.writeException()
            result.errback(e)
            return result
        
        self.connectingDeferred = result
        result.addErrback(self._cancelConnecting)

        return result

    @handler(ErrorConnecting, Client.gamePlug)
    def receiveErrorConnecting(self, msg):
        self._errorConnecting(msg.reason)

    def _errorConnecting(self, reason):
        self.connectingDeferred.errback(UnableToConnect(reason))
        self.nethandler = None

    def _cancelConnecting(self, error):
        'Used as an errback for connectingDeferred.'

        print 'Client: cancelling connecting'
        self.connectingDeferred = None

        self.intentionalDisconnect = True
        self.clientConnectionLost()
        return error

    def cancelConnecting(self, error = None):
        print 'Client: Attempting to cancel connection'
        if self.connectingDeferred is None:
            raise ValueError('Cannot cancel connecting when not connecting.')
        return self._cancelConnecting(error)

    def requestMapBlock(self, filename, missingID):
        self.missingMapBlocks[missingID] = filename
        self.nonRetrievedMapBlocks.append(missingID)
        self.missingGraphics[missingID] = True
        self.gamePlug.send(RequestMapBlock(missingID, filename))

    def weKnowEnoughToBeConnected(self):
        return len(self.nonRetrievedMapBlocks) == 0 and len(self.missingGraphics) == 0

    @handler(MapBlockMsg, Client.gamePlug)
    def receiveMapBlockMsg(self, msg):
        'Called when the server sends map block information.'
        if msg.missingID in self.nonRetrievedMapBlocks:
            filename = self.missingMapBlocks[msg.missingID]
            self.nonRetrievedMapBlocks.remove(msg.missingID)
            userPath = getPath(user, 'blocks')
            path = os.path.join(userPath, filename)
            try:
                base, ext = filename.rsplit('.', 1)
            except ValueError:
                base, ext = filename, ''

            newGraphicPath = os.path.join(userPath, base) + '.png'                

            i=1
            while os.path.exists(newGraphicPath) or \
                  os.path.exists(path):
                i+=1
                nameMinusExt = "%s_%d_%03d" % (os.path.join(userPath, base), msg.missingID, i)
                path = nameMinusExt + '.block'
                newGraphicPath = nameMinusExt + '.png'
            
            f = file(path, 'w')
            contents = msg.contents

            assert msg.missingID in self.missingGraphics
            assert not os.path.exists(newGraphicPath)

            self.missingGraphics[msg.missingID] = newGraphicPath
            self.missingMapBlocks[msg.missingID] = path

            f.write(contents)
            f.close()
            
            # Have we all the information now?
            if self.weKnowEnoughToBeConnected():
                self.connected(self.serverSettings)
        else:
            print 'Received same mapblock definition twice'

    @handler(MapBlockGraphicsMsg, Client.gamePlug)
    def receiveMapBlockGraphicsMsg(self, msg):        
        'Called when the server sends map block graphics.'
        if msg.missingID in self.missingGraphics:
            assert msg.missingID not in self.nonRetrievedMapBlocks
            filename = self.missingGraphics[msg.missingID]
            if filename == True: # A placeholder - must not have received mapblock correctly
                error = 'Map transfer error'
                self._errorConnecting(error)
                raise IOError(error)
            
            del self.missingGraphics[msg.missingID]
            assert not os.path.exists(filename)
            assert(not msg.missingID in self.nonRetrievedMapBlocks)
            f = file(filename, 'wb')
            f.write(msg.data)
            f.close()
            self._addToLayoutsFromUserDir(self.missingMapBlocks[msg.missingID], msg.missingID)
                
            
            
            # Have we all the information now?
            if self.weKnowEnoughToBeConnected():
                self.connected(self.serverSettings)
        else:
            print 'Received same graphics definition twice'

    def _getNewGraphicName(self, missingID, path, base, extension):
        i=0
        while os.path.exists("%s_%d_%03d.%s" % (os.path.join(path, base), missingID, i, extension)):
            i+=1
        return "%s_%d_%03d.%s" % (base, missingID, i, extension)
        

    def _addToLayoutsFromUserDir(self, fn, index):
        if not self.layoutDatabase.addLayoutAtFilename(getPath(user, 'blocks'), fn):
            self._errorConnecting('Invalid map from the server')
        layout = self.layoutDatabase.layoutsByFilename[fn]
        if self.layoutDefs[index] is not None:
            self._errorConnecting('Invalid block data. Try reconnecting')
            raise Exception
        else:
            self.layoutDefs[index] = layout
        

    def disconnect(self):
        print 'Client: disconnecting from server.'
        if self.nethandler is None:
            return defer.fail(Exception('Not connected'))
        self.intentionalDisconnect = True
        self.netman.closeConnection(self.nethandler.connId)

    @handler(ConnectionLost)
    def receiveConnectionLost(self, msg):
        self.clientConnectionLost()

    def clientConnectionLost(self):
        '''Called when the tcp connection to the server is lost.'''
        self.gamePlug.disconnectAll()
        if self.nethandler is not None:
            self.nethandler = None
        if not self.intentionalDisconnect:
            reason = 'Lost connection to server'
        else:
            # reset it
            self.intentionalDisconnect = False
            reason = None

        # Tell the main interface that connection was lost.
        # TODO: Do this as a message too.
        self.onClosed.execute(reason)
        
    @handler(ServerShutdownMsg, Client.gamePlug)
    def receiveServerShutdownMsg(self, msg):
        print 'Client: Server shutting down.'
        self.nethandler.disconnect()

    def connected(self, settings):
        Client.connected(self, settings)

        # Connection made successfully. Call callback.
        print 'Client: Connection established and validated.'
        self.connectingDeferred.callback(self.world)
        self.gamePlug.send(ReadyForDynamicDetailsMsg())

