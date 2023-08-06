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

# DEBUG: If this flag is set, profile information will be printed on exit.
profileMe = False

# DEBUG: If this flag is set, all game information will be saved to a log file.
logMe = False

import sys, pygame, os
from twisted.internet import reactor, task
from twisted.python import log

from trosnoth.src.trosnothgui import interface
from trosnoth.src import universe
from trosnoth.src.trosnothgui import defines
from trosnoth.src.utils import logging, utils, unrepr
from trosnoth.data import getPath, user
import trosnoth.data.music as music

from trosnoth.src.gui import app
import trosnoth.src.gui.musicManager as musicManager
from trosnoth.src.gui.screenManager import screenManager

def loadSettingsFile(filename):
    filename = getPath(user, filename)
    try:
        fileHandle = open(filename, 'r')
        s = fileHandle.read()
        d = unrepr.unrepr(s)
        if not isinstance(d, dict):
            d = {}
    except IOError:
        d = {}
    return d

def getSettingsValues(kwargs):
    # load what display settings we can from file
    display = loadSettingsFile("display")
    sound = loadSettingsFile("sound")
    allSettings = {}
    allSettings.update(display)
    allSettings.update(sound)
    allSettings.update(kwargs)
    
    if not allSettings.has_key('size'):
        allSettings['size'] = defines.screenSize
    if not allSettings.has_key('fullscreen'):
        allSettings['fullscreen'] = defines.fullScreen
    if not allSettings.has_key('usealpha'):
        allSettings['usealpha'] = defines.useAlpha
    if not allSettings.has_key('playmusic'):
        allSettings['playmusic'] = defines.playMusic
    return allSettings

class Main(app.MultiWindowApplication):
    '''Instantiating the Main class will set up the game. Calling the run()
    method will run the reactor. This class handles the three steps of joining
    a game: (1) get list of clients; (2) connect to a server; (3) join the
    game.'''

    def __init__(self, **kwargs):
        '''Initialise the game.'''

        d = getSettingsValues(kwargs)

        fullscreen = d['fullscreen']
        size = d['size']
        defines.useAlpha = d['usealpha']
        playmusic = d['playmusic']

        if fullscreen:
            options = pygame.locals.FULLSCREEN|pygame.locals.DOUBLEBUF
        else:
            options = 0
        universe.init()
        
        super(Main, self).__init__(size, options, defines.gameName, interface.Interface,
                                   playMusic = playmusic)
        
        # Since we haven't connected to the server, there is no world.
        self.player = None
           
    def __repr__(self):
        return "Main Object"

    # TODO: ultimately, get rid of "restart", and simply send
    # a "recalculate your location+area" message to all elements
    # Then we can get rid of this specific tick method
    

    def changeScreenSize(self, size, fullScreen):
        if fullScreen:
            options = pygame.locals.FULLSCREEN|pygame.locals.DOUBLEBUF
        else:
            options = 0
        
        self.screenManager.setScreenProperties(size, options, defines.gameName)   


def runGame():
    if logMe:
        logging.startLogging()
    
    # Check for command-line parameters.
    params = {}
    exec('params.update(%s)' % ' '.join(sys.argv[1:]))
        
    mainObject = Main(**params)
    
    try:
        mainObject.run_twisted()
    finally:
        mainObject.finalise()
        if logMe:
            logging.endLogging()

if __name__ == '__main__':
    if profileMe:
        import profile
        profile.run('runGame()')
        raw_input('Press enter:')
    else:
        runGame()
