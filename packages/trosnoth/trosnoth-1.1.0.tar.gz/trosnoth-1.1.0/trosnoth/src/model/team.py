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

import trosnoth

class Team(object):
    '''Represents a team of the game'''
    def __init__(self, bkgColour, sysMsgColour, chatColour, miniMapZoneOwnColour,
                 miniMapOrbOwnColour, miniPlayerClr, miniGhostClr, img, shotImg, orbImg, teamID):
        self.currentTransaction = None
        self.numOrbsOwned = 0
        try:
            trosnoth._testmode
            self.teamStars = 100
        except AttributeError:
            self.teamStars = 0
        self.backgroundColour = bkgColour
        self.sysMessageColour = sysMsgColour
        self.chatColour = chatColour
        self.miniMapZoneOwnColour = miniMapZoneOwnColour
        self.miniMapOrbOwnColour = miniMapOrbOwnColour
        self.miniMapPlayerColour = miniPlayerClr
        self.miniMapGhostColour = miniGhostClr
        self.captain = None
        self.ready = False
        self.image = img
        self.shotImage = shotImg
        self.orbImage = orbImg

        if (not isinstance(teamID, str)) or len(teamID) != 1:
            raise TypeError, 'teamID must be a single character'
        self.id = teamID

        if teamID == "A":
            self.teamName = "Blue"
        else:
            self.teamName = "Red"
        
    def __repr__(self):
        return '%s team' % self.teamName

    def orbLost(self):
        '''Called when a orb belonging to this team has been lost'''
        self.numOrbsOwned -= 1

    def orbGained(self):
        '''Called when a orb has been attributed to this team'''
        self.numOrbsOwned += 1

    def checkLost(self):
        '''Returns whether the team has lost the game (True = Lost Game)'''
        return self.numOrbsOwned == 0

    def validate(self, numOrbs):
        return self.numOrbsOwned == numOrbs
            

    def updateTeamStars(self, stars):
        self.teamStars += stars

    @staticmethod
    def setOpposition(teamA, teamB):
        teamA.opposingTeam = teamB
        teamB.opposingTeam = teamA
