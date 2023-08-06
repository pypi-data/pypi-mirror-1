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

class FireShotMsg(NetworkMessage):
    idString = 'shot'
    fields = 'playerId', 'angle', 'xpos', 'ypos', 'type'
    packspec = 'cfffc'

class GrenadeExplodedMsg(NetworkMessage):
    idString = 'gren'
    fields = 'playerId', 'xpos', 'ypos'
    packspec = 'cff'


####################
# Server to Client
####################

class ShotFiredMsg(NetworkMessage):
    idString = 'SHOT'
    fields = 'playerId', 'shotId', 'angle', 'xpos', 'ypos', 'type'
    packspec = 'ccfffc'