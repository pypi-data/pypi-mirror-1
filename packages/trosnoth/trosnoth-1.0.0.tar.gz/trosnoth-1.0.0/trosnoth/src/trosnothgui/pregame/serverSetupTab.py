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


# TODO: check we use all these imports
import sys
from socket import *

import pygame
from twisted.internet import protocol, reactor, task
from twisted.internet.error import CannotListenError
from twisted.internet.protocol import DatagramProtocol

import trosnoth.src.trosnothgui.defines as defines
import trosnoth.src.gui.framework.framework as framework
import trosnoth.src.gui.framework.prompt as prompt
from trosnoth.src.gui.framework.elements import PictureElement, TextElement, TextButton
from trosnoth.src.gui.framework.tab import Tab
from trosnoth.src.gui.framework.checkbox import CheckBox
from trosnoth.src.gui.framework.listbox import ListBox
from trosnoth.src.gui.framework.dialogbox import DialogBox, DialogResult, DialogBoxAttachedPoint
import trosnoth.data.startupMenu as startupMenu
from trosnoth.src.trosnothgui.pregame import colours
from trosnoth.src.gui.fonts.font import ScaledFont

from trosnoth.src.networkDefines import *

from trosnoth.src.gui.common import *

from trosnoth.src.trosnothgui.pregame.imageRadioButton import ImageRadioButton, RadioButtonGroup
from trosnoth.src.trosnothgui.pregame.promptImageRadioButton import PromptImageRadioButton

import trosnoth.data.startupMenu as startupMenu
from trosnoth.data import getPath


def localServerRunning():
    port = None

    # Try binding port 6789
    try:
        port = reactor.listenTCP(6789, TestFactory())
    except CannotListenError:
        pass

    # If it was successful, there is no server: stop listening
    if port:
        port.stopListening()
        return False
    else:
        return True

class TestProtocol(protocol.Protocol):
    pass
class TestFactory(protocol.ServerFactory):
    protocol = TestProtocol

class ServerSetupTab(Tab):
    def __init__(self, app, tabContainer, startupInterface):
        super(ServerSetupTab, self).__init__(app, "Start a Game")
        self.toCreate = ServerDoesntExistMenu(app, tabContainer, startupInterface, self)
        self.created = ServerAlreadyExistsMenu(app, tabContainer, startupInterface, self)
        self.tabContainer = tabContainer
        self.setAppropriateElements()

        # Refresh the elements list every now and then in case server has shut down.
        task.LoopingCall(self.setAppropriateElements).start(5, False)

    def setAppropriateElements(self):
        if localServerRunning():
            self.elements = [self.created]
            self.tabContainer.renameTab("Game Options", self)
        else:
            self.elements = [self.toCreate]
            self.tabContainer.renameTab("Start a Game", self)

    def setName(self, name):
        self.toCreate.setName(name)        

