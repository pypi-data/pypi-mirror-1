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

'''interface.py - defines the Interface class which deals with drawing the
game to the screen, including menus and other doodads.'''

import os, sys

import pygame
from twisted.internet import defer, reactor, task
from math import atan2

import trosnoth
from trosnoth.src.base import MenuError
import trosnoth.src.trosnothgui.ingame.viewManager as viewManager
import trosnoth.src.networkClient as networkClient
from trosnoth.src.universe import Team, Player
from trosnoth.src.gui.framework import prompt, hotkey
from trosnoth.src.gui.framework.dialogbox import DialogBox, DialogResult, DialogBoxAttachedPoint
from trosnoth.src.gui import keyboard
from trosnoth.src import keymap
from trosnoth.src.trosnothgui.ingame import mainMenu
import trosnoth.src.transaction as transactionModule
from trosnoth.src.upgrades import upgradeNames
from trosnoth.src.upgrades import Turret, Shield, MinimapDisruption, PhaseShift, Grenade

from trosnoth.src.gui.framework import framework, elements, listbox
from trosnoth.src.gui.framework.unobtrusiveValueGetter import NumberGetter, YesNoGetter
from trosnoth.src.gui.framework.elements import PictureElement

from trosnoth.src.trosnothgui.pregame.startupInterface import StartupInterface
from trosnoth.src.trosnothgui.credits import CreditsScreen
from trosnoth.src.trosnothgui.ingame.messagebank import MessageBank
from trosnoth.src.trosnothgui.ingame.transactionGUI import TransactionGUI
from trosnoth.data import loadSprite, user, getPath
from trosnoth.src.utils.getUserInfo import getName, writeName
from trosnoth.src.trosnothgui.defines import *

from trosnoth.src.trosnothgui.ingame import colours
from trosnoth.src.trosnothgui import pregame

from trosnoth.src.gui.common import ScaledLocation, Location, ScaledSize, FullScreenAttachedPoint, Area, addPositions, ScaledArea, AttachedPoint

from trosnoth.src.gui.screenManager.windowManager import MultiWindowException

class Interface(framework.CompoundElement):
    def __init__(self, app, netClient=None):
        super(Interface, self).__init__(app)
        
        # Set up the NetworkClient object.
        if netClient is None:
            self.netClient = networkClient.NetworkClient(self)
        else:
            self.netClient = netClient
            netClient.mainInterface = self
            netClient.interface = None
        self.server = None

        # Create an interfaces for pre- and post-connection.
        self.startupInterface = StartupInterface(app, self)
        self.activeInterface = self.startupInterface
        
        img = loadSprite('pointer.bmp')
        img.set_colorkey((255,255,255))
        pointer = PictureElement(self.app, img, pygame.mouse.get_pos())
        self.app.screenManager.setPointer(pointer)
        pygame.mouse.set_visible(0)
        
        self.elements = [self.startupInterface]

    def processEvent(self, event):
        # Capture the quit event.
        if event.type == pygame.QUIT:                
            reactor.stop()
            return
        return super(Interface, self).processEvent(event)
    
    def startServer(self, serverName, halfMapWidth = None, mapHeight = None,
                    maxPlayers = None, gameDuration = None, recordReplay = None):
        'Starts a server.'
        if self.server is not None:
            if self.server.running:
                return
            else:
                del self.server
        settings = {}
        
        if halfMapWidth != None:
            settings['halfMapWidth'] = halfMapWidth
        if mapHeight != None:
            settings['mapHeight'] = mapHeight
        if maxPlayers != None:
            settings['maxPlayers'] = maxPlayers
        if gameDuration != None:
            settings['gameDuration'] = gameDuration
        if recordReplay != None:
            settings['recordReplay'] = recordReplay
            
        from trosnoth.src.networkServer import NetworkServer

        try:
            # TODO: make sure there aren't two servers of the same name
            self.server = NetworkServer(serverName, 6789, settings = settings)
        except Exception, e:
            # Creating a local server failed
            print e

    def connectionEstablished(self, world):
        'Called when this client establishes a connection to a server.'
        self.startupInterface.connectionComplete()

        # Create a game interface.
        gi = GameInterface(self.app, self, world)
        self.elements = [gi]

    def connectionLost(self):
        self.elements = [self.startupInterface]

