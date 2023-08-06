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

from trosnoth.src.trosnothgui.pregame.displaySettingsTab import DisplaySettingsTab
from trosnoth.src.trosnothgui.pregame.keymapTab import KeymapTab
from trosnoth.src.trosnothgui.pregame.soundSettingsTab import SoundSettingsTab
from trosnoth.src.gui.framework import framework, elements
from trosnoth.src.gui.framework.tabContainer import TabContainer, TabSize
from trosnoth.src.gui.common import *
from trosnoth.src.trosnothgui import defines
from trosnoth.src.trosnothgui.pregame import colours


class SettingsMenu(framework.CompoundElement):
    def __init__(self, app, startupInterface):
        super(SettingsMenu, self).__init__(app)
        self.startupInterface = startupInterface

        area = ScaledArea(50,140,924, 570)
        bg = pygame.Surface((924, 500))
        bg.fill((0,0,0))
        if defines.useAlpha:
            bg.set_alpha(192)
        self.tabContainer = TabContainer(self.app, area, startupInterface.font, colours.tabContainerColour)
        bp = elements.SizedPicture(app, bg, Location(AttachedPoint((0,0),self.tabContainer._getTabRect)), TabSize(self.tabContainer))

        displayTab = DisplaySettingsTab(app, startupInterface)
        self.tabContainer.addTab(displayTab)
        
        keymapTab = KeymapTab(app, startupInterface)
        self.tabContainer.addTab(keymapTab)

        soundTab = SoundSettingsTab(app, startupInterface)
        self.tabContainer.addTab(soundTab)
        
        self.elements = [bp, self.tabContainer]
