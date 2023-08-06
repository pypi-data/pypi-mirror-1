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

from twisted.internet import reactor
import pygame

from trosnoth.src.gui.framework import framework
from trosnoth.src.gui.common import Location, FullScreenAttachedPoint, ScaledSize, Area
from trosnoth.src.gui.framework.unobtrusiveValueGetter import NumberGetter, YesNoGetter

from trosnoth.src.trosnothgui.ingame.messagebank import MessageBank
from trosnoth.src.trosnothgui.ingame.stars import StarGroup
from trosnoth.src.trosnothgui.ingame.udpnotify import UDPNotificationBar
from trosnoth.src.trosnothgui.ingame import mainMenu
from trosnoth.src.trosnothgui.ingame.transactionGUI import TransactionGUI
from trosnoth.src.trosnothgui.ingame.gauges import TurretGauge, RespawnGauge, UpgradeGauge
from trosnoth.src.trosnothgui.ingame import colours

from trosnoth.src.base import MenuError
import trosnoth.src.model.transaction as transactionModule
from trosnoth.src.model.upgrades import Turret, Shield, MinimapDisruption, PhaseShift, Grenade, Ricochet, upgradeNames
from trosnoth.src.model.team import Team
from trosnoth.src.model.player import Player

class DetailsInterface(framework.CompoundElement):
    '''Interface containing all the overlays onto the screen:
    chat messages, player lists, gauges, stars, transaction requests, etc.'''
    def __init__(self, app, gameInterface):
        super(DetailsInterface, self).__init__(app)
        world = gameInterface.world
        self.gameInterface = gameInterface

        # Maximum number of messages viewable at any one time
        maxView = 8

        self.world = world
        rect = pygame.Rect((0,0), self.app.screenManager.scaledSize)
        self.player = None
        self.currentMessages = MessageBank(self.app, maxView, 50,
                                           Location(FullScreenAttachedPoint(ScaledSize(-40,-40),'bottomright'), 'bottomright'),
                                           'right', 'bottom',
                                           self.app.screenManager.fonts.messageFont)
        self.currentChats = MessageBank(self.app, maxView, 50, Location(FullScreenAttachedPoint(ScaledSize(40,256),'topleft'), 'topleft'), 'left', 'top',
                                        self.app.screenManager.fonts.messageFont)
        # If we want to keep a record of all messages and their senders
        self.allMessages = []
        self.transactionGUI = None
        self.input = None
        self.inputText = None
        self.unobtrusiveGetter = None
        self.turretGauge = None
        self.respawnGauge = None
        self.upgradeGauge = None
        self.starGroup = StarGroup(self.app)
        self.udpNotifier = UDPNotificationBar(self.app)

        menuloc = Location(FullScreenAttachedPoint((0,0), 'bottomleft'), 'bottomleft')
        self.menuManager = mainMenu.MainMenu(self.app, menuloc, self, self.gameInterface.keyMapping)
        self.elements = [self.currentMessages, self.currentChats,
                         self.starGroup, self.udpNotifier]

    def gameOver(self, winningTeam):
        self.gameInterface.gameOver(winningTeam)

    def setPlayer(self, player):
        self.player = player
        if self.menuManager not in self.elements:
            self.elements.append(self.menuManager)

    def _getUpgrade(self, stars, upgrade):
        try:
            startingStars = int(stars)
        except:
            raise MenuError, "Please enter a valid value"
        else:
            if not self.player.hasThisManyStars(startingStars):
                raise MenuError, "You do not have that many stars"
            else:
                self.gameInterface.netClient.startTransaction(upgrade, self.player, stars)

    def _requestUpgrade(self, upgradeType):
        result, reason = self.player.canRequestUpgrade(upgradeType)
        if result:
            self.getStars('How many stars to contribute from the start?', self._getUpgrade, upgradeType)
        else:
            raise MenuError, reason

    def _addStars(self, numStars):
        result, reason = self.player.canAddStarsNow(numStars)
        if result:
            self.gameInterface.netClient.addStars(self.player.team, self.player, numStars)
        else:
            raise MenuError, reason
        
        

    def doAction(self, action):
        '''
        Activated by hotkey or menu.
        action corresponds to the action name in the keyMapping.
        '''
        if action == 'leaderboard':
            self.showPlayerDetails()
            self.menuManager.manager.reset()
        elif action == 'toggle interface':
            self.toggleInterface()
            self.menuManager.manager.reset()
        elif action == 'more actions':
            if self.menuManager is not None:
                self.menuManager.showMoreMenu()
        elif action == 'leave':
            # Disconnect from the server.
            self.gameInterface.disconnect()
        elif action == 'menu':
            # Return to main menu and show or hide the menu.
            if self.menuManager is not None:
                self.menuManager.escape()
        elif action == 'follow':
            if self.gameInterface.world.replay:
                # Replay-specific: follow the action.
                self.gameInterface.gameViewer.setTarget(None)
    
        # All actions after this line should require a player.
        if self.player is None:
            return
        if action == 'respawn':
            result, reason = self.player.canRespawn()
            if result:
                self.player.requestRespawn()
            else:
                raise MenuError, reason
        elif action == 'turret':
            self._requestUpgrade(Turret)
            self.menuManager.manager.reset()
        elif action == 'shield':
            self._requestUpgrade(Shield)
            self.menuManager.manager.reset()
        elif action == 'minimap disruption':
            self._requestUpgrade(MinimapDisruption)
            self.menuManager.manager.reset()
        elif action == 'phase shift':
            self._requestUpgrade(PhaseShift)
            self.menuManager.manager.reset()
        elif action == 'grenade':
            self._requestUpgrade(Grenade)
            self.menuManager.manager.reset()
        elif action == 'ricochet':
            self._requestUpgrade(Ricochet)
            self.menuManager.manager.reset()
        elif action == 'use upgrade':
            result, reason = self.player.canUseUpgrade()
            if result:
                self.player.requestUse()
            else:
                raise MenuError, reason
            self.menuManager.manager.reset()
        elif action == 'add stars':
            result, reason = self.player.canAddStars()
            if result:
                self.getStars('How many stars to contribute?', self._addStars)
            else:
                raise MenuError, reason
            
            self.menuManager.manager.reset()
        elif action == 'abandon':
            self.abandon(self.player)
            self.menuManager.manager.reset()
        elif action == 'chat':
            self.chat()
            self.menuManager.manager.reset()
        elif action == 'captain':
            self.becomeCaptain()
            self.menuManager.manager.reset()
        elif action == 'team ready':
            self.teamReady()
            self.menuManager.manager.reset()
        elif action == 'buy upgrade':
            if self.menuManager is not None:
                self.menuManager.showBuyMenu()

    def transactionStarted(self, transaction):
        '''Called when a transaction is started, so it can display this
        information to the user'''
        # There may be an existing transaction which is completed/abandoned, but still on screen
        if self.transactionGUI:
            if self.transactionGUI.transaction.state not in (transactionModule.TransactionState.Abandoned, transactionModule.TransactionState.Completed):
                # We must have had some bad information
                print 'We had incorrect transaction information.'
            self.elements.remove(self.transactionGUI)
            del self.transactionGUI
            self.transactionGUI = None

        # If we're not focusing on a player, do not show the GUI.
        # Although perhaps if we were 'focusing' on a team, we could...
        # Count that as a TODO.
        if not (self.player and transaction.purchasingTeam is self.player.team):
            return


        self.transactionGUI = TransactionGUI(self.app, Location(FullScreenAttachedPoint(ScaledSize(200,0), 'topleft'), 'topleft'), transaction, self.player)
        self.elements.append(self.transactionGUI)

        def deleteTransGUI(transactionGUI):
            '''Removes the TransactionGUI object from the screen'''
            # This check is necessary in case another one was created
            # while one was still up
            if transactionGUI is self.transactionGUI:
                if transactionGUI in self.elements:
                    self.elements.remove(transactionGUI)
                else:
                    print 'SOMEWHAT BAD: transactionGUI not in elements'
                self.transactionGUI = None

        def transactionChanged(sender, state):
            assert transaction is sender
            if state in (transactionModule.TransactionState.Abandoned, transactionModule.TransactionState.Completed):
                self.newMessage("%s's Transaction %s" % (repr(transaction.purchasingTeam), transactionModule.TransactionStateText[state]), colours.transactionMessageColour)
                reactor.callLater(3, deleteTransGUI, self.transactionGUI)

        # Set up a message to display to the screen when someone adds star(s)
        fAddStarsMessage = lambda sender, player, stars: self.newMessage('%s added %d star%s' % (player.nick, stars, ('s', '')[stars == 1]), colours.transactionMessageColour)

        self.newMessage('%s purchasing %s' % (transaction.purchasingPlayer.nick, upgradeNames[transaction.upgrade]), colours.transactionMessageColour)
                                                                         
        transaction.onNumStarsChanged.addListener(fAddStarsMessage)
        transaction.onStateChanged.addListener(transactionChanged)

    def transactionChanged(self, transaction):
        if self.transactionGUI is None or self.transactionGUI.transaction != transaction:
            self.transactionStarted(transaction)
        else:
            # It should automatically detect any changes.
            pass

    def newMessage(self, text, colour = colours.grey):
        self.currentMessages.newMessage(text, colour)
        self.allMessages.append((text))

    def newChat(self, text, sender, private):
        if sender is self.player:
            # Don't bother receiving messages from myself.
            return
        
        nick = sender.nick
        if not private:
            # Message for everyone
            extra = ': '
            self.allMessages.append((nick, text))
            
        elif isinstance(private, Player) and self.player is private:
            # Destined for the one player
            extra = ' (private): '
            self.allMessages.append((nick, '#P# ' + text))
            
        elif isinstance(private, Team) and self.player is not None and \
                self.player.team == private:
            # Destined for the one team.
            extra = ': '
            self.allMessages.append((nick, text))
            
        else:
            # May not have been destined for our player after all.
            print "Don't want this text"
            return
        allText = nick + extra + text
        self.currentChats.newMessage(allText, sender.team.chatColour)

    def sentChat(self, text, team, private):
        if not private:
            # Message for everyone
            extra = 'Me (open): '
            self.allMessages.append(('Me (open):', text))
            
        elif isinstance(private, Player):
            # Destined for the one player
            extra = 'Me (to_%s): ' % (private.nick)
            self.allMessages.append((extra, '#P# ' + text))
            
        elif isinstance(private, Team):
            # Destined for the one team.
            extra = 'Me: '
            self.allMessages.append(('Me', text))
            
        else:
            # May not have been destined for our player after all.
            print "Don't want this text"
            return
        allText = extra + text
        self.currentChats.newMessage(allText, team.chatColour)

    def processEvent(self, event):
        '''Event processing works in the following way:
        1. If there is a prompt on screen, the prompt will either use the
        event, or pass it on.
        2. If passed on, the event will be sent back to the main class, for it
        to process whether player movement uses this event. If it doesn't use
        the event, it will pass it back.
        3. If so, the hotkey manager will see if the event means anything to it.
        If not, that's the end, the event is ignored.'''

        try:
            return super(DetailsInterface, self).processEvent(event)
        except MenuError, err:
            self.newMessage(err.value, colours.errorMessageColour)
            self.endInput()
            return None


    def endInput(self):
        if self.input:
            self.elements.remove(self.input)
            self.input = None
        if self.inputText:
            self.elements.remove(self.inputText)
            self.inputText = None
        if self.unobtrusiveGetter:
            self.elements.remove(self.unobtrusiveGetter)
            self.unobtrusiveGetter = None
        if self.menuManager is not None and self.menuManager not in self.elements:
            self.elements.append(self.menuManager)
        self.input = self.inputText = None
        

    def inputStarted(self):
        self.elements.append(self.input)
        self.elements.append(self.inputText)
        self.input.onEsc.addListener(lambda sender: self.endInput())
        self.input.onEnter.addListener(lambda sender: self.endInput())
        if self.menuManager is not None:
            try:
                self.elements.remove(self.menuManager)
            except ValueError:
                pass



    def chat(self):
        if not self.player:
            return

        self.gameInterface.gameViewer.openChat(self.player)
        

    def getStars(self, message, function, *params):
        '''Called when a number of stars is requested.
        function is the function that should be called when the number of
        stars has been inputted'''
        self.endInput()
        self.unobtrusiveGetter = NumberGetter(self.app, Location(FullScreenAttachedPoint((0,0), 'center'), 'center'), message, self.app.screenManager.fonts.unobtrusivePromptFont, colours.unobtrusivePromptColour, 3)
        self.elements.append(self.unobtrusiveGetter)
        def gotValue(num):
            if self.unobtrusiveGetter:
                self.elements.remove(self.unobtrusiveGetter)
                self.unobtrusiveGetter = None
            function(num, *params)
                
        self.unobtrusiveGetter.onGotValue.addListener(gotValue)


    def abandon(self, player):
        '''Called when a player says they wish to abandon their upgrade, or
        the transaction they initiated'''
        if player.upgrade:
            addOn = 'Upgrade'
        elif player.team.currentTransaction and \
                player.team.currentTransaction.purchasingPlayer is player:
            addOn = 'Transaction'
        else:
            return

        message = 'Really abandon your ' + addOn + ' (Y/N)'
        self.endInput()
        self.unobtrusiveGetter = YesNoGetter(self.app, Location(FullScreenAttachedPoint((0,0), 'center'), 'center'), message, self.app.screenManager.fonts.unobtrusivePromptFont, colours.unobtrusivePromptColour, 3)
        self.elements.append(self.unobtrusiveGetter)

        def gotValue(abandon):
            if self.unobtrusiveGetter:
                self.elements.remove(self.unobtrusiveGetter)
                self.unobtrusiveGetter = None
            if abandon:
                player.abandon()
                
        self.unobtrusiveGetter.onGotValue.addListener(gotValue)
        


    def upgradeUsed(self, player):
        if player is self.player:
            if self.upgradeGauge is not None:
                # Remove the existing one.
                print 'Stray upgradeGauge!'
                self.elements.remove(self.upgradeGauge)
            self.upgradeGauge = UpgradeGauge(self.app, Area(FullScreenAttachedPoint(ScaledSize(0,-20), 'midbottom'), ScaledSize(100,30), 'midbottom'), player)
            self.elements.append(self.upgradeGauge)

    def upgradeDestroyed(self, player):
        if player is self.player and self.upgradeGauge is not None:
            self.elements.remove(self.upgradeGauge)
            self.upgradeGauge = None

    def turretStarted(self, player):
        if player is self.player:
            self.turretGauge = TurretGauge(self.app, Area(FullScreenAttachedPoint(ScaledSize(0,-60), 'midbottom'), ScaledSize(100,30), 'midbottom'), player)
            self.elements.append(self.turretGauge)

    def turretEnded(self, player):
        if player is self.player:
            self.elements.remove(self.turretGauge)
            self.turretGauge = None

    def playerKilled(self, player, killer):
        if player is self.player:
            if self.respawnGauge is not None:
                self.elements.remove(self.respawnGauge)
            self.respawnGauge = RespawnGauge(self.app, Area(FullScreenAttachedPoint(ScaledSize(0,-20), 'midbottom'), ScaledSize(100,30), 'midbottom'), player)
            self.elements.append(self.respawnGauge)

    def playerRespawned(self, player):
        if player is self.player and self.respawnGauge is not None:
            self.elements.remove(self.respawnGauge)
            self.respawnGauge = None

    def becomeCaptain(self):
        if self.player:
            self.gameInterface.netClient.setAsCaptain(self.player)

    def teamReady(self):
        if self.player:
            self.gameInterface.netClient.teamReady(self.player)

    def showPlayerDetails(self):
        self.gameInterface.gameViewer.toggleLeaderBoard()

    def toggleInterface(self):
        self.gameInterface.gameViewer.toggleInterface()