class GameInterface(framework.CompoundElement):
    '''Interface for when we are connected to a server.'''

    def __init__(self, app, mainInterface, world):
        super(GameInterface, self).__init__(app)
        self.interface = mainInterface
        self.world = world

        # Set up the keyboard mapping.
        self.keyMapping = keyboard.KeyboardMapping(keymap.default_game_keys)

        try:
            # Try to load keyboard mappings from the user's personal settings.
            config = open(getPath(user, 'keymap'), 'rU').read()
            self.keyMapping.load(config)
        except IOError:
            pass

        # TODO: it would make more sense to me to put gameViewer in
        #       playerInterface; but... whatever works for now.
        self.gameViewer = viewManager.GameViewer(self.app, self, world)
        if world.replay:
            self.gameMenu = ReplayMenu(self.app, self, world)
        else:
            self.gameMenu = GameMenu(self.app, self, world)
        self.detailsInterface = DetailsInterface(self.app, self)
        self.runningPlayerInterface = None
        self.observerInterface = ObserverInterface(self.app, self)
        self.menuHotkey = hotkey.MappingHotkey(self.app, 'menu', mapping=self.keyMapping)
        self.menuHotkey.onActivated.addListener(self.showMenu)
        self.elements = [
                         self.gameViewer, self.gameMenu,
                         self.menuHotkey, self.detailsInterface
                        ]
        self.hotkeys = hotkey.Hotkeys(self.app, self.keyMapping, self.detailsInterface.doAction)
        self.menuShowing = True
        self.gameOverScreen = None

        self.vcInterface = None
        if world.replay:
            self.vcInterface = ViewControlInterface(self.app, self)
            self.elements.append(self.vcInterface)
            self.hideMenu()

    def joined(self, player):
        '''Called when joining of game is successful.'''
        print 'Joined game ok.'

        self.runningPlayerInterface = pi = PlayerInterface(self.app, self, player)
        self.detailsInterface.setPlayer(player)
        self.elements = [self.gameViewer,
                         pi, self.menuHotkey, self.hotkeys, self.detailsInterface]

    def showMenu(self):
        if self.runningPlayerInterface is not None:
            if self.runningPlayerInterface.player is not None:
                # Can't get to this particular menu after you've joined the game.
                return
        self.elements = [self.gameViewer, self.gameMenu]
        self.menuShowing = True

    def minimapDisruption(self, player):
        self.gameViewer.minimapDisruption(player)

    def endMinimapDisruption(self):
        self.gameViewer.endMinimapDisruption()

    def hideMenu(self):
        if self.runningPlayerInterface is not None:
            self.elements = [self.gameViewer, self.runningPlayerInterface, self.gameMenu, self.menuHotkey,
                             self.hotkeys, self.detailsInterface]
        else:
            self.elements = [self.gameViewer, self.observerInterface, self.gameMenu, self.menuHotkey,
                             self.hotkeys, self.detailsInterface]
        if self.vcInterface is not None:
            self.elements.insert(2, self.vcInterface)

        if self.gameOverScreen:
            self.elements.append(self.gameOverScreen)
        self.menuShowing = False

    def disconnect(self):
        self.interface.netClient.disconnect()
        if self.gameViewer.timerBar is not None:
            self.gameViewer.timerBar.kill()
            self.gameViewer.timerBar = None
        try:
            self.gameViewer.closeChat()
        except MultiWindowException:
            pass

    def replayDisconnect(self, sender):
        self.interface.server.shutdown()
        self.interface.server = None

    def gameOver(self, winningTeam):
        self.gameOverScreen = GameOverInterface(self.app, self, winningTeam)
        self.elements.append(self.gameOverScreen)
        try:
            self.elements.remove(self.menuHotkey)
        except:
            pass

    def reDraw(self):
        # TODO: This is redrawing every time there's a tag.
        # Could optimise that a bit to only redraw if the screen contains
        # one of its mapblocks.
        self.gameViewer.viewManager.reDraw()

    def processEvent(self, event):
        try:
            return super(GameInterface, self).processEvent(event)
        except MenuError, err:
            self.detailsInterface.newMessage(err.value, colours.errorMessageColour)
            self.detailsInterface.endInput()
            return None

