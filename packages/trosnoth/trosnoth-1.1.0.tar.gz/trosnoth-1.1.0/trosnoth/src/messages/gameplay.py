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

from trosnoth.src.utils.components import Message

class Killing(Message):
    fields = 'target', 'killer', 'shot', 'xPos', 'yPos'

class TaggingZone(Message):
    fields = 'zone', 'player', 'team'

class PlayerKilled(Message):
    fields = 'target', 'killer'

class TaggedZone(Message):
    fields = ('zone', 'player')

class KillShot(Message):
    fields = 'player', 'shot'

class PlayerUpdate(Message):
    fields = ('playerId', 'xPos', 'yPos', 'yVel', 'mapBlockI', 'mapBlockJ',
            'angle', 'ghostThrust',
            'keys')
            #'left', 'right', 'jump', 'down', 'hasUpgrade', 'dead')

class PlayerRespawn(Message):
    fields = 'player', 'zone'

class ZoneChange(Message):
    fields = 'player', 'zone'
