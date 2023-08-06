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


class SoundSettingsTab(Tab, framework.TabFriendlyCompoundElement):
    def __init__(self, app, startupInterface):
        super(SoundSettingsTab, self).__init__(app, "Sounds")
        self.startupInterface = startupInterface

        button = startupInterface.button

        font = self.app.screenManager.fonts.bigMenuFont
        smallNoteFont = self.app.screenManager.fonts.smallNoteFont

        self.text = [TextElement(self.app, 'Play Music', font,
                                 ScaledLocation(400, 310, 'topright'),
                                 colours.headingColour)]

        self.invalidInputText = TextElement(self.app, '', font,
                                            ScaledLocation(512, 245,'midtop'),
                                            (192, 0,0))

        self.musicBox = CheckBox(self.app, ScaledLocation(450, 320),
                                 text = '',
                                 font = font,
                                 colour = (192,192,192),
                                 initValue = self.app.musicManager.isMusicPlaying())
        
        self.input = [self.musicBox]

        self.buttons = [button('save', self.saveSettings, (-100, -50), 'midbottom'),
                        button('cancel', startupInterface.mainMenu, (100, -50), 'midbottom')]
        
        self.elements = self.text + self.input + [self.invalidInputText] + self.buttons
        
    def saveSettings(self):
        values = self.getValues()
        if values is not None:
            playMusic = values[0]

            # Write to file
            soundFilename = getPath(user, 'sound')
            soundFile = open(soundFilename, 'w')
            soundFile.write(repr({'playmusic' : playMusic}))
            soundFile.close()

            if (playMusic != self.app.musicManager.isMusicPlaying()):
                if playMusic:
                    self.app.musicManager.playMusic()
                else:
                    self.app.musicManager.stopMusic()
                    
            defines.playMusic = playMusic

            self.startupInterface.mainMenu()

    def getValues(self):

        playMusic = self.musicBox.value

        self.incorrectInput("")

        return [playMusic, ""]

    def getInt(self, value):
        if value == '':
            return 0
        return int(value)
        
    def incorrectInput(self, string):
        self.invalidInputText.setText(string)
        self.invalidInputText.setFont(self.startupInterface.font)