class DetailsInterface(framework.CompoundElement):
    '''Interface containing all the overlays onto the screen:
    chat messages, player lists, gauges, stars, transaction requests, etc.'''
    def __init__(self, app, gameInterface):
        super(DetailsInterface, self).__init__(app)
        world = gameInterface.world
        self.gameInterface = gameInterface
        gameInterface.interface.netClient.setDetailsInterface(self)

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

        menuloc = Location(FullScreenAttachedPoint((0,0), 'bottomleft'), 'bottomleft')
        self.menuManager = mainMenu.MainMenu(self.app, menuloc, self, self.gameInterface.keyMapping)
        self.elements = [self.currentMessages, self.currentChats,
                         self.starGroup]

    def gameOver(self, winningTeam):
        self.gameInterface.gameOver(winningTeam)

    def setPlayer(self, player):
        self.player = player
        if self.menuManager not in self.elements:
            self.elements.append(self.menuManager)

    def doAction(self, action):
        '''
        Activated by hotkey or menu.
        action corresponds to the action name in the keyMapping.
        '''
        if action == 'leaderboard':
            self.showPlayerDetails()
            self.menuManager.manager.reset()
        elif action == 'zone progress':
            self.showZoneProgress()
            self.menuManager.manager.reset()
        elif action == 'timer':
            self.showTimer()
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
            self.player.requestRespawn()
        elif action == 'turret':
            self.player.requestUpgrade(Turret, self.getStars)
            self.menuManager.manager.reset()
        elif action == 'shield':
            self.player.requestUpgrade(Shield, self.getStars)
            self.menuManager.manager.reset()
        elif action == 'minimap disruption':
            self.player.requestUpgrade(MinimapDisruption, self.getStars)
            self.menuManager.manager.reset()
        elif action == 'phase shift':
            self.player.requestUpgrade(PhaseShift, self.getStars)
            self.menuManager.manager.reset()
        elif action == 'grenade':
            self.player.requestUpgrade(Grenade, self.getStars)
            self.menuManager.manager.reset()
        elif action == 'use upgrade':
            self.player.requestUse()
            self.menuManager.manager.reset()
        elif action == 'add stars':
            self.player.addStars(self.getStars)
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
        if not (self.player and transaction.purchasingTeam == self.player.team):
            return


        self.transactionGUI = TransactionGUI(self.app, Location(FullScreenAttachedPoint(ScaledSize(200,0), 'topleft'), 'topleft'), transaction, self.player)
        self.elements.append(self.transactionGUI)

        def deleteTransGUI(transactionGUI):
            '''Removes the TransactionGUI object from the screen'''
            # This check is necessary in case another one was created
            # while one was still up
            if transactionGUI == self.transactionGUI:
                if transactionGUI in self.elements:
                    self.elements.remove(transactionGUI)
                else:
                    print 'SOMEWHAT BAD: transactionGUI not in elements'
                self.transactionGUI = None

        def transactionChanged(sender, state):
            assert transaction == sender
            if state in (transactionModule.TransactionState.Abandoned, transactionModule.TransactionState.Completed):
                self.newMessage("%s's Transaction %s" % (repr(transaction.purchasingTeam), transactionModule.TransactionStateText[state]), colours.transactionMessageColour)
                reactor.callLater(3, deleteTransGUI, self.transactionGUI)

        # Set up a message to display to the screen when someone adds star(s)
        fAddStarsMessage = lambda sender, player, stars: self.newMessage('%s added %d star%s' % (player.nick, stars, ('s', '')[stars == 1]), colours.transactionMessageColour)

        self.newMessage('%s purchasing %s' % (transaction.purchasingPlayer.nick, upgradeNames[transaction.upgrade]), colours.transactionMessageColour)
                                                                         
        transaction.onNumStarsChanged.addListener(fAddStarsMessage)
        transaction.onStateChanged.addListener(transactionChanged)

    def newMessage(self, text, colour = colours.grey):
        self.currentMessages.newMessage(text, colour)
        self.allMessages.append((text))

    def newChat(self, text, sender, private):
        if sender == self.player:
            # Don't bother receiving messages from myself.
            return
        
        nick = sender.nick
        if not private:
            # Message for everyone
            extra = ': '
            self.allMessages.append((nick, text))
            
        elif isinstance(private, Player) and \
             self.player and self.player == private:
            # Destined for the one player
            extra = ' (private): '
            self.allMessages.append((nick, '#P# ' + text))
            
        elif isinstance(private, Team) and \
             self.player and self.player.team == private:
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
             player.team.currentTransaction.purchasingPlayer == player:
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
        if self.player and player == self.player:
            if self.upgradeGauge is not None:
                # Remove the existing one.
                print 'Stray upgradeGauge!'
                self.elements.remove(self.upgradeGauge)
            self.upgradeGauge = UpgradeGauge(self.app, Area(FullScreenAttachedPoint(ScaledSize(0,-20), 'midbottom'), ScaledSize(100,30), 'midbottom'), player)
            self.elements.append(self.upgradeGauge)

    def upgradeDestroyed(self, player):
        if self.player is not None and player == self.player and self.upgradeGauge is not None:
            self.elements.remove(self.upgradeGauge)
            self.upgradeGauge = None

    def turretStarted(self, player):
        if self.player and player == self.player:
            self.turretGauge = TurretGauge(self.app, Area(FullScreenAttachedPoint(ScaledSize(0,-60), 'midbottom'), ScaledSize(100,30), 'midbottom'), player)
            self.elements.append(self.turretGauge)

    def turretEnded(self, player):
        if self.player and player == self.player:
            self.elements.remove(self.turretGauge)
            self.turretGauge = None

    def playerDied(self, player):
        if self.player and player == self.player:
            self.respawnGauge = RespawnGauge(self.app, Area(FullScreenAttachedPoint(ScaledSize(0,-20), 'midbottom'), ScaledSize(100,30), 'midbottom'), player)
            self.elements.append(self.respawnGauge)

    def playerRespawned(self, player):
        if self.player and player == self.player and self.respawnGauge:
            self.elements.remove(self.respawnGauge)
            self.respawnGauge = None

    def becomeCaptain(self):
        if self.player:
            self.gameInterface.interface.netClient.setAsCaptain(self.player)

    def teamReady(self):
        if self.player:
            self.gameInterface.interface.netClient.teamReady(self.player)

    def showPlayerDetails(self):
        self.gameInterface.gameViewer.toggleLeaderBoard()

    def showZoneProgress(self):
        self.gameInterface.gameViewer.toggleZoneProgress()

    def showTimer(self):
        self.gameInterface.gameViewer.toggleTimer()

            
        
