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
# Server to Client
####################

class AddPlayerMsg(NetworkMessage):
    idString = 'NewP'
    fields = 'playerId', 'teamId', 'zoneId', 'nick'
    packspec = 'ccI*'

class GivePlayerMsg(NetworkMessage):
    idString = 'OwnP'
    fields = 'playerId'
    packspec = 'c'

class RemovePlayerMsg(NetworkMessage):
    idString = 'DelP'
    fields = 'playerId'
    packspec = 'c'

class CannotCreatePlayerMsg(NetworkMessage):
    idString = 'NotP'
    fields = 'reasonId', 'teamId', 'waitTime', 'nick'
    packspec = 'ccf*'
    waitTime = 0 # Default value.


####################
# Client to Server
####################

class JoinRequestMsg(NetworkMessage):
    idString = 'Join'
    fields = 'teamId', 'nick'
    packspec = 'c*'

class LeaveRequestMsg(NetworkMessage):
    idString = 'Leev'
    fields = 'playerId',
    packspec = 'c'
