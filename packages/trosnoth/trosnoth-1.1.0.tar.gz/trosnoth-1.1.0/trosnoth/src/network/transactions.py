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

class StartingTransactionMsg(NetworkMessage):
    idString = 'tran'
    fields = 'teamId', 'playerId', 'numStars', 'upgradeType'
    packspec = 'ccbc'

class AddingStarsMsg(NetworkMessage):
    idString = 'star'
    fields = 'teamId', 'playerId', 'numStars'
    packspec = 'ccb'

####################
# Server -> Client
####################

class StartedTransactionMsg(NetworkMessage):
    idString = 'Tran'
    fields = 'teamId', 'playerId', 'numStars', 'upgradeType', 'timeLeft'
    packspec = 'ccbcf'

class AddedStarsMsg(NetworkMessage):
    idString = 'Star'
    fields = 'teamId', 'playerId', 'numStars', 'totalStars'
    packspec = 'ccbb'

class TransactionCompleteMsg(NetworkMessage):
    idString = 'TDun'
    fields = 'teamId', 'playerId', 'upgradeType'
    packspec = 'ccc'

####################
# S->C and C->S
####################

class DeleteUpgradeMsg(NetworkMessage):
    idString = 'DUpg'
    fields = 'playerId'
    packspec = 'c'
    
class AbandonTransactionMsg(NetworkMessage):
    idString = 'Abdn'
    fields = 'teamId'
    packspec = 'c'

class UseUpgradeMsg(NetworkMessage):
    idString = 'UseU'
    fields = 'playerId', 'xPos', 'yPos', 'zoneId', 'upgradeType'
    packspec = 'cffIc'
