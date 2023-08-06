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

from trosnoth.src.gui.framework import framework
from trosnoth.src.gui.framework.elements import TextElement, Backdrop
from trosnoth.data import getPath
from trosnoth.data import startupMenu
from trosnoth.src.trosnothgui.pregame import colours
from trosnoth.version import titleVersion

from trosnoth.src.gui.common import *

class TrosnothBackdrop(framework.CompoundElement):
    def __init__(self, app):
        super(TrosnothBackdrop, self).__init__(app)

        backdrop = Backdrop(app, getPath(startupMenu, 'blackdrop.png'))
    
        # Place the title.
        titlefont = app.screenManager.fonts.titleFont
        titlepos = Location(FullScreenAttachedPoint(ScaledSize(0, 20), 'midtop'), 'midtop')
        title = TextElement(app, 'Trosnoth', titlefont, titlepos, colours.titleColour)

        # Things that will be part of the backdrop of the entire startup menu system.
        verFont = self.app.screenManager.fonts.versionFont
        self.elements = [
            backdrop,
            title,
            TextElement(self.app, titleVersion, verFont,
                Location(FullScreenAttachedPoint(ScaledSize(-10,-10),
                'bottomright'), 'bottomright'), (192, 192, 192))
        ]