class PlayerInterface(framework.Element):
    '''Interface for controlling a player.'''

    # The virtual keys we care about.
    state_vkeys = frozenset(['left', 'right', 'jump', 'down'])

    def __init__(self, app, gameInterface, player):
        super(PlayerInterface, self).__init__(app)
        
        world = gameInterface.world
        self.gameInterface = gameInterface
        self.keyMapping = gameInterface.keyMapping

        self.receiving = True
        
        self.world = world
        self.player = player
        rect = pygame.Rect((0,0), self.app.screenManager.scaledSize)

        # Make sure the viewer is focusing on this player.
        self.gameInterface.gameViewer.setTarget(player)


    def tick(self, deltaT):
        pos = pygame.mouse.get_pos()
        self.updatePlayerViewAngle(pos)
        
    def updatePlayerViewAngle(self, pos):
        '''Updates the viewing angle of the player based on the mouse pointer
        being at the position pos. This gets its own method because it needs
        to happen as the result of a mouse motion and of the viewManager
        scrolling the screen.'''
        
        # Angle is measured clockwise from vertical.
        if not self.player.rect.collidepoint(pos):
            dx = pos[0]-self.player.rect.center[0]
            dy = pos[1]-self.player.rect.center[1]
            theta = atan2(dx, -dy)
            dist = (dx ** 2 + dy ** 2) ** 0.5
            self.player.lookAt(theta, dist)

    def stopThePlayer(self):
        self.player.setToNoState()

    def processEvent(self, event):
        '''Event processing works in the following way:
        1. If there is a prompt on screen, the prompt will either use the
        event, or pass it on.
        2. If passed on, the event will be sent back to the main class, for it
        to process whether player movement uses this event. If it doesn't use
        the event, it will pass it back.
        3. If so, the hotkey manager will see if the event means anything to it.
        If not, that's the end, the event is ignored.'''
        
        # Handle events specific to in-game.
        if self.player:
            if event.type == pygame.KEYDOWN:
                try:
                    stateKey = self.keyMapping[event.key]
                except KeyError:
                    return event

                if stateKey not in self.state_vkeys:
                    return event

                self.player.updateState(stateKey, True)
            elif event.type == pygame.KEYUP:
                try:
                    stateKey = self.keyMapping[event.key]
                except KeyError:
                    return event

                if stateKey not in self.state_vkeys:
                    return event

                self.player.updateState(stateKey, False)
            elif event.type == pygame.MOUSEMOTION:
                # FIXME: The following line generates glitches.
                # self.updatePlayerViewAngle(event.pos)
                pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Fire a shot.
                self.player.fireShot()
            else:
                return event

