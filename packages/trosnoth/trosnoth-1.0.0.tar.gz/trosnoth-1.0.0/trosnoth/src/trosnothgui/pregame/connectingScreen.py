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

from trosnoth.src.gui.framework.elements import TextElement
from trosnoth.src.gui.framework import framework
from trosnoth.src.gui.common import ScaledLocation
from trosnoth.src.trosnothgui.pregame import colours


class ConnectingScreen(framework.CompoundElement):
    def __init__(self, app, startupInterface, serverName = 'server'):
        super(ConnectingScreen, self).__init__(app)
        self.startupInterface = startupInterface

        button = startupInterface.button

        self.text = TextElement(self.app, 'Connecting to %s...' % serverName,
                                     startupInterface.font,
                                     ScaledLocation(512, 384, 'center'),
                                     colour = colours.connectingColour)
        self.elements = [button('cancel', startupInterface.cancelConnect,
                                (0, 300), 'center'),
                         self.text
                         ]

    def setServer(self, serverName):
        self.text.setText('Connecting to %s...' % serverName)
        self.text.setFont(self.startupInterface.font)
