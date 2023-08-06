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

from trosnoth.src.gui.framework.tab import Tab
from trosnoth.src.gui.framework.tabContainer import TabSize
from trosnoth.src.gui.framework.listbox import ListBox
from trosnoth.src.gui.framework.elements import TextElement, TextButton
from trosnoth.src.trosnothgui.pregame import colours
from trosnoth.src.gui.common import *

class LanTab(Tab):
    def __init__(self, app, tabContainer, startupInterface, netClient):
        super(LanTab, self).__init__(app, "LAN")
        self.startupInterface = startupInterface
        self.tabContainer = tabContainer
        tabSize = TabSize(tabContainer)
        self.netClient = netClient

        self.serverList = ListBox(self.app, Area(AttachedPoint(ScaledSize(20,60),self.tabContainer._getTabRect), ScaledSize(600,390)),
                                  [],
                                  startupInterface.font,
                                  colours.listboxButtons)
        self.noGamesText = TextElement(self.app, 'no games available',
                                     startupInterface.font,
                                     Location(AttachedPoint(ScaledSize(20,60),self.tabContainer._getTabRect)),
                                     colours.noGamesColour
                         )
        self.elements = [
                         self.button('connect',  self.connect,               ScaledSize(-50, 50), 'topright'),
                         self.button('refresh',  self.refreshServerList,     ScaledSize(-50, 110), 'topright'),
                         self.serverList,
                         TextElement(self.app, 'please select a game:',
                                     startupInterface.font,
                                     Location(AttachedPoint(ScaledSize(20,5),self.tabContainer._getTabRect)),
                                     colours.listboxTitle
                         ),
                         ]
        
    def button(self, text, onClick, pos, anchor='topleft'):
        pos = Location(AttachedPoint(pos,self.tabContainer._getTabRect, anchor), anchor)
        result = TextButton(self.app, pos, text, self.startupInterface.font, colours.mainMenuColour, colours.white)
        result.onClick.addListener(lambda sender: onClick())
        return result

    def connect(self):
        'Connect button was clicked.'
        # Try to connect.
        if self.serverList.index != -1:
            self.startupInterface.lanConnect(self.serverList.getItem())

    def refreshServerList(self):
        # Ask the network client for a list of servers.
        
        self.netClient.refreshServerList().addErrback(self.errorGettingServers)

    def tick(self, deltaT):
        items = self.netClient.getServerList()
        
        if len(items) == 0:
            if self.noGamesText not in self.elements:
                self.elements.append(self.noGamesText)
        elif self.noGamesText in self.elements:
            self.elements.remove(self.noGamesText)
        self.serverList.setItems(items)
        if self.serverList.getNumItems() > 0 and self.serverList.getIndex() == -1:
            self.serverList.setIndex(0)
        super(LanTab, self).tick(deltaT)
        
    def errorGettingServers(self, error):
        # TODO: Some sort of message to user.
        self.serverList.setItems([])
        print >>sys.stderr, 'Error getting server list: %s' % error.getErrorMessage()

    def activated(self):
        self.refreshServerList()