class ViewControlInterface(framework.Element):
    '''Interface for controlling a the replay view.'''

    # The virtual keys we care about.
    state_vkeys = frozenset(['left', 'right', 'jump', 'down'])

    def __init__(self, app, gameInterface):
        super(ViewControlInterface, self).__init__(app)
        
        world = gameInterface.world
        self.gameInterface = gameInterface
        self.keyMapping = gameInterface.keyMapping

        self.world = world
        self._state = dict([(k, False) for k in self.state_vkeys])

        self.vx = 0
        self.vy = 0

    def updateState(self, state, enabled):
        self._state[state] = enabled
        if self._state['left'] and not self._state['right']:
            self.vx = -1000
        elif self._state['right'] and not self._state['left']:
            self.vx = 1000
        else:
            self.vx = 0

        if self._state['jump'] and not self._state['down']:
            self.vy = -1000
        elif self._state['down'] and not self._state['jump']:
            self.vy = 1000
        else:
            self.vy = 0

    def tick(self, deltaT):
        if self.vx != 0 or self.vy != 0:
            x, y = self.gameInterface.gameViewer.viewManager.getTargetPoint()
            x += self.vx * deltaT
            y += self.vy * deltaT
            self.gameInterface.gameViewer.setTarget((x, y))

    def processEvent(self, event):
        '''Event processing works in the following way:
        1. If there is a prompt on screen, the prompt will either use the
        event, or pass it on.
        2. If passed on, the event will be sent back to the main class, for it
        to process whether player movement uses this event. If it doesn't use
        the event, it will pass it back.
        3. If so, the hotkey manager will see if the event means anything to it.
        If not, that's the end, the event is ignored.'''
        
        # Handle events specific to in-game.
        if event.type == pygame.KEYDOWN:
            try:
                stateKey = self.keyMapping[event.key]
            except KeyError:
                return event

            if stateKey not in self.state_vkeys:
                return event

            self.updateState(stateKey, True)
        elif event.type == pygame.KEYUP:
            try:
                stateKey = self.keyMapping[event.key]
            except KeyError:
                return event

            if stateKey not in self.state_vkeys:
                return event

            self.updateState(stateKey, False)
        else:
            return event


            
