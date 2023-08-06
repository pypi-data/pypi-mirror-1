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

from trosnoth.src.network.netmsg import NetworkMessage

####################
# Client to Server
####################

class KillingMsg(NetworkMessage):
    idString = 'Kill'
    fields = 'targetId', 'killerId', 'shotId', 'xPos', 'yPos'
    packspec = 'cccff'

class TaggingZoneMsg(NetworkMessage):
    idString = 'Tag!'
    fields = 'zoneId', 'playerId', 'teamId'
    packspec = 'Icc'

####################
# Server to Client
####################

class KilledMsg(NetworkMessage):
    idString = 'Dead'
    fields = 'targetId', 'killerId', 'shotId', 'xPos', 'yPos', 'stars'
    packspec = 'cccffB'

class TaggedZoneMsg(NetworkMessage):
    idString = 'Tagd'
    fields = ('zoneId', 'playerId', 'teamId', 'teamOrbCount',
            'playerStarCount', 'killedTurret', 'turretId')
    packspec = 'IccIBBc'

####################
# C->S and S->C
####################

class KillShotMsg(NetworkMessage):
    idString = 'KiSh'
    fields = 'playerId', 'shotId'
    packspec = 'cc'

class PlayerUpdateMsg(NetworkMessage):
    idString = 'PlUp'
    fields = ('playerId', 'xPos', 'yPos', 'yVel', 'angle', 'ghostThrust',
            'keys')
    packspec = 'cfffff*'

class RespawnMsg(NetworkMessage):
    idString = 'Resp'
    fields = 'playerId', 'zoneId'
    packspec = 'cI'

class ZoneChangeMsg(NetworkMessage):
    idString = 'ZnCh'
    fields = 'playerId', 'zoneId'
    packspec = 'cI'
