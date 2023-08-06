# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2007  Joshua Bartlett
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

'''chatBox.py - defines the ChatBox class which deals with drawing the
chat box (the box in which you input chat) to the screen.'''

import pygame

from twisted.internet import reactor
from trosnoth.src.gui.framework.elements import TextElement
from trosnoth.src.gui.framework.prompt import InputBox
from trosnoth.src.gui.framework.hotkey import Hotkey
from trosnoth.src.gui.fonts import font
from trosnoth.src.gui.common import *
from trosnoth.src.gui.framework.dialogbox import MoveableBox, DialogResult, DialogBoxAttachedPoint
import trosnoth.src.gui.framework.framework as framework
from trosnoth.src.trosnothgui.ingame import colours

class ChatBox(MoveableBox):
    def __init__(self, app, world, gameViewer):
        super(ChatBox, self).__init__(app, ScaledSize(320, 100), 'Send a Message', 'to team:')
        self.world = world
        self.app = app
        self.gameViewer = gameViewer
        self.chatMode = 'team'


        # Elements
        
        self.inputPosition = Area(DialogBoxAttachedPoint(self, ScaledSize(0,5), 'midtop'), ScaledSize(300,30), 'midtop')
        self.input = InputBox(self.app, self.inputPosition,
                              font=self.app.screenManager.fonts.chatFont)

        self.input.onEnter.addListener(lambda sender: self.hitEnter(sender.value))
        self.input.onEsc.addListener(lambda sender: self.cancel())
        
        self.helpText = TextElement(self.app, 'Press CTRL to broadcast', self.app.screenManager.fonts.keymapFont,
                                        Location(DialogBoxAttachedPoint(self, ScaledSize(0, 50), 'midtop'), 'midtop'),
                                        colours.black)

        self.elements = [self.input, self.helpText]
        self.setFocus(self.input)
        self._setPos((0,0))

    def setPlayer(self, player):
        self.player = player
        self.updateColours()

    def reset(self):
        self.input.setValue('')

    def switchModes(self):
        if self.chatMode == 'team':
            self.chatMode = 'all'
            newSubCaption = 'to everyone:'
            self.helpText.setText('Press CTRL for team message')
        else:
            self.chatMode = 'team'
            newSubCaption = 'to team:'
            self.helpText.setText('Press CTRL to broadcast')

        self.setCaption(subCaption = newSubCaption)
        self.updateColours()

    def updateColours(self):
        titleColour = colours.white
        if self.chatMode == 'team':
            if self.player.team.id == 'A':
                borderColour = colours.chatBlueBorder
                bgColour = colours.chatBlueBackground
            else:
                borderColour = colours.chatRedBorder
                bgColour = colours.chatRedBackground
        else:
            borderColour = colours.chatAllBorder
            bgColour = colours.chatAllBackground

        self.setColours(borderColour, titleColour, bgColour)
        
    def cancel(self):
        self.result = DialogResult.Cancel
        self.Close()
    
    def hitEnter(self, senderValue):
        self.result = DialogResult.OK
        self.world.netClient.sendChat(senderValue, self.player, chatMode = self.chatMode)
        self.Close()

    def processEvent(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
            self.switchModes()
        else:
            return super(ChatBox, self).processEvent(event)
