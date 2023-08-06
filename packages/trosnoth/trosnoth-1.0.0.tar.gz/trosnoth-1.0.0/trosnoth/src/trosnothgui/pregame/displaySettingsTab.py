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

from trosnoth.data import getPath, user
from trosnoth.src.gui.framework import framework
from trosnoth.src.gui.framework.elements import TextElement, TextButton
from trosnoth.src.gui.framework.checkbox import CheckBox
from trosnoth.src.gui.framework.tab import Tab
import trosnoth.src.gui.framework.prompt as prompt
import trosnoth.src.trosnothgui.pregame.colours as colours
from trosnoth.src.trosnothgui import defines
from trosnoth.src.gui.common import *


class DisplaySettingsTab(Tab, framework.TabFriendlyCompoundElement):
    def __init__(self, app, startupInterface):
        super(DisplaySettingsTab, self).__init__(app, "Display")
        self.startupInterface = startupInterface

        button = startupInterface.button

        font = self.app.screenManager.fonts.bigMenuFont
        smallNoteFont = self.app.screenManager.fonts.smallNoteFont

        self.text = [
                     TextElement(self.app, 'X', font,
                                 ScaledLocation(630, 310, 'topright'),
                                 colours.headingColour),
                     TextElement(self.app, 'Screen Resolution', font,
                                 ScaledLocation(400, 310, 'topright'),
                                 colours.headingColour),
                     TextElement(self.app, 'Fullscreen Mode', font,
                                 ScaledLocation(400, 380,'topright'),
                                 colours.headingColour),
                     TextElement(self.app, 'Use Alpha Channel', font,
                                 ScaledLocation(400, 450,'topright'),
                                 colours.headingColour),
                     TextElement(self.app, 'Deselect this option if Ghosts or Phase Shift',
                                 smallNoteFont,
                                 ScaledLocation(520, 455,'topleft'),
                                 colours.headingColour),
                     TextElement(self.app, 'cause your framerate to go down.',
                                 smallNoteFont,
                                 ScaledLocation(520, 485,'topleft'),
                                 colours.headingColour),
                                 ]

        self.invalidInputText = TextElement(self.app, '', font,
                                            ScaledLocation(512, 245,'midtop'),
                                            (192, 0,0))

        self.widthInput = prompt.InputBox(self.app, ScaledArea(450, 310, 150, 60),
                                          initValue = str(self.app.screenManager.size[0]),
                                          font = font,
                                          maxLength = 4,
                                          validator = prompt.intValidator)

        self.widthInput.onEnter.addListener(lambda sender: self.saveSettings())
        self.widthInput.onClick.addListener(self.setFocus)
        self.widthInput.onTab.addListener(self.tabNext)

        self.heightInput = prompt.InputBox(self.app, ScaledArea(642, 310, 150, 60),
                                          initValue = str(self.app.screenManager.size[1]),
                                          font = font,
                                          maxLength = 4,
                                          validator = prompt.intValidator)

        self.heightInput.onEnter.addListener(lambda sender: self.saveSettings())
        self.heightInput.onClick.addListener(self.setFocus)
        self.heightInput.onTab.addListener(self.tabNext)

        self.tabOrder = [self.widthInput, self.heightInput]
        
        self.fullscreenBox = CheckBox(self.app, ScaledLocation(450, 390),
                                             text = '',
                                             font = font,
                                             colour = (192,192,192),
                                             initValue = self.app.screenManager.isFullScreen())

        self.alphaBox = CheckBox(self.app, ScaledLocation(450, 460),
                                 text = '',
                                 font = font,
                                 colour = (192,192,192),
                                 initValue = defines.useAlpha)
        
        self.input = [self.widthInput, self.heightInput, self.widthInput, self.fullscreenBox, self.alphaBox]
        
        self.elements = self.text + self.input + \
                        [self.invalidInputText,
                         button('save',
                                self.saveSettings,
                                (-100, -50), 'midbottom'),
                         button('cancel',
                                startupInterface.mainMenu,
                                (100, -50), 'midbottom'),
                         ]
        self.setFocus(self.widthInput)

        
    def saveSettings(self):
        values = self.getValues()
        if values is not None:
            screenSize, fullScreen, useAlpha = values

            # Write to file
            displayFilename = getPath(user, 'display')
            displayFile = open(displayFilename, 'w')
            displayFile.write(repr({'size' : screenSize,
                                    'fullscreen' : fullScreen,
                                    'usealpha'   : useAlpha}))
            displayFile.close()

            defines.useAlpha = useAlpha

            # Don't bother changing the screen if the settings that matter haven't changed
            if (screenSize != self.app.screenManager.size) or (fullScreen != self.app.screenManager.isFullScreen()):
                # Tell the main program to change its screen size.
                self.startupInterface.interface.app.changeScreenSize(screenSize, fullScreen)

            self.startupInterface.mainMenu()

    def getValues(self):

        height = self.getInt(self.heightInput.value)
        width = self.getInt(self.widthInput.value)
        fullScreen = self.fullscreenBox.value
        useAlpha = self.alphaBox.value

        '''The resolutionList is used when fullScreen is true.'''
        resolutionList = pygame.display.list_modes()
        resolutionList.sort()
        minResolution = resolutionList[0]
        resolutionList.sort(reverse=True)    
        maxResolution = resolutionList[0]

        if defines.limitResolution:
            maxResolution = defines.limitResolution

        if not fullScreen:
            minResolution = (320, 240)

        '''These values are used when fullScreen is false.'''
        # TODO: instead of using the maximum of all possible resolutions,
        # use the current resolution as the maximum size instead
        # (but only when fullScreen == false)
        widthRange = (minResolution[0], maxResolution[0])
        heightRange = (minResolution[1], maxResolution[1])

        if not widthRange[0] <= width <= widthRange[1]:
            self.incorrectInput("Screen width must be between %d and %d" %
                                (widthRange[0], widthRange[1]))
            width = None
            return
        if not heightRange[0] <= height <= heightRange[1]:
            self.incorrectInput("Screen height must be between %d and %d" %
                                (heightRange[0], heightRange[1]))
            height = None
            return
        if fullScreen:
            selectedResolution = (width, height)
            if selectedResolution not in resolutionList:
                self.incorrectInput("Selected resolution is not valid for this display")
                height = width = None
                return

        self.incorrectInput("")

        return [(width, height), fullScreen, useAlpha]

    def getInt(self, value):
        if value == '':
            return 0
        return int(value)
        
    def incorrectInput(self, string):
        self.invalidInputText.setText(string)
        self.invalidInputText.setFont(self.startupInterface.font)
