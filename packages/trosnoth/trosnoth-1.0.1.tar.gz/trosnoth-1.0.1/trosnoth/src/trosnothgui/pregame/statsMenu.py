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

import os
import time
import webbrowser

import trosnoth.src.trosnothgui.defines as defines
import trosnoth.src.gui.framework.framework as framework
from trosnoth.src.gui.framework.listbox import ListBox
from trosnoth.src.gui.framework.elements import TextElement, TextButton
from trosnoth.src.gui.framework.dialogbox import DialogBox, DialogResult, DialogBoxAttachedPoint
from trosnoth.src.gui.common import *
from trosnoth.src.trosnothgui.pregame import colours
from trosnoth.src.gui.fonts.font import ScaledFont

from trosnoth.data import getPath, user, makeDirs
from trosnoth.src.utils.statGeneration import generateStats

class StatsMenu(framework.CompoundElement):
    def __init__(self, app, startupInterface):
        super(StatsMenu, self).__init__(app)
        self.startupInterface = startupInterface

        font = self.app.screenManager.fonts.bigMenuFont
        smallFont = self.app.screenManager.fonts.ampleMenuFont
        largeFont = self.app.screenManager.fonts.hugeMenuFont

        def newText(string, yValue):
            return TextElement(self.app, string, font,
                               ScaledLocation(985, yValue, 'topright'),
                               colours.headingColour)
        
        self.instructions = ["To view combined",
                             "statistics for",
                             "all games,"]
        self.staticText = []

        yValue = 130
        for string in self.instructions:
            self.staticText.append(newText(string, yValue))
            yValue += 50

        self.viewAllButton = TextButton(self.app, ScaledLocation(985, yValue, 'topright'),
                                        'click here', font,
                                        colours.mainMenuColour, colours.white)
        self.viewAllButton.onClick.addListener(lambda sender: self.viewStats(True))

        # Dynamic text
        self.listHeaderText = TextElement(self.app, 'available replay files:', font,
                                           ScaledLocation(50, 130),
                                           colours.headingColour)
        self.noFiles1Text = TextElement(self.app, '', font,
                                       ScaledLocation(50, 200),
                                       colours.noGamesColour)
        self.noFiles2Text = TextElement(self.app, '', font,
                                       ScaledLocation(50, 250),
                                       colours.noGamesColour)

        self.dynamicText = [self.listHeaderText, self.noFiles1Text, self.noFiles2Text]

        # Text buttons
        
        self.viewButton = TextButton(self.app, ScaledLocation(820, 545, 'midtop'),
                                      '', largeFont,
                                      colours.mainMenuColour, colours.white)
        self.viewButton.onClick.addListener(lambda sender: self.viewStats())
        
        self.refreshButton = TextButton(self.app, ScaledLocation(650, 640),
                                        'refresh', font,
                                        colours.mainMenuColour, colours.white)
        self.refreshButton.onClick.addListener(lambda sender: self.populateList())
        
        self.cancelButton = TextButton(self.app, ScaledLocation(985, 640, 'topright'),
                                       'cancel', font,
                                       colours.mainMenuColour, colours.white)
        self.cancelButton.onClick.addListener(lambda sender: self.startupInterface.mainMenu())

        self.buttons = [self.viewButton, self.refreshButton, self.cancelButton, self.viewAllButton]

        # Game list
        self.gameList = ListBox(self.app, ScaledArea(50, 200, 550, 550),
                                [], font, colours.listboxButtons)
        self.gameList.onValueChanged.addListener(self.updateSidebar)

        # Combine the elements        
        self.elementsFiles = self.staticText + self.dynamicText + self.buttons + [self.gameList]
        self.elementsNoFiles = self.dynamicText + self.buttons

        # Populate the list of games
        self.populateList()

    def populateList(self):

        # Clear out the sidebar
        self.viewButton.setText('')
        self.noFiles1Text.setText('')
        self.noFiles2Text.setText('')
        for i in range(0, len(self.staticText) - 1):
            self.staticText[i].setText('')
        self.listHeaderText.setText('available games:')
        self.gameList.index = -1
        self.elements = self.elementsFiles[:]

        # Get a list of files with the name "*.stat"
        logDir = getPath(user, 'stats')
        makeDirs(logDir)
        self.statFiles = []

        for fname in os.listdir(logDir):
            if fname[-5:] == ".stat":
                self.statFiles.append(fname[:-5])

        if len(self.statFiles) == 0:
            self.elements = self.elementsNoFiles[:]
            self.listHeaderText.setText("0 available games:")
            self.noFiles1Text.setText("You have not yet run any")
            self.noFiles2Text.setText("games on this computer!")
        elif len(self.statFiles) == 1:
            self.listHeaderText.setText("1 available game:")
            self.gameList.index = 0
            self.updateSidebar(0)
        else:
            self.listHeaderText.setText("%d available games:" % len(self.statFiles))
            for i in range(0, len(self.staticText) - 1):
                self.staticText[i].setText(self.instructions[i])

        self.gameList.setItems(self.statFiles)

    def updateSidebar(self, listID):        
        # Enable the view stats button
        self.viewButton.setText("view stats")

    def viewStats(self, allGames = False):
        '''View stats button was clicked.'''
        if allGames:
            self.htmlPath = generateStats()
        else:
            self.htmlPath = generateStats(self.gameList.getItem())

        self.statsGeneratedBox = StatsGeneratedDialog(self.app)
        self.statsGeneratedBox.onClose.addListener(self._dialogClosed)
        self.statsGeneratedBox.Show()

    def _dialogClosed(self):
        if self.statsGeneratedBox.result == DialogResult.OK:
            webbrowser.open(self.htmlPath)
        
    def draw(self, surface):
        super(StatsMenu, self).draw(surface)
        width = max(int(3*self.app.screenManager.scaleFactor), 1)
        scalePoint = self.app.screenManager.placePoint
        pygame.draw.line(surface, colours.mainMenuColour, scalePoint((0,130)), scalePoint((1024, 130)), width)
        pygame.draw.line(surface, colours.mainMenuColour, scalePoint((640,130)), scalePoint((640, 768)), width)
        pygame.draw.line(surface, colours.mainMenuColour, scalePoint((640,540)), scalePoint((1024, 540)), width)

