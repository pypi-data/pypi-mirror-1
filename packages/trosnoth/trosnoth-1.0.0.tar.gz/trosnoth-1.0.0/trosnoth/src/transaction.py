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

'''transaction.py - defines the Transaction class; keeps a record of who
has given how many stars towards purchasing an upgrade'''

from trosnoth.src.utils.utils import timeNow, new
from trosnoth.src.utils.event import Event
import trosnoth.src.utils.logging as logging
from twisted.internet import reactor


class TransactionState(object):
    Open, Abandoned, Completed = new(3)

TransactionStateText = {
    TransactionState.Open : 'Open',
    TransactionState.Abandoned : 'Abandoned',
    TransactionState.Completed : 'Completed'
    }

class Transaction(object):
    '''Represents the purchasing of an upgrade; initiated by any player on a
    team. It performs calculations pertaining to the transaction, and will
    complete or abandon the transaction'''
    
    def __init__(self, team, player, upgrade, timeLeft = 30.):
        self.purchasingTeam = team
        self.purchasingTeam.currentTransaction = self
        self.purchasingPlayer = player
        self.contributions = {}
        self.totalStars = 0
        self.upgrade = upgrade
        self.requiredStars = self.upgrade.requiredStars
        self.state = TransactionState.Open

        # onNumStarsChanged events will take three parameters when triggered:
        # 1. This transaction object
        # 2. The player who added these stars
        # 3. The number of stars this person added
        self.onNumStarsChanged = Event()

        # onStateChanged events will take two parameters when triggered:
        # 1. This transaction object
        # 2. The current TransactionState
        self.onStateChanged = Event()
        
    def getNumStars(self, player):
        '''Returns the number of stars a certain player has donated towards this
        transaction'''
        if self.contributions.has_key(player):
            return self.contributions[player]
        else:
            return 0
        
    def addStars(self, player, stars):
        '''Adds the given number of stars to the transaction'''

        # Checking code (could ask for validation)        
        assert self.totalStars + stars <= self.requiredStars

        self._doTheAdding(player, stars)

        if stars > 0:
            self.onNumStarsChanged.execute(self, player, stars)

    def _doTheAdding(self, player, stars):
        if self.contributions.has_key(player):
            self.contributions[player] += stars
        else:
            self.contributions[player] = stars
        self.totalStars += stars

    def removeStars(self, player):
        '''Removes all of a player's contribution (used if they die/inexplicably
        leave the game)'''
        try:
            num = self.contributions[player]
        except KeyError:
            # Player has no stars currently contributed
            logging.writeException()
            return
        # Remove the player all their contributing stars from the list
        del self.contributions[player]
        self.totalStars -= num
        self.onNumStarsChanged.execute(self, player, self.totalStars)


    def complete(self):
        '''Completes the transaction. Stars' removal is taken care of by
        the netClient'''
        if self.state == TransactionState.Open:
            self.purchasingPlayer.upgrade = self.upgrade(self.purchasingPlayer)
            self.state = TransactionState.Completed
            self.onStateChanged.execute(self, self.state)
            self.purchasingTeam.currentTransaction = None

    def abandon(self):
        if self.state == TransactionState.Open:
            self.state = TransactionState.Abandoned
            self.onStateChanged.execute(self, self.state)
            self.purchasingTeam.currentTransaction = None


class ServerTransaction(Transaction):
    '''Represents the purchasing of an upgrade; initiated by any player on a
    team. It performs calculations pertaining to the transaction, and will
    complete or abandon the transaction'''
    
    timeLimit = 30.
    
    def __init__(self, team, player, upgrade):
        if team.teamStars < upgrade.requiredStars:
            raise ValueError,  "Team doesn't have enough stars for that"
        super(ServerTransaction, self).__init__(team, player, upgrade)
        self.universe = player.universe
        self.timeMade = timeNow()
        reactor.callLater(self.timeLimit, self.abandon)

    def age(self):
        return self.timeLimit - timeNow() + self.timeMade
        
    def addStars(self, player, stars):
        '''Adds the given number of stars to the transaction'''

        # Checking code        
        if self.totalStars + stars > self.requiredStars:
            stars = self.requiredStars - self.totalStars
        if player.stars < stars:
            # Player has incorrect star data. Send it back.
            self.universe.netServer.validateStars(player = player)
            return

        self._doTheAdding(player, stars)

        # Server-side only check        
        if self.totalStars >= self.requiredStars:
            # The transaction is complete
            self.complete()
        elif stars > 0:
            self.onNumStarsChanged.execute(self, player, stars)
                
    def removeStars(self, player):
        '''Removes all of a player's contribution (used if they die/inexplicably
        leave the game)'''
        if self.state == TransactionState.Open and self.contributions.has_key(player):
            num = self.contributions[player]
            # Remove the player and all their contributed stars from the list
            del self.contributions[player]
            self.totalStars -= num

    def complete(self):
        # This is quite fragile and could use some refactoring:
        # if you call team.removeStars before setting the state,
        # it will try to abandon the transaction. This won't
        # succeed if you have first set the state to Completed.
        # However, if you simply call the superclass to set completed
        # state, before updating the star numbers, it will also trigger
        # the onStateChanged event, which will send an update to everyone
        # with the wrong star numbers for everyone.
        if self.state == TransactionState.Open:
            for player in self.contributions.keys():
                player.removeStars(self.contributions[player])
            super(ServerTransaction, self).complete()
            self.purchasingTeam.removeStars(self.requiredStars)