class GaugeBase(framework.Element):
    '''Represents a graphical gauge to show the overheatedness of a turret'''
    def __init__(self, app, area):
        super(GaugeBase, self).__init__(app)
        self.area = area

    def draw(self, surface):
        rect = self.area.getRect(self.app)
        pos = rect.topleft
        amount = int(self.getRatio() * rect.width)

        backColour = self.getBackColour()
        if backColour != None:
            backRect = pygame.rect.Rect(pos[0]+amount, pos[1],
                                        rect.width - amount + 1, rect.height)
            surface.fill(backColour, backRect)
            
        if amount > 0:
            insideRect = pygame.rect.Rect(pos, (amount, rect.height))
            surface.fill(self.getForeColour(), insideRect)

        # Draw the border on top
        pygame.draw.rect(surface, colours.gaugeBorder, rect, 2)            


    # Return a number as a proportion (0..1) of how complete
    # this box is. To be implemented in subclasses
    def getRatio(self):
        raise NotImplementedException

    # Return the foreground colour that this gauge should be.
    # To be implemented in subclasses
    def getForeColour(self):
        raise NotImplementedException

    # Return the background colour that this gauge should be.
    # None = blank
    # To be implemented in subclasses
    def getBackColour(self):
        return None


class RespawnGauge(GaugeBase):
    '''Represents a graphical gauge to show how close to respawning a player
    is.'''
    def __init__(self, app, area, player):
        super(RespawnGauge, self).__init__(app, area)
        self.player = player

    def getRatio(self):
        return min(self.player.respawnGauge / self.player.respawnTotal, 1)

    def getForeColour(self):
        return colours.gaugeRespawnFore

    def getBackColour(self):
        if self.getRatio() <= 0:
            return colours.gaugeRespawnReady
        else:
            return colours.gaugeRespawnBack

        
class TurretGauge(GaugeBase):
    '''Represents a graphical gauge to show the overheatedness of a turret'''
    def __init__(self, app, area, player):
        self.player = player
        super(TurretGauge, self).__init__(app, area)

    def getRatio(self):
        return min(1, self.player.turretHeat / self.player.turretHeatCapacity)

    def getForeColour(self):
        if self.player.turretOverHeated:
            return colours.gaugeTurretHeated
        elif self.getRatio() > 0.5:
            return colours.gaugeTurretWarn
        else:
            return colours.gaugeTurretFine

class UpgradeGauge(GaugeBase):
    '''Represents a graphical gauge to show how much time a player has left
    to use their upgrade.'''
    def __init__(self, app, area, player):
        super(UpgradeGauge, self).__init__(app, area)
        self.player = player

    def getRatio(self):
        return min(self.player.upgradeGauge / self.player.upgradeTotal, 1)

    def getForeColour(self):
        return colours.gaugeUpgradeFore

    def getBackColour(self):
        return colours.gaugeUpgradeBack


class StarGroup(framework.CompoundElement):
    def __init__(self, app):
        super(StarGroup, self).__init__(app)

    def _remove(self, starAn):
        self.elements.remove(starAn)
    def star(self, pos):
        self.elements.append(StarAnimation(self.app, pos, self))
        
class StarAnimation(elements.PictureElement):
    def __init__(self, app, pos, starGroup):
        global _starPic
        try:
            pic = _starPic
        except NameError:
            pic = _starPic = loadSprite('star.png')
            pic.set_colorkey((255,255,255))

        super(StarAnimation, self).__init__(app, pic, pos)

        self.pos = pos
        self.count = 0
        self.starGroup = starGroup
        reactor.callLater(0.1, self.advance)

    def advance(self):
        self.pos = (self.pos[0], self.pos[1] - 10)
        self.setPos(self.pos)
        self.count += 1
        if self.count < 5:
            reactor.callLater(0.1, self.advance)
        else:
            self.starGroup._remove(self)

class InGameMenu(framework.CompoundElement):
    def __init__(self, app, gameInterface):
        super(InGameMenu, self).__init__(app)
        self.interface = gameInterface
        self.titleFont = titleFont = self.app.screenManager.fonts.titleFont
        self.font = self.app.screenManager.fonts.menuFont

    '''
    onClick can be expected to be a function with no parameters
    '''
    def button(self, height, text, hotkey, onClick=None):
        item = elements.TextButton(self.app, ScaledLocation(512, height, 'center'),
                                   text,
                                   self.font,
                                   colours.inGameButtonColour, colours.white,
                                   hotkey)
        if onClick:
            item.onClick.addListener(lambda sender: onClick())
        return item