class ServerDoesntExistMenu(framework.TabFriendlyCompoundElement):
    def __init__(self, app, tabContainer, startupInterface, parent):
        super(ServerDoesntExistMenu, self).__init__(app)
        self.startupInterface = startupInterface
        self.tabContainer = tabContainer
        self.parent = parent

        self.serverName = ''
        self.mapHeight = ''
        self.halfMapWidth = ''
        self.maxPlayers = ''

        font = self.app.screenManager.fonts.bigMenuFont

        self.radio = RadioButtonGroup(app)

        imageSize = ScaledSize(200,120)
        imageSmall = SizedImage(getPath(startupMenu, 'small.png'), imageSize, (0,0,0))
        imageLong  = SizedImage(getPath(startupMenu, 'long.png'), imageSize, (0,0,0))
        imageLarge = SizedImage(getPath(startupMenu, 'large.png'), imageSize, (0,0,0))

        largeRadio = ImageRadioButton(app, "Standard", ScaledArea(85,370,200,150), imageLarge)
        largeRadio.value = (3,2)
        self.radio.add(largeRadio)

        smallRadio = ImageRadioButton(app, "Small", ScaledArea(305, 370,200,150), imageSmall)
        smallRadio.value = (1,1)
        self.radio.add(smallRadio)

        longRadio = ImageRadioButton(app, "Wide", ScaledArea(85,540,200,150), imageLong)
        longRadio.value = (5,1)
        self.radio.add(longRadio)

        customRadio = PromptImageRadioButton(app, "Custom", ScaledArea(305,540,200,150))
        self.radio.add(customRadio)

        self.radio.selected(largeRadio)
        self.radio.onSelectionChanged.addListener(self.setPlayerNumber)   


        self.text = [
                     TextElement(self.app, 'Game Name:', font,
                                 ScaledLocation(85, 220),
                                 colours.headingColour),
                     TextElement(self.app, 'Team Size:', font,
                                 ScaledLocation(600, 220),
                                 colours.headingColour),
                     TextElement(self.app, 'players per side', app.screenManager.fonts.smallNoteFont,
                                 ScaledLocation(720, 310),
                                 colours.headingColour),
                     TextElement(self.app, 'Time Limit:', font,
                                 ScaledLocation(600, 360), 
                                 colours.headingColour),
                     TextElement(self.app, 'minutes', app.screenManager.fonts.smallNoteFont,
                                 ScaledLocation(720, 450), 
                                 colours.headingColour),
                     ]

        self.invalidInputText = TextElement(self.app, '', self.app.screenManager.fonts.ampleMenuFont,
                                            ScaledLocation(50, 770, 'bottomleft'),
                                            colours.invalidDataColour)
        self.serverInput = prompt.InputBox(self.app, ScaledArea(85, 290, 420, 60),
                                      initValue = '',
                                      font = font)
        self.serverInput.onClick.addListener(self.setFocus)
        self.serverInput.onTab.addListener(self.tabNext)
        self.serverInput.onEnter.addListener(lambda sender: self.startServer())
        
        self.maxPlayersInput = prompt.InputBox(self.app, ScaledArea(600, 290, 100, 60),
                                           initValue = '16',
                                           font = font, maxLength = 3,
                                           validator = prompt.intValidator)
        self.maxPlayersInput.onClick.addListener(self.setFocus)
        self.maxPlayersInput.onTab.addListener(self.tabNext)
        self.maxPlayersInput.onEnter.addListener(lambda sender: self.startServer())

        self.gameDurationInput = prompt.InputBox(self.app, ScaledArea(600, 430, 100, 60),
                                           font = font, maxLength = 3,
                                           validator = prompt.intValidator)
        self.gameDurationInput.onClick.addListener(self.setFocus)
        self.gameDurationInput.onTab.addListener(self.tabNext)
        self.gameDurationInput.onEnter.addListener(lambda sender: self.startServer())

        self.noLimitBox = CheckBox(self.app, ScaledLocation(830, 385),
                                           text = 'No Limit',
                                           font = app.screenManager.fonts.smallNoteFont,
                                           colour = colours.mainMenuColour,
                                           initValue = True,
                                           style='circle')
        self.noLimitBox.onValueChanged.addListener(lambda sender: self.enableGameDuration(not sender.value))

        self.recordReplayBox = CheckBox(self.app, ScaledLocation(600, 520),
                                           text = 'Save Replay',
                                           font = app.screenManager.fonts.smallNoteFont,
                                           colour = colours.mainMenuColour,
                                           initValue = True,
                                           style='circle')

        self.startButton = TextButton(self.app, ScaledLocation(600, 580), 'start', app.screenManager.fonts.hugeMenuFont, colours.startButton, colours.white)
        self.startButton.onClick.addListener(lambda sender: self.startServer())
        
        self.input = [self.serverInput, self.maxPlayersInput, self.gameDurationInput]
        self.enableGameDuration(False)

        self.elements = self.text + self.input + \
                        [self.recordReplayBox,
                         self.noLimitBox,
                         self.invalidInputText,
                         self.startButton,
                         self.radio
                        ]
        self.setFocus(self.serverInput)
        self.lastSelection = -1
        self.setPlayerNumber(0)   

    def setPlayerNumber(self, index):
        playerSizes = [8, 3, 5]
        chosenNum = int(self.maxPlayersInput.getValue())
        if (self.lastSelection == -1 or self.lastSelection == 3 or playerSizes[self.lastSelection] == chosenNum) and index != 3:
            self.maxPlayersInput.setValue(str(playerSizes[index]))
        if index != 3 and index != -1:
            self.lastSelection = index
        

    def setName(self, name):
        #if self.serverInput.getValue() == "":
            self.serverInput.setValue("%s's game" % (name,))

    def setTabOrder(self):
        if self._enableGameDuration:
            self.tabOrder = [self.serverInput, self.maxPlayersInput, self.gameDurationInput]
        else:
            self.tabOrder = [self.serverInput, self.maxPlayersInput]

    def setFocus(self, object):
        if (not self._enableGameDuration) and object == self.gameDurationInput:
            self.noLimitBox.setValue(False)
        hadFocus = self.gameDurationInput.hasFocus
        super(ServerDoesntExistMenu, self).setFocus(object)
        # If the game duration box had and now does not have focus
        if hadFocus and not self.gameDurationInput.hasFocus and self.gameDurationInput.value == "":
            self.enableGameDuration(False)
            self.noLimitBox.setValue(True)

    def enableGameDuration(self, val):
        self._enableGameDuration = val
        if val:
            self.gameDurationInput.setBackColour(colours.white)
            self.setFocus(self.gameDurationInput)
        else:
            self.gameDurationInput.setBackColour(colours.disabled)
            if self.gameDurationInput.hasFocus:
                self.setFocus(self.maxPlayersInput)
        self.setTabOrder()
            

    def startServer(self):
        values = self.getValues()
        if values:
            self.incorrectInput("")
            self.startupInterface.startServer(*values)
            self.parent.setAppropriateElements()
            # Select the LAN tab
            self.tabContainer._tabSelected(0)
            # Set the server name back to nothing in case
            # the user changes their player name in-game -
            # it will be reset hereafter.

    def setBackColours(self):
        if self._enableGameDuration:
            self.gameDurationInput.setBackColour(colours.white)
        else:
            self.gameDurationInput.setBackColour(colours.disabled)
        self.maxPlayersInput.setBackColour(colours.white)
        self.serverInput.setBackColour(colours.white)

    def getValues(self):
        '''Returns the inputted values in the order:
        1. halfMapWidth
        2. mapHeight
        3. maxPlayers
        4. Game Duration
        5. Record Replay?'''
        # TODO: move these to a central location for server and interface to read
        numPlayers = (2, 128)

        self.setBackColours()

        invalid = False
        
        height = width = maxPlayers = duration = name = None
        if self.serverInput.value == '':     # TODO: ensure there isn't one of that name already
            if not invalid:
                invalid = True
                self.incorrectInput("Please give this game a name")
            self.serverInput.setBackColour(colours.invalidDataColour)
        else:
            name = self.serverInput.value
    
        if numPlayers[0] <= self.getInt(self.maxPlayersInput.value) <= numPlayers[1]:
            maxPlayers = self.getInt(self.maxPlayersInput.value)
        else:
            if not invalid:
                self.incorrectInput("Must have between %d and %d players per team" %
                                    (numPlayers[0], numPlayers[1]))
                invalid = True
            self.maxPlayersInput.setBackColour(colours.invalidDataColour)
            

        if self.noLimitBox.value:
            duration = 0
        else:
            duration = self.getInt(self.gameDurationInput.value)
            if duration == 0:
                self.gameDurationInput.setBackColour(colours.invalidDataColour)
                if not invalid:
                    invalid = True
                    self.incorrectInput("Please set a duration for this game") 
                
        radioChoice = self.radio.getSelectedValue()
        if radioChoice is None:
            if not invalid:
                invalid = True
                self.incorrectInput("Please choose a map size")

        if invalid:
            return None

                    
        recordReplay = self.recordReplayBox.value
        width, height = radioChoice

        
        return [name, width, height, maxPlayers, duration, recordReplay]

    def getInt(self, value):
        if value == '':
            return 0
        return int(value)
        

    def incorrectInput(self, string):
        self.invalidInputText.setText(string)

    def draw(self, surface):
        super(ServerDoesntExistMenu, self).draw(surface)
        rect = self.tabContainer._getTabRect()
        verLineX = rect.left + (rect.width * 0.545)
        pygame.draw.line(surface, colours.tabContainerColour, (verLineX, rect.top), (verLineX, rect.bottom), self.tabContainer._getBorderWidth())
        horLineY = rect.top + (rect.height * 0.72)
        pygame.draw.line(surface, colours.tabContainerColour, (verLineX, horLineY), (rect.right, horLineY), self.tabContainer._getBorderWidth())


