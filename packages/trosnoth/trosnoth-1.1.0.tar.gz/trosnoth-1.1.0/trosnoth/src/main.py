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
from twisted.internet.error import CannotListenError
from twisted.python import log

from trosnoth.src.trosnothgui import interface
from trosnoth.src.model import universe
from trosnoth.src.trosnothgui import defines
from trosnoth.src.utils import logging, utils, unrepr
from trosnoth.src.network.networkDefines import serverVersion
from trosnoth.data import getPath, user

from trosnoth.src.gui import app
import trosnoth.src.gui.sound.musicManager as musicManager
from trosnoth.src.gui.screenManager import screenManager

from trosnoth.src.network.netman import NetworkManager
from trosnoth.src.network.trosnothdiscoverer import TrosnothDiscoverer
from trosnoth.src.init import initFonts, initMusic, initSound

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

class DisplaySettings(object):
    '''
    Stores the Trosnoth display settings.
    '''

    def __init__(self, app):
        self.app = app

        self.reset()

    def reset(self):
        # Attempt to load the settings from file.
        data = loadSettingsFile('display')

        self.size = data.get('size', defines.screenSize)
        self.fullScreen = data.get('fullscreen', defines.fullScreen)
        self.useAlpha = data.get('usealpha', defines.useAlpha)
        self.fsSize = data.get('fsSize', self.size)

        defines.useAlpha = self.useAlpha

    def getSize(self):
        if self.fullScreen:
            return self.fsSize
        else:
            return self.size

    def apply(self):
        '''
        Apply the current settings.
        '''
        defines.useAlpha = self.useAlpha

        size = self.getSize()

        # Don't bother changing the screen if the settings that matter haven't changed
        if (size != self.app.screenManager.size) or (self.fullScreen !=
                self.app.screenManager.isFullScreen()):
            # Tell the main program to change its screen size.
            self.app.changeScreenSize(size, self.fullScreen)

    def save(self):
        '''
        Save the values to file.
        '''
        # Write to file
        displayFilename = getPath(user, 'display')
        displayFile = open(displayFilename, 'w')
        displayFile.write(repr({
            'size': self.size,
            'fullscreen': self.fullScreen,
            'usealpha': self.useAlpha,
            'fsSize': self.fsSize,
        }))
        displayFile.close()
        
class SoundSettings(object):
    '''
    Stores the Trosnoth display settings.
    '''

    def __init__(self, app):
        self.app = app

        self.reset()

    def reset(self):
        # Attempt to load the settings from file.
        data = loadSettingsFile('sound')

        self.soundEnabled = data.get('playSound', True)
        self.musicEnabled = data.get('playMusic', True)
        self.musicVolume = data.get('musicVolume', 100)
        self.soundVolume = data.get('soundVolume', 100)

    def apply(self):
        '''
        Apply the current settings.
        '''

        if self.musicEnabled != self.app.musicManager.isMusicPlaying():
            if self.musicEnabled:
                self.app.musicManager.playMusic()
            else:
                self.app.musicManager.stopMusic()

        self.app.musicManager.setVolume(self.musicVolume)

        if self.soundEnabled:
            self.app.soundPlayer.setMasterVolume(self.soundVolume / 100.)
        else:
            self.app.soundPlayer.setMasterVolume(0)

    def save(self):
        '''
        Save the values to file.
        '''
        # Write to file
        filename = getPath(user, 'sound')
        dataFile = open(filename, 'w')
        dataFile.write(repr({
            'playSound': self.soundEnabled,
            'playMusic': self.musicEnabled,
            'musicVolume': self.musicVolume,
            'soundVolume': self.soundVolume
        }))
        dataFile.close()
        

class Main(app.MultiWindowApplication):
    '''Instantiating the Main class will set up the game. Calling the run()
    method will run the reactor. This class handles the three steps of joining
    a game: (1) get list of clients; (2) connect to a server; (3) join the
    game.'''

    def __init__(self, **kwargs):
        '''Initialise the game.'''

        self.initNetwork()

        self.displaySettings = DisplaySettings(self)
        self.soundSettings = SoundSettings(self)

        if self.displaySettings.fullScreen:
            options = pygame.locals.FULLSCREEN
        else:
            options = 0
        universe.init()
        
        super(Main, self).__init__(
            self.displaySettings.getSize(),
            options,
            defines.gameName,
            interface.Interface)
        
        # Set the master sound volume.
        self.soundSettings.apply()

        # Since we haven't connected to the server, there is no world.
        self.player = None
           
    def __str__(self):
        return 'Trosnoth Main Object'

    def initNetwork(self):
        self.server = None

        # Set up the network connection.
        try:
            self.netman = NetworkManager(6789, 6789)
        except CannotListenError:
            # Set up a network manager on an arbitrary port (i.e.
            # you probably cannot run an Internet server because you
            # won't have port forwarding for the correct port.)
            self.netman = NetworkManager(0, None)
            
            # TODO: Perhaps show a message on the interface warning that games
            # may not be visible on the Internet.

        # Set up the game discovery protocol.
        self.discoverer = TrosnothDiscoverer(self.netman)

    def stopping(self):
        # Shut down the server if one's running.
        if self.server is not None:
            self.server.shutdown()

        # Save the discoverer's peers.
        self.discoverer.kill()

        super(Main, self).stopping()

    def _initFonts(self):
        super(Main, self)._initFonts()
        initFonts(self.fonts)

    def _initSound(self):
        super(Main, self)._initSound()
        initMusic(self.musicManager)
        initSound(self.soundPlayer)

    def changeScreenSize(self, size, fullScreen):
        if fullScreen:
            options = pygame.locals.FULLSCREEN
        else:
            options = 0
        
        self.screenManager.setScreenProperties(size, options, defines.gameName)   

    def startServer(self, serverName, halfMapWidth=None, mapHeight=None,
                    maxPlayers=None, gameDuration=None, recordReplay=None,
                    invisibleGame=False):
        'Starts a server.'
        if self.server is not None:
            if self.server.running:
                return
        settings = {}
        
        if halfMapWidth != None:
            settings['halfMapWidth'] = halfMapWidth
        if mapHeight != None:
            settings['mapHeight'] = mapHeight
        if maxPlayers != None:
            settings['maxPlayers'] = maxPlayers
        if gameDuration != None:
            settings['gameDuration'] = gameDuration
        if recordReplay != None:
            settings['recordReplay'] = recordReplay
            
        from trosnoth.src.network.networkServer import ServerNetHandler

        try:
            self.server = ServerNetHandler(self.netman, serverName,
                    settings=settings)
        except:
            # Creating a local server failed
            logging.writeException()
        else:
            # Tell the discovery protocol about it.
            if not invisibleGame:
                info = {
                    'name': serverName,
                    'version': serverVersion,
                }
                self.discoverer.setGame(info)
                self.server.onShutdown.addListener(self._serverShutdown)

    def _serverShutdown(self):
        self.discoverer.delGame()
        self.server = None

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
        if logMe:
            logging.endLogging()

if __name__ == '__main__':
    if profileMe:
        import cProfile as profile
        profile.run('runGame()')
        raw_input('Press enter:')
    else:
        runGame()