class ReplayMenu(InGameMenu):
    def __init__(self, app, gameInterface, world):
        super(ReplayMenu, self).__init__(app, gameInterface)
        self.elements = []
        self.gameInterface = gameInterface

        item = elements.TextButton(app, ScaledLocation(0, 768, 'bottomleft'),
                                   'End Replay',
                                   self.font,
                                   colours.inGameButtonColour, colours.white)
        item.onClick.addListener(self.interface.replayDisconnect)
        self.elements.append(item)

class GameMenu(InGameMenu):
    '''This is not actually a menu any more, but rather a controller used only
    when joining the game.'''
    
    def __init__(self, app, gameInterface, world):
        super(GameMenu, self).__init__(app, gameInterface)
        self.joined = False
        self.joiningInfo = None
        self.gameInterface = gameInterface
        
        self.joinGameDialog = JoinGameDialog(self.app, self, world)
        self.joinGameDialog.onClose.addListener(self._joinDlgClose)

        self.joiningScreen = JoiningDialog(self.app, self)

        self.joinGameDialog.Show()

    def _joinDlgClose(self):
        if self.joinGameDialog.result != DialogResult.OK:
            self.interface.disconnect()
        else:
            nick = self.joinGameDialog.nickBox.value.strip()
            nick = nick[:maxNameLength]
            writeName(nick)

            team = self.joinGameDialog.selectedTeam
            self.joiningInfo = nick, team
            self.interface.interface.netClient.join(
                    nick,
                    team
            ).addCallback(self.joinComplete).addErrback(self.joinErrback)
            self.joiningScreen.show(nick)
        
    def showMessage(self, text):
        self.joinGameDialog.cantJoinYet.setText(text)

    def cancelJoin(self, sender):
        self.interface.interface.netClient.cancelJoin(*self.joiningInfo)
        self.joiningScreen.Close()
        self.joinGameDialog.Show()

    def joinComplete(self, result):
        if result[0] == 'success':
            # Join was successful.
            player = result[1]
            self.joined = True
            self.interface.joined(player)
            self.joiningScreen.Close()
            return

        self.joiningScreen.Close()
        self.joinGameDialog.Show()

        if result[0] == 'noserver':
            # Not yet connected.
            print 'Join failed: not yet connected to server!'
            self.showMessage('Network connection error.')
        elif result[0] == 'full':
            # Team is full.
            self.showMessage('That team is full!')
        elif result[0] == 'over':
            # The game is over.
            self.showMessage('The game is over!')
        elif result[0] == 'wait':
            # Need to wait a few seconds before rejoining.
            self.showMessage('You need to wait ' + result[1] + ' seconds before rejoining.')
        elif result[0] == 'error':
            # Python error.
            self.showMessage('Join failed: python error')
        elif result[0] == 'cancel':
            # Do nothing: join cancelled.
            print 'Join cancelled'
        else:
            # Unknown reason.
            self.showMessage('Join failed: ' + result[0])

    def joinErrback(self, error):
        'Errback for joining game.'
        # TODO: Produce some kind of traceback of the error.
        error.printTraceback()
        self.joinComplete(['There was an error'])
        