class ServerAlreadyExistsMenu(framework.TabFriendlyCompoundElement):
    def __init__(self, app, tabContainer, startupInterface, parent):
        super(ServerAlreadyExistsMenu, self).__init__(app)
        self.startupInterface = startupInterface
        self.tabContainer = tabContainer
        self.parent = parent

        self.blueTeamName = 'Blue'
        self.redTeamName = 'Red'
        self.gameMode = 'Normal'

        self.inputsEdited = False
        self.resetCountdownDefault = 30
        self.resetCountdown = self.resetCountdownDefault
        self.resetTimer = task.LoopingCall(self.resetCountdownFunction)

        self.delayedCall = None

        font = self.app.screenManager.fonts.bigMenuFont

        # Static text
        self.staticText = [TextElement(self.app, 'Game Status:', font,
                                 ScaledLocation(70, 240),
                                 colours.headingColour),
                           TextElement(self.app, 'Team Names:', font,
                                 ScaledLocation(70, 320),
                                 colours.headingColour),
                           TextElement(self.app, 'Game Mode:', font,
                                 ScaledLocation(70, 400), 
                                 colours.headingColour)]

        # Dynamic text
        self.assistanceText = TextElement(self.app, '', font,
                                            ScaledLocation(70, 480),
                                            colours.invalidDataColour)
        self.gameStatusText = TextElement(self.app, 'Not yet started', font,
                                          ScaledLocation(350, 240),
                                          colours.inactive)

        self.dynamicText = [self.assistanceText, self.gameStatusText]

        # Input boxes
        self.blueTeamInput = prompt.InputBox(self.app, ScaledArea(350, 320, 270, 60),
                                             initValue = self.blueTeamName,
                                             font = font, colour = colours.blueTeam,
                                             maxLength = 10)
        self.blueTeamInput.onClick.addListener(self.setFocus)
        self.blueTeamInput.onEdit.addListener(lambda sender: self.inputEdit())
        self.blueTeamInput.onTab.addListener(self.tabNext)
        self.blueTeamInput.onEnter.addListener(lambda sender: self.saveSettings())

        self.redTeamInput = prompt.InputBox(self.app, ScaledArea(655, 320, 270, 60),
                                            initValue = self.redTeamName,
                                            font = font, colour = colours.redTeam,
                                            maxLength = 10)
        self.redTeamInput.onClick.addListener(self.setFocus)
        self.redTeamInput.onEdit.addListener(lambda sender: self.inputEdit())
        self.redTeamInput.onTab.addListener(self.tabNext)
        self.redTeamInput.onEnter.addListener(lambda sender: self.saveSettings())

        self.gameModeInput = prompt.InputBox(self.app, ScaledArea(350, 400, 575, 60),
                                             initValue = self.gameMode,
                                             font = font, colour = colours.white,
                                             maxLength = 20)
        self.gameModeInput.onClick.addListener(self.setFocus)
        self.gameModeInput.onEdit.addListener(lambda sender: self.inputEdit())
        self.gameModeInput.onTab.addListener(self.tabNext)
        self.gameModeInput.onEnter.addListener(lambda sender: self.saveSettings())

        self.input = self.tabOrder = [self.blueTeamInput, self.redTeamInput, self.gameModeInput]

        # Text buttons
        self.shutdownButton = TextButton(self.app, ScaledLocation(410, 620, 'center'),
                                         'SHUT DOWN SERVER',
                                         app.screenManager.fonts.hugeMenuFont,
                                         colours.redTeam, colours.white)
        self.shutdownButton.onClick.addListener(lambda sender: self.shutdownServer())
        self.shutdownWarning = False

        self.startGameButton = TextButton(self.app, ScaledLocation(925, 240, 'topright'),
                                          'force begin', font,
                                          colours.mainMenuColour, colours.white)
        self.startGameButton.onClick.addListener(lambda sender: self.startGame())

        self.saveButton = TextButton(self.app, ScaledLocation(925, 480, 'topright'),
                                     'save settings', font,
                                     colours.mainMenuColour, colours.white)
        self.saveButton.onClick.addListener(lambda sender: self.saveSettings())

        self.buttons = [self.shutdownButton, self.startGameButton, self.saveButton]

        # By your powers combined, I am Captain Planet!
        self.elements = self.staticText + self.dynamicText + self.input + self.buttons

        try:
            # Initiate the StatusProtocol. Listen on default response port.
            self.statusProtocol = StatusProtocol(self, defaultServerAdminResponsePort)

            # Update the game status every second.
            self.updateStatusLoop = task.LoopingCall(self.updateStatus)
            self.updateStatusLoop.start(1.0, True)
        except CannotListenError:
            self.elements = self.staticText

            self.elements = [TextElement(app, "There is a game running on this computer,", app.screenManager.fonts.bigMenuFont,
                                         ScaledLocation(512, 290, 'center'), colours.noGamesColour),
                             TextElement(app, "however the Game Options are already open", app.screenManager.fonts.bigMenuFont,
                                         ScaledLocation(512, 350, 'center'), colours.noGamesColour),
                             TextElement(app, "in another copy of Trosnoth.", app.screenManager.fonts.bigMenuFont,
                                         ScaledLocation(512, 410, 'center'), colours.noGamesColour),
                             TextElement(app, "Please use the first Trosnoth you opened or", app.screenManager.fonts.bigMenuFont,
                                         ScaledLocation(512, 480, 'center'), colours.invalidDataColour),
                             TextElement(app, "close all copies of Trosnoth and try again.", app.screenManager.fonts.bigMenuFont,
                                         ScaledLocation(512, 540, 'center'), colours.invalidDataColour)]

       
    # This has the same effect as using the server admin tool,
    # except it is hardcoded to port 6790
    def sendCommand(self, command):
        s = socket(AF_INET, SOCK_DGRAM)
        n = s.sendto(command, ('127.0.0.1', defaultServerAdminPort))

    def updateStatus(self):
        self.sendCommand("GameStatus")

    def saveSettings(self):
        nameChange = False
        modeChange = False
        if self.blueTeamInput.getValue().strip() != self.blueTeamName:
            nameChange = True
            self.sendCommand('TeamName0=' + self.blueTeamInput.getValue().strip())
        if self.redTeamInput.getValue().strip() != self.redTeamName:
            nameChange = True
            self.sendCommand('TeamName1=' + self.redTeamInput.getValue().strip())
        if self.gameModeInput.getValue().strip() != self.gameMode:
            modeChange = True
            self.sendCommand('GameMode=' + self.gameModeInput.getValue().strip())
        if not modeChange:
            if nameChange:
                self.stopCountdown('Settings have been saved.')
        else:
            self.stopCountdown('Waiting for response...')
        self.assistanceText.setColour(colours.startButton)

    def startGame(self):
        self.sendCommand('StartGame')
        
    def shutdownServer(self):
        self.shutdownConfirmationBox = ShutdownDialog(self.app)
        self.shutdownConfirmationBox.onClose.addListener(self._shutdownDlgClose)
        self.shutdownConfirmationBox.Show()

    def _shutdownDlgClose(self):
        if self.shutdownConfirmationBox.result == DialogResult.OK:
            self.sendCommand('Shutdown')
            reactor.callLater(0.1, self.parent.setAppropriateElements)

    # The following three functions are all related: if a user edits the team names or gamde mode
    # but doesn't save them, they will get a certain amount of time before the inputs are reset to
    # those obtained from the server.
    
    def inputEdit(self):
        if self.blueTeamInput.getValue().strip() != self.blueTeamName or \
            self.redTeamInput.getValue().strip() != self.redTeamName or \
            self.gameModeInput.getValue().strip() != self.gameMode:
            if not self.inputsEdited:
                self.inputsEdited = True
                self.resetTimer.start(1.0, False)
        else:
            self.stopCountdown('')

    def resetCountdownFunction(self):
        self.resetCountdown -= 1
        if self.resetCountdown <= 0:
            self.stopCountdown("Settings reset due to inactivity")
            self.populateInputs()
            self.delayedErase(self.assistanceText)
        elif self.resetCountdown <= 5 or self.resetCountdown == 10 or self.resetCountdown == 20:
            self.assistanceText.setText("Settings will reset in %d seconds" % self.resetCountdown)
            self.assistanceText.setColour(colours.startButton)

    def stopCountdown(self, message):
        self.assistanceText.setText(message)
        self.assistanceText.setColour(colours.invalidDataColour)
        # There's a chance that the timer might never have been started.
        try:
            self.resetTimer.stop()
        except AssertionError:
            pass
        self.inputsEdited = False
        self.resetCountdown = self.resetCountdownDefault

    def populateInputs(self):
        self.blueTeamInput.setValue(self.blueTeamName)
        self.redTeamInput.setValue(self.redTeamName)
        self.gameModeInput.setValue(self.gameMode)

    def delayedErase(self, element, time = 3):
        self.delayedCall = reactor.callLater(time, self.clearText, element)

    def clearText(self, element):
        element.setText('')

