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

from trosnoth.src.model.player import Player
from trosnoth.src.model.upgrades import upgradeNames

from trosnoth.src.utils.math import distance

# Component message passing
from trosnoth.src.utils.components import *
from trosnoth.src.messages.chat import *
from trosnoth.src.messages.game import *
from trosnoth.src.messages.gameplay import *
from trosnoth.src.messages.players import *
from trosnoth.src.messages.shot import *
from trosnoth.src.messages.transactions import *
from trosnoth.src.messages.validation import NotifyUDPStatus

class InterfaceComponent(Component):

    plug = Plug()

    def __init__(self, gameInterface):
        super(InterfaceComponent, self).__init__()
        self.gameInterface = gameInterface
        self.detailsInterface = gameInterface.detailsInterface
        self.gameViewer = gameInterface.gameViewer

    @handler(AddPlayer)
    def addPlayer(self, msg):
        player = msg.player
        message = '%s has joined %s' % (player.nick, player.team)
        self.detailsInterface.newMessage(message)
        self.gameViewer.worldgui.addPlayer(player)

    @handler(RemovePlayer)
    def removePlayer(self, msg):
        player = msg.player
        message = '%s has left the game' % (player.nick,)
        self.detailsInterface.newMessage(message)
        self.gameViewer.worldgui.removePlayer(player)

    @handler(GameStart)
    def gameStart(self, msg):
        message = 'The game is now on!!'
        self.detailsInterface.newMessage(message)
        if self.gameViewer.timerBar:
            self.gameViewer.timerBar.loop()
        self.gameViewer.pregameMessage.setText('')
        #self.playSound('start', 1)

    @handler(GameOver)
    def gameOver(self, msg):
        self.detailsInterface.gameOver(msg.winningTeam)
        if msg.timeOver:
            message2 = 'Game time limit has expired'
            self.detailsInterface.newMessage(message2)
        if self.gameViewer.timerBar:
            self.gameViewer.timerBar.gameFinished()
        #self.playSound('end', 1)

    @handler(SetCaptain)
    def setCaptain(self, msg):
        player = msg.captain
        self.detailsInterface.newMessage("%s is %s's captain" %
                (player.nick, player.team), player.team.chatColour)

    @handler(TeamIsReady)
    def teamIsReady(self, msg):
        player = msg.player
        self.detailsInterface.newMessage('%s is ready' %
                                         (player.team,),
                                         player.team.chatColour)

    @handler(StartedTransaction)
    def startedTransaction(self, msg):
        # Prompt the player, seeing if they want to contribute
        player = msg.transaction.purchasingPlayer
        interface = self.detailsInterface
        interface.transactionStarted(msg.transaction)
        upgrade = msg.transaction.upgrade
        if isinstance(interface.player, Player) and \
           interface.player.team == player.team and interface.player != player:
            message = '%s wants to buy a %s. Contribute?' % (player.nick,
                    upgradeNames[upgrade])
            interface.getStars(message, interface._addStars)

    @handler(TransactionChanged)
    def transactionChanged(self, msg):
        self.detailsInterface.transactionChanged(msg.transaction)

    @handler(DeleteUpgrade)
    def deleteUpgrade(self, msg):
        player = msg.player
        message = "%s's %s is gone" % (player.nick, \
                                       repr(player.upgrade))
        self.detailsInterface.newMessage(message)

    @handler(UseUpgrade)
    def useUpgrade(self, msg):
        player = msg.player
        message = '%s is using %s' % (player.nick, \
                                      repr(player.upgrade))
        self.detailsInterface.newMessage(message)

    @handler(ChatFromServer)
    def gotChatFromServer(self, msg):
        self.detailsInterface.newMessage(msg.text)

    @handler(StartingSoon)
    def startingSoon(self, msg):
        self.detailsInterface.newMessage('Both teams are ready. Game starting in %d seconds' % msg.delay)
        self.gameViewer.pregameMessage.setText('Prepare yourself...')


    @handler(TaggedZone)
    def taggedZone(self, msg):
        self.gameInterface.reDraw()
        player, zone = msg.player, msg.zone
        owner = ''
        if zone.orbOwner == None:
            owner = 'neutral '
        
        if player is not None:
            message = '%s tagged %szone %3d' % (player.nick, owner, zone.id)
        else:
            message = 'Zone %3d rendered neutral' % (zone.id)
        self.detailsInterface.newMessage(message)
        # Draw a star.
        rect = self.gameViewer.worldgui.getPlayerSprite(player).rect
        self.detailsInterface.starGroup.star(rect.center)
        #self.playSound('tag', 1)

    @handler(PlayerKilled)
    def playerKilled(self, msg):
        killer, target = msg.killer, msg.target
        message = '%s killed %s' % (killer.nick, target.nick)
        self.detailsInterface.newMessage(message)
        # Draw the star animation if applicable.
        if killer.local:
            # Perhaps we should move this functionality to the worldgui itself
            rect = self.gameViewer.worldgui.getPlayerSprite(target).rect
            self.detailsInterface.starGroup.star(rect.center)
        dist = self.distance(target.pos)
        #self.playSound('die', self.getSoundVolume(dist))

        self.detailsInterface.playerKilled(target, killer)

    @handler(PlayerRespawn)
    def playerRespawn(self, msg):
        message = '%s is back in the game' % (msg.player.nick,)
        self.detailsInterface.newMessage(message)
        dist = self.distance(msg.player.pos)
        #self.playSound('respawn', self.getSoundVolume(dist))

        self.detailsInterface.playerRespawned(msg.player)

    @handler(OwnChat)
    def ownChat(self, msg):
        self.detailsInterface.sentChat(msg.text, msg.team, msg.target)
        
    @handler(Chat)
    def chat(self, msg):
        self.detailsInterface.newChat(msg.text, msg.sender, msg.target)
        #self.playSound('chat', 1)

    @handler(ShotFired)
    def shotFired(self, msg):
        pos = msg.shot.pos
        dist = self.distance(pos)
        self.gameViewer.worldgui.addShot(msg.shot)
        #self.playSound('shoot', self.getSoundVolume(dist))

    @handler(NotifyUDPStatus)
    def udpStatusChanged(self, msg):
        if msg.connected:
            self.detailsInterface.udpNotifier.hide()
        else:
            self.detailsInterface.udpNotifier.show()

    def distance(self, pos):
        return distance(self.gameViewer.viewManager.getTargetPoint(), pos)

    def getSoundVolume(self, distance):
        'The volume for something that far away from the player'
        # Up to 500px away is within the "full sound zone" - full sound
        distFromScreen = max(0, distance - 500)
        # 1000px away from "full sound zone" is 0 volume:
        return 1 - (distFromScreen / 1000)

    def playSound(self, action, volume=1):
        self.gameInterface.app.soundPlayer.play(action, volume)
