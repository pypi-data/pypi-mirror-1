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
# Client -> Server
####################

class RequestPlayersMsg(NetworkMessage):
    idString = 'rPls'
    fields = ()
    packspec = ''

class RequestZonesMsg(NetworkMessage):
    idString = 'rZns'
    fields = ()
    packspec = ''

class RequestStarsMsg(NetworkMessage):
    idString = 'rSts'
    fields = ()
    packspec = ''

class RequestUpgradesMsg(NetworkMessage):
    idString = 'rUps'
    fields = ()
    packspec = ''

class RequestTransactionMsg(NetworkMessage):
    idString = 'rTrn'
    fields = 'teamId'
    packspec = 'c'

class RequestUDPStatusMsg(NetworkMessage):
    idString = 'rUDP'
    fields = ()
    packspec = ''

####################
# Server -> Client
####################

class ValidateGameStatusMsg(NetworkMessage):
    idString = 'vGSt'
    fields = 'state', 'timed', 'timeRemaining'
    packspec = 'cbd'

class ValidateTeamStatusMsg(NetworkMessage):
    idString = 'vTSt'
    fields = ('teamId', 'hasCaptain', 'captainId', 'ready', 'orbCount',
            'playerCount', 'hasTransaction')
    packspec = 'cbcbIBb'

class ValidateUpgradesMsg(NetworkMessage):
    '''
    This message carries with it a string of the ids of the players with
    upgrades in play.
    '''
    idString = 'vUps'
    fields = 'playerIds'
    packspec = '*'

class ValidateUpgradeMsg(NetworkMessage):
    '''
    zoneId is only important for turret messages.
    '''
    idString = 'vUpg'
    fields = 'playerId', 'upgradeType', 'inUse', 'zoneId'
    packspec = 'ccbI'

class ValidatePlayersMsg(NetworkMessage):
    idString = 'vPls'
    fields = 'playerIds'
    packspec = '*'
    
class ValidatePlayerMsg(NetworkMessage):
    idString = 'vPlr'
    fields = 'playerId', 'teamId', 'stars', 'zoneId', 'isDead', 'nick'
    packspec = 'ccBIb*'

class ValidateZoneMsg(NetworkMessage):
    '''
    orbTeamId and zoneTeamId should be '\x00' for no team.
    '''
    idString = 'vZon'
    fields = 'zoneId', 'orbTeamId', 'zoneTeamId'
    packspec = 'Icc'

class RequestPlayerUpdateMsg(NetworkMessage):
    idString = 'rUpd'
    fields = 'playerId'
    packspec = 'c'

class RequestZoneUpdateMsg(NetworkMessage):
    idString = 'rZUp'
    fields = 'playerId'
    packspec = 'c'

class ValidateTransactionMsg(NetworkMessage):
    # If there is no upgrade in progress, upgradeType will be '\x00'.
    idString = 'vTrn'
    fields = ('teamId', 'playerId', 'upgradeType', 'timeLeft',
            'contributions')
    packspec = 'cccf*'

    # Default values:
    playerId = '\x00'
    timeLeft = 0
    contributions = ''

class NotifyUDPStatusMsg(NetworkMessage):
    idString = 'vUDP'
    fields = 'connected'
    packspec = 'b'