class ShutdownDialog(DialogBox):
    '''Defines the elements and layout thereof of the server shutdown confirmation dialog box.'''

    def __init__(self, app):
        super(ShutdownDialog, self).__init__(app, ScaledSize(450, 340), "Server Shutdown")

        # Warning message
        text = [TextElement(app, "Are you sure you want", app.screenManager.fonts.mediumMenuFont,
                                Location(DialogBoxAttachedPoint(self, ScaledSize(0, 10), 'midtop'), 'midtop'), colours.invalidDataColour),
                TextElement(app, "to shutdown the server?", app.screenManager.fonts.mediumMenuFont,
                                Location(DialogBoxAttachedPoint(self, ScaledSize(0, 55), 'midtop'), 'midtop'), colours.invalidDataColour),
                TextElement(app, "Doing so will immediately", app.screenManager.fonts.mediumMenuFont,
                                Location(DialogBoxAttachedPoint(self, ScaledSize(0,130), 'midtop'), 'midtop'), colours.invalidDataColour),
                TextElement(app, "end the game and", app.screenManager.fonts.mediumMenuFont,
                                Location(DialogBoxAttachedPoint(self, ScaledSize(0,175), 'midtop'), 'midtop'), colours.invalidDataColour),
                TextElement(app, "disconnect all users!", app.screenManager.fonts.mediumMenuFont,
                                Location(DialogBoxAttachedPoint(self, ScaledSize(0,220), 'midtop'), 'midtop'), colours.invalidDataColour)]
        
        font = ScaledFont("KLEPTOCR.TTF", 50)

        # OK Button
        okButton = TextButton(app,  Location(DialogBoxAttachedPoint(self, ScaledSize(-100,280), 'midtop'), 'midtop'), "Confirm", font, colours.dialogButtonColour, colours.radioMouseover)
        okButton.onClick.addListener(lambda sender: self.ok())

        # Cancel Button
        cancelButton = TextButton(app,  Location(DialogBoxAttachedPoint(self, ScaledSize(100,280), 'midtop'), 'midtop'), "Cancel", font, colours.dialogButtonColour, colours.radioMouseover)
        cancelButton.onClick.addListener(lambda sender: self.cancel())

        # Add elements to screen
        self.elements = text + [okButton, cancelButton]
        self.setColours(colours.redTeam, colours.dialogBoxTextColour, colours.dialogBoxTextColour)

    def ok(self):
        self.result = DialogResult.OK
        self.Close()
        
    def cancel(self):
        self.result = DialogResult.Cancel
        self.Close()

