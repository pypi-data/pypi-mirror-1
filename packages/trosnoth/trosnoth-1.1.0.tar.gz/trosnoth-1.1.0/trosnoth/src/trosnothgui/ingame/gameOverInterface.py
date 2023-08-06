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

from trosnoth.src.trosnothgui.ingame import colours
from trosnoth.src.trosnothgui.ingame.ingameMenu import InGameMenu
from trosnoth.src.gui.framework import elements
from trosnoth.src.trosnothgui.credits import CreditsScreen
from trosnoth.src.gui.common import ScaledLocation

class GameOverInterface(InGameMenu):
    def __init__(self, app, team, onDisconnect):
        super(GameOverInterface, self).__init__(app)
        
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
        credits = CreditsScreen(self.app, creditsColour, onDisconnect,
                speed=50, loop=False, startOff=True)
        self.elements = [gameWon, credits]