class StatsGeneratedDialog(DialogBox):
    '''Defines the elements and layout thereof of the 'stats successfully generated' dialog box.'''

    def __init__(self, app):
        super(StatsGeneratedDialog, self).__init__(app, ScaledSize(450, 350), "Stats Successfully Generated")

        text = ["A HTML file has been created",
                "containing the requested",
                "statistics. Do you want to",
                "open this file now?",
                "(This will close Trosnoth",
                "if it is in fullscreen mode)"]
        textElements = []

        yValue = 10
        for string in text:
            textElements.append(TextElement(app, string, app.screenManager.fonts.mediumMenuFont,
                                Location(DialogBoxAttachedPoint(self, ScaledSize(0, yValue), 'midtop'), 'midtop'),
                                colours.startButton))
            yValue += 45
        
        font = ScaledFont("KLEPTOCR.TTF", 50)

        # OK Button
        okButton = TextButton(app, Location(DialogBoxAttachedPoint(
                              self, ScaledSize(-100,290), 'midtop'), 'midtop'),
                              "Yes", font, colours.mainMenuColour, colours.white)
        
        okButton.onClick.addListener(lambda sender: self.ok())

        # Cancel Button
        cancelButton = TextButton(app, Location(DialogBoxAttachedPoint(
                                  self, ScaledSize(100,290), 'midtop'), 'midtop'),
                                  "No", font, colours.mainMenuColour, colours.white)
        
        cancelButton.onClick.addListener(lambda sender: self.cancel())

        # Add elements to screen
        self.elements = textElements + [okButton, cancelButton]
        self.setColours(None, None, colours.black)

    def ok(self):
        self.result = DialogResult.OK
        self.Close()
        
    def cancel(self):
        self.result = DialogResult.Cancel
        self.Close()