class JoinGameDialog(DialogBox):
    def __init__(self, app, gmInterface, world):
        super(JoinGameDialog, self).__init__(app, ScaledSize(512, 284), 'Join Game')
        self.gmInterface = gmInterface
        self.selectedTeam = None

        fonts = self.app.screenManager.fonts
        self.nickBox = prompt.InputBox(
            self.app,
            Area(DialogBoxAttachedPoint(self, ScaledSize(0, 70), 'midtop'), ScaledSize(200, 60), 'midtop'),
            '',
            font = fonts.menuFont
        )
        self.nickBox.onClick.addListener(self.setFocus)
        self.nickBox.onTab.addListener(lambda sender: self.clearFocus())
        name = getName()
        if name is not None:
            self.nickBox.setValue(name)

        self.cantJoinYet = elements.TextElement(
            self.app,
            '',
            fonts.ingameMenuFont,
            ScaledLocation(256, 145, 'center'),
            colours.cannotJoinColour
        )
        
        teamA = world.teams[0]
        teamB = world.teams[1]

        self.elements = [
            elements.TextElement(
                self.app,
                'Please enter your nick:',
                fonts.menuFont,
                Location(DialogBoxAttachedPoint(self, ScaledSize(0, 10), 'midtop'), 'midtop'),
                colours.black
            ),
            self.nickBox,
            self.cantJoinYet,
        
            elements.TextButton(
                self.app,
                Location(DialogBoxAttachedPoint(self, ScaledSize(-25, 150), 'midtop'), 'topright'),
                'Join %s' % (teamA,),
                fonts.menuFont,
                colours.team1msg,
                colours.white,
                onClick=lambda obj: self.joinTeam(teamA)
            ),
            elements.TextButton(
                self.app,
                Location(DialogBoxAttachedPoint(self, ScaledSize(25, 150), 'midtop'), 'topleft'),
                'Join %s' % (teamB,),
                fonts.menuFont,
                colours.team2msg,
                colours.white,
                onClick=lambda obj: self.joinTeam(teamB)
            ),

            elements.TextButton(
                self.app, 
                Location(DialogBoxAttachedPoint(self, ScaledSize(0, -10), 'midbottom'), 'midbottom'),
                'Cancel',
                fonts.menuFont,
                colours.inGameButtonColour,
                colours.white,
                onClick=self.cancel
            )
        ]
        self.setColours(colours.joinGameBorderColour, colours.joinGameTitleColour,
                colours.joinGameBackgroundColour)
        self.setFocus(self.nickBox)

    def joinTeam(self, team):
        self.selectedTeam = team
        self.cantJoinYet.setText('')

        nick = self.nickBox.value
        if nick == '' or nick.isspace():
            # Disallow all-whitespace nicks
            return

        self.result = DialogResult.OK
        self.Close()
        
    def cancel(self, sender):
        self.result = DialogResult.Cancel
        self.Close()

class JoiningDialog(DialogBox):
    def __init__(self, app, gameMenuInterface):
        super(JoiningDialog, self).__init__(app, ScaledSize(530, 180), 'Trosnoth')
        self.gmInterface = gameMenuInterface

        fonts = self.app.screenManager.fonts
        self.text = elements.TextElement(
            self.app,
            '',
            fonts.menuFont,
            Location(DialogBoxAttachedPoint(self, ScaledSize(0, 40), 'midtop'), 'midtop'),
            colour = colours.joiningColour
        )

        self.elements = [self.text,
            elements.TextButton(
                self.app, 
                Location(DialogBoxAttachedPoint(self, ScaledSize(0, -10), 'midbottom'), 'midbottom'),
                'Cancel',
                fonts.menuFont,
                colours.inGameButtonColour,
                colours.white,
                onClick=gameMenuInterface.cancelJoin
            )
        ]
        self.setColours(colours.joinGameBorderColour, colours.joinGameTitleColour,
                colours.joinGameBackgroundColour)

    def show(self, nick):
        self.text.setText('Joining as %s...' % (nick,))
        self.Show()

class ObserverInterface(framework.CompoundElement):
    def __init__(self, app, gameInterface):
        super(ObserverInterface, self).__init__(app)
        self.gameInterface = gameInterface
        self.keyMapping = gameInterface.keyMapping

    def processEvent(self, event):
        if event.type == pygame.KEYDOWN and \
                    self.keyMapping.get(event.key, None) == 'menu':
           self.gameInterface.showMenu()

class GameOverInterface(InGameMenu):
    def __init__(self, app, gmInterface, team):
        super(GameOverInterface, self).__init__(app, gmInterface)
        
        titleFont = self.app.screenManager.fonts.titleFont
        if team:
            winText = '%s has won' % (team,)
            winColour = team.chatColour
            creditsColour = team.sysMessageColour
        else:
            winText = 'Game is drawn'
            winColour = (128, 128, 128)
            creditsColour = colours.creditsColour

        gameWon = elements.TextElement(self.app, winText, titleFont,
                                       ScaledLocation(0, 0, 'topleft'),
                                       winColour)
        credits = CreditsScreen(self.app, creditsColour, gmInterface.disconnect, speed=50, loop=False, startOff=True)
        self.elements = [gameWon, credits]
