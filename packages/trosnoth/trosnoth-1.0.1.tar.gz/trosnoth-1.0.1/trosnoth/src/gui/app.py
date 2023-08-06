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

import pygame

from pygame.locals import QUIT

from screenManager import screenManager, windowManager
from musicManager import MusicManager

# timeNow is used to update things based on how much time has passed.
# Note: on Windows, time.clock() is more precise than time.time()
import platform
if platform.system() == 'Windows':
    from time import clock as timeNow
else:
    from time import time as timeNow    

class ApplicationExit(Exception):
    pass

class Application(object):
    '''Instantiating the Main class will set up a ui. Calling the run()
    method will run the application.'''

    def __init__(self, size, graphicsOptions, caption, element, playMusic=False):
        '''Initialise the application.'''
        self.musicManager = MusicManager()

        # Load the music and start playing it.
        if playMusic:
            self.musicManager.playMusic()

        self._makeScreenManager(element, size, graphicsOptions, caption)
        self.fonts = self.screenManager.fonts
        self.lastTime = None

    def __getattr__(self, attr):
        if attr == 'interface':
            return self.screenManager.interface

    def _makeScreenManager(self, element, size, graphicsOptions, caption):
        self.screenManager = screenManager.ScreenManager(self, size,
                                                         graphicsOptions, caption)
        self.fonts = self.screenManager.fonts
        self.screenManager.createInterface(element)

    def run(self):
        '''Runs the application.'''
        def _stop():
            raise ApplicationExit
        self._stop = _stop
        
        self.lastTime = timeNow()
        while True:
            try:
                self.tick()
            except ApplicationExit:
                break

    def run_twisted(self, reactor=None):
        '''Runs the application using Twisted's reactor.'''
        from twisted.internet import task

        if reactor is None:
            from twisted.internet import reactor
        
        self._stop = reactor.stop
        self.lastTime = timeNow()
        
        task.LoopingCall(self.tick).start(0, False).addErrback(self._tickError)
        reactor.run()

    def stop(self):
        self._stop()
        
        
    def tick(self):
        '''Processes the events in the pygame event queue, and causes the
        application to be updated, then refreshes the screen. This routine is
        called as often as possible - it is not limited to a specific frame
        rate.'''
        # Process the events in the event queue.
        for event in pygame.event.get():
            event = self.screenManager.processEvent(event)
            if event is not None and event.type == QUIT:
                self.stop()
                return

        # Give things an opportunity to update their state.
        now = timeNow()
        deltaT = now - self.lastTime
        self.lastTime = now
        self.screenManager.tick(deltaT)

        # Update the screen.
        self.screenManager.draw(self.screenManager.screen)

        # Flip the display.
        pygame.display.flip()

    def _tickError(self, result):
        self.stop()
        
        # Returning the error will cause it to be logged.
        return result

    def finalise(self):
        '''Performs any required clean-up.'''
        self.screenManager.finalise()


class MultiWindowApplication(Application):

    def _makeScreenManager(self, element, size, graphicsOptions, caption):
        self.screenManager = windowManager.WindowManager(self, element, size,
                                                         graphicsOptions, caption)
        self.fonts = self.screenManager.fonts
        self.screenManager.createInterface(element)
