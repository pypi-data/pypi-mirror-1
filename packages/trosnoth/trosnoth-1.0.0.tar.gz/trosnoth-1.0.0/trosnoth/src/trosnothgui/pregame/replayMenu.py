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
import pickle
import base64
import time

import trosnoth.src.trosnothgui.defines as defines
import trosnoth.src.gui.framework.framework as framework
from trosnoth.src.gui.framework.listbox import ListBox
from trosnoth.src.gui.framework.elements import TextElement, TextButton
from trosnoth.src.gui.common import *
from trosnoth.src.trosnothgui.pregame import colours

from trosnoth.data import getPath, user, makeDirs

from trosnoth.src.networkDefines import replayVersion


class ReplayMenu(framework.CompoundElement):
    def __init__(self, app, startupInterface, netClient):
        super(ReplayMenu, self).__init__(app)
        self.startupInterface = startupInterface
        self.netClient = netClient

        font = self.app.screenManager.fonts.bigMenuFont
        smallFont = self.app.screenManager.fonts.ampleMenuFont
        largeFont = self.app.screenManager.fonts.hugeMenuFont

        # Static text
        self.staticText = [TextElement(self.app, 'server details:', font,
                                       ScaledLocation(985, 130, 'topright'),
                                       colours.headingColour),
                           TextElement(self.app, 'date and time:', font,
                                       ScaledLocation(985, 370, 'topright'),
                                       colours.headingColour) ]

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
        self.serverNameText = TextElement(self.app, '', font,
                                          ScaledLocation(985, 185, 'topright'),
                                          colours.startButton)
        self.serverDetailsText = TextElement(self.app, '', font,
                                             ScaledLocation(985, 240, 'topright'),
                                             colours.startButton)
        self.teamNamesText = TextElement(self.app, '', smallFont,
                                         ScaledLocation(985, 295, 'topright'),
                                         colours.startButton)
        self.dateText = TextElement(self.app, '', smallFont,
                                    ScaledLocation(985, 430, 'topright'),
                                    colours.startButton)
        self.lengthText = TextElement(self.app, '', smallFont,
                                      ScaledLocation(985, 480, 'topright'),
                                      colours.startButton)

        self.dynamicText = [self.listHeaderText, self.noFiles1Text, self.noFiles2Text, self.serverNameText,
                            self.serverDetailsText, self.teamNamesText, self.dateText, self.lengthText]

        # Text buttons
        self.watchButton = TextButton(self.app, ScaledLocation(905, 545, 'topright'),
                                      '', largeFont,
                                      colours.mainMenuColour, colours.white)
        self.watchButton.onClick.addListener(lambda sender: self.watch())
        
        self.refreshButton = TextButton(self.app, ScaledLocation(650, 640),
                                        'refresh', font,
                                        colours.mainMenuColour, colours.white)
        self.refreshButton.onClick.addListener(lambda sender: self.populateList())
        
        self.cancelButton = TextButton(self.app, ScaledLocation(985, 640, 'topright'),
                                       'cancel', font,
                                       colours.mainMenuColour, colours.white)
        self.cancelButton.onClick.addListener(lambda sender: self.startupInterface.mainMenu())

        self.buttons = [self.watchButton, self.refreshButton, self.cancelButton]

        # Replay list
        self.replayList = ListBox(self.app, ScaledArea(50, 200, 550, 550),
                                  [], font, colours.listboxButtons)
        self.replayList.onValueChanged.addListener(self.updateSidebar)

        # Combine the elements        
        self.elementsFiles = self.staticText + self.dynamicText + self.buttons + [self.replayList]
        self.elementsNoFiles = self.dynamicText + self.buttons

        # Populate the list of replays
        self.populateList()

    def populateList(self):

        # Clear out the sidebar
        self.serverNameText.setText('')
        self.serverDetailsText.setText('')
        self.teamNamesText.setText('')
        self.dateText.setText('')
        self.lengthText.setText('')
        self.watchButton.setText('')
        self.noFiles1Text.setText('')
        self.noFiles2Text.setText('')
        self.listHeaderText.setText('available replay files:')
        self.replayList.index = -1
        self.elements = self.elementsFiles[:]

        # Get a list of files with the name "*.replay"
        logDir = getPath(user, 'replays')
        makeDirs(logDir)
        replayFiles = []
        self.replayInfo = {}

        for fname in os.listdir(logDir):
            if fname[len(fname)-7:len(fname)] == ".replay":
                replayFiles.append(fname)

        # It is possible (and is in fact extremely likely) that what
        # constitutes a valid replay file will change over time.

        # The primary solution (although not completely ideal) is to only allow
        # clients to view replays made in the same version of Trosnoth. To do this
        # it grabs the replayVersion variable from networkDefines.py and compares
        # it to the replay version stored in the replay file.
        
        # Go through the files found and check that they are valid.
        # SVer and Okay are not currently used.
        validIdentifiers = ['Name', 'Date', 'SVer', 'Okay', 'RVer', 'Sett', 'CStr', 'Time']
        for fname in replayFiles:
            replayFile = open(logDir + "/" + fname, "r")
            line = ""
            score = 0
            tempInfoStorage = {}
            while line.strip() != "InfoOver":
                line = replayFile.readline()
                # If the line 'InfoOver' isn't found in the file, it isn't valid
                if line == '':
                    score = 0
                    break
                    continue
                if line[:6] == "Info: " and line[10:12] == ": ":
                    # Make sure that all of the replay information is present
                    if line[6:10] in validIdentifiers:
                        score += 1
                        tempInfoStorage[line[6:10]] = line[12:].rstrip()
                    if line[6:10] == "RVer":
                        loadedReplayVersion = line[12:-1]

            try:
                secondLastLine = file(logDir + "/" + fname).readlines()[-1].strip()
            except IndexError:
                continue

            if not secondLastLine.startswith("ReplayData: "):
                continue
                        
            if score == len(validIdentifiers):
                # Check that this version of Trosnoth matches the replay
                if loadedReplayVersion == replayVersion:
                    displayName = fname[:len(fname)-7]
                    tempInfoStorage['File'] = fname
                    tempInfoStorage['Last'] = secondLastLine[12:26]
                    self.replayInfo[displayName] = tempInfoStorage.copy()
                   
        # All of these checks are pretty easy to fool if somebody creates a replay
        # file manually, but if they do anything like that they should expect the
        # program to break.

        # TODO: allow the user to set their own name for the replay file and show
        #       this as the name in the list (much like StarCraft).
        
        # Sort the replays with most recent first.
        items = [(v['Time'], n) for n, v in self.replayInfo.iteritems()]
        items.sort(reverse=True)
        items = [n for v,n in items]
        self.replayList.setItems(items)

        if len(self.replayInfo) == 0:
            self.elements = self.elementsNoFiles[:]
            self.listHeaderText.setText("0 available replay files:")
            self.noFiles1Text.setText("You have not yet recorded")
            self.noFiles2Text.setText("any replays!")
        elif len(self.replayInfo) == 1:
            self.listHeaderText.setText("1 available replay file:")
            self.replayList.index = 0
            self.updateSidebar(0)
        else:
            self.listHeaderText.setText("%d available replay files:" % len(self.replayInfo))

    def updateSidebar(self, listID):
        # Update the details on the sidebar
        displayName = self.replayList.getItem(listID)

        # Server title [Name]
        self.serverNameText.setText(self.replayInfo[displayName]['Name'])

        # Map size [Sett][halfMapWidth] x [Sett][mapHeight]
        serverSettings = pickle.loads(base64.b64decode(self.replayInfo[displayName]['Sett']))
        self.serverDetailsText.setText("map size: %d x %d" % (serverSettings['halfMapWidth'], serverSettings['mapHeight']))

        # Team names [Sett][teamNames]
        if not serverSettings['teamNames']:
            blueTeam = "Blue"
            redTeam = "Red"
        else:
            blueTeam = serverSettings['teamNames'][0]
            redTeam = serverSettings['teamNames'][1]
        self.teamNamesText.setText(blueTeam + " vs " + redTeam)

        # Date and time of match [Date]
        datePython = time.strptime(self.replayInfo[displayName]['Date'], "%Y-%m-%d %H-%M-%S")
        dateString = time.strftime("%a %d/%m/%y, %H:%M", datePython)
        self.dateText.setText(dateString)

        # Length of match [Last]
        dateUnix = int(time.mktime(datePython))
        lastUnix = float(self.replayInfo[displayName]['Last'])

        lengthSeconds = int(lastUnix - dateUnix)
        lengthMinutes, lengthSeconds = divmod(lengthSeconds, 60)

        secPlural = ("s", "")[lengthSeconds == 1]
        minPlural = ("s", "")[lengthMinutes == 1]
        if lengthMinutes == 0:
            lengthString = "%d second%s" % (lengthSeconds,secPlural)
        else:
            lengthString = "%d min%s, %d sec%s" % (lengthMinutes, minPlural, lengthSeconds, secPlural)

        self.lengthText.setText(lengthString)
        
        # Enable the watch button
        self.watchButton.setText("watch")

    def watch(self):
        '''Watch button was clicked.'''
        # Try to create a replay server.
        if self.replayList.index != -1:
            self.startupInterface.replayConnect(self.replayInfo[self.replayList.getItem()]['File'], self.replayList.getItem())

    def draw(self, surface):
        super(ReplayMenu, self).draw(surface)
        width = max(int(3*self.app.screenManager.scaleFactor), 1)
        scalePoint = self.app.screenManager.placePoint
        pygame.draw.line(surface, colours.mainMenuColour, scalePoint((0,130)), scalePoint((1024, 130)), width)
        pygame.draw.line(surface, colours.mainMenuColour, scalePoint((640,130)), scalePoint((640, 768)), width)
        #pygame.draw.line(surface, colours.mainMenuColour, scalePoint((640,364)), scalePoint((1024, 364)), width)
        pygame.draw.line(surface, colours.mainMenuColour, scalePoint((640,540)), scalePoint((1024, 540)), width)