class StatusProtocol(DatagramProtocol):
    '''This protocol is used to receive game status information from the server.'''

    def __init__(self, menu, port):
        self.menu = menu

        # Ask the system for a UDP port.
        self.port = reactor.listenUDP(port, self)

    def datagramReceived(self, datagram, address):

        status = self.menu.gameStatusText
        
        if address[0] != '127.0.0.1':
            return

        if datagram.startswith('GameStatus:'):
            # GameStatus:I7.7
            currentGameState = datagram[11]
            if currentGameState != 'P':
                self.menu.startGameButton.setText('')

            if currentGameState == 'P':
                status.setText('Not yet started')
                status.setColour(colours.inactive)
                self.menu.startGameButton.setText('force begin')
            elif currentGameState == 'I':
                decimalPos = datagram.find(".")
                blueScore = int(datagram[12:decimalPos])
                redScore = int(datagram[decimalPos+1:])

                if blueScore > redScore:
                    status.setText('In progress (%d-%d to %s)' %
                            (blueScore, redScore, self.menu.blueTeamName))
                    status.setColour(colours.blueTeam)
                elif redScore > blueScore:
                    status.setText('In progress (%d-%d to %s)' %
                            (redScore, blueScore, self.menu.redTeamName))
                    status.setColour(colours.redTeam)
                else:
                    status.setText('In progress (%d-%d tie)' %
                            (redScore, blueScore))
                    status.setColour(colours.bothTeams)
            elif currentGameState in ('D', 'B', 'R'):
                if currentGameState == 'B':
                    status.setText('Game over - %s wins!' % self.menu.blueTeamName)
                    status.setColour(colours.blueTeam)
                elif currentGameState == 'R':
                    status.setText('Game over - %s wins!' % self.menu.redTeamName)
                    status.setColour(colours.redTeam)
                else:
                    status.setText('Game over - it was a draw!')
                    status.setColour(colours.bothTeams)
                self.menu.saveButton.setText('')
            else:
                self.menu.gameStatusText.setText('Unknown')
                self.menu.gameStatusText.setColour(colours.inactive)

        if datagram.startswith('TeamNames:'):
            # TeamNames:Team 1    Team 2    GameMode
            #           12345678901234567890...
            self.menu.blueTeamName = datagram[10:20].strip()
            self.menu.redTeamName = datagram[20:30].strip()
            self.menu.gameMode = datagram[30:].strip()

            if not self.menu.inputsEdited:
                self.menu.populateInputs()

        if datagram.startswith('Result:'):
            if datagram[7:] == "InvalidGameMode":
                self.menu.assistanceText.setText("Invalid game mode!")
                self.menu.assistanceText.setColour(colours.invalidDataColour)
                self.menu.inputEdit()
            elif datagram[7:] == "Success":
                self.menu.stopCountdown('Settings have been saved.')
                self.menu.assistanceText.setColour(colours.startButton)
            self.menu.delayedErase(self.menu.assistanceText)
