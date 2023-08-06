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

'''leaderboard.py - defines the LeaderBoard class which deals with drawing the
leader board to the screen.'''

from twisted.internet import reactor
import trosnoth.src.gui.framework.framework as framework
from trosnoth.src.trosnothgui.ingame.messagebank import MessageBank

class LeaderBoard(framework.CompoundElement):
    def __init__(self, app, world, maxSize, startPt, L_R, U_D, font, maxLength=100):
        super(LeaderBoard, self).__init__(app)
        self.world = world
        self.elements = [MessageBank(app, maxSize, maxLength, startPt, L_R, U_D, font)]
        self.update()

    def update(self):
        self.callDef = reactor.callLater(3, self.update)
        bank = self.elements[0]

        bank.deleteAll()
        for player in self.world.players:
            string = player.detailString()
            bank.newMessage(string, player.team.chatColour)

    def kill(self):
        self.callDef.cancel()
