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

import pickle
import os
import base64
import time

from twisted.internet import task

from trosnoth.src.network.setup import ReadyForDynamicDetailsMsg
from trosnoth.src import serverUniverse, serverLayout
from trosnoth.src.model.universe_base import GameState
from trosnoth.src.utils.unrepr import unrepr
from trosnoth.src.utils.utils import timeNow
from trosnoth.src.utils import logging

from trosnoth.src.utils.jsonImport import json
from trosnoth.src.utils.components import Component, handler, Plug
from trosnoth.src.network.networkServer import serverMsgs
from trosnoth.src.network.networkClient import Client, clientMsgs
from trosnoth.src.messages.connection import *

from trosnoth.data import getPath, user, makeDirs

def makeClient(app, filename):
    '''
    Sets up a replay client and game and connects them together.
    Returns the Client object.
    '''
    server = ReplayGame(filename)
    client = Client(app)

    client.gamePlug.connectPlug(server.plug)
    server.start()

    # TODO: The following line is a hack.
    client.world.replay = True

    return client

class ReplayGame(Component):

    plug = Plug()

    def __init__(self, fileName):
        Component.__init__(self)

        replayPath = getPath(user, 'savedGames')
        makeDirs(replayPath)

        self.replayFile = open(os.path.join(replayPath, fileName), 'r')

        fileInfo = self.replayFile.readline().split(',')

        encodedLines = []

        for lineCount in range(1, int(fileInfo[1]) + 1):
            encodedLines.append(self.replayFile.readline())

        self.replayInfo = json.loads(''.join(encodedLines))
        self.replayInfo['connectionString']['layoutDefs'] = unrepr(self.replayInfo['connectionString']['layoutDefs'])
        self.replayInfo['connectionString']['worldMap'] = unrepr(self.replayInfo['connectionString']['worldMap'])
        
        self.settings = self.replayInfo['serverSettings']
        self._start = float(self.replayInfo['unixTimestamp'])

        # How this is structured:
        # replayTimes is an ordered list of timestamps.
        # replayData is a dictionary: the keys are the timestamps
        # and the values are a list of packets that need to be sent
        # at that time.

        self.replayTimes = []
        self.replayData = {}

        # How many lines should be read at a time?
        self.linesAtATime = 500
        self.totalLinesRead = 0
        self.totalLinesPlayedBack = 0
        self.keepReading = True

        for lineNumber in range(1, self.linesAtATime):
            line = self.replayFile.readline()
            self.totalLinesRead += 1

            if line.strip() == '':
                self.keepReading = False
                break
            
            if line.startswith('ReplayData: '):
                discard, timestamp, protocol, packet = line.split(' ', 3)
                timestamp = float(timestamp) - self._start
                if timestamp not in self.replayTimes:
                    self.replayTimes.append(timestamp)
                    self.replayData[timestamp] = []
                self.replayData[timestamp].append(base64.b64decode(packet))

        # Up to [x] lines will be read by this point, but there still might be more!

        self.running = False


    def start(self):
        self.plug.send(GotSettings(self.getClientSettings()))

        self.startTime = timeNow()
        self.replayPlayback = task.LoopingCall(self.tick)
        self.replayPlayback.start(0, False)

        if self.keepReading:
            self.replayReading = task.LoopingCall(self.readSomeMore)
            self.replayReading.start(10, False)

        self.running = True

    def sendMessage(self, msg):
        print 'Replay: got request to send message to server: %s' % (msg,)
    # sendMessage must be a handler for everything that networkServer can
    # receive.
    for _msg in serverMsgs:
        sendMessage = handler(_msg)(sendMessage)
    del _msg        

    def readSomeMore(self):
        try:
            self._readSomeMore()
        except:
            logging.writeException()

    def _readSomeMore(self):
        for lineNumber in range(0, self.linesAtATime):
            line = self.replayFile.readline()
            self.totalLinesRead += 1
            if line.strip() == '':
                self.keepReading = False
                self.replayReading.stop()
                break
            if line.startswith('ReplayData: '):
                discard, timestamp, protocol, packet = line.split(' ', 3)
                timestamp = float(timestamp) - self._start
                if timestamp not in self.replayTimes:
                    self.replayTimes.append(timestamp)
                    self.replayData[timestamp] = []
                self.replayData[timestamp].append(base64.b64decode(packet))
        print '%d lines now read' % self.totalLinesRead
        print '%d lines now played back' % self.totalLinesPlayedBack

    def tick(self):
        try:
            self._tick()
        except:
            logging.writeException()

    def _tick(self):
        curTime = timeNow() - self.startTime
        if len(self.replayTimes) > 0:
            while self.replayTimes[0] < curTime:
                timestamp = self.replayTimes[0]
                for packet in self.replayData[timestamp]:
                    self.totalLinesPlayedBack += 1
                    if packet[-1] == '\n':
                        packet = packet[:-1]
                    msg = clientMsgs.buildMessage(packet)
                    self.plug.send(msg)

                del self.replayTimes[0]
                if len(self.replayTimes) == 0:
                    self.replayPlayback.stop()
                    print 'GAME OVER MAN, GAME OVER'
                    print '%d LINES READ' % self.totalLinesRead
                    print '%d LINES PLAYED BACK' % self.totalLinesPlayedBack
                    self.shutdown()
                    break

    def stop(self):
        self.replayPlayback.stop()
        self.replayReading.stop()
        
    def getClientSettings(self):
        '''Returns a string representing the settings which must be sent to
        clients that connect to this server.'''

        return self.replayInfo['connectionString']

    def shutdown(self):
        print 'Replay Server: SHUTTING DOWN'

        # Fixes an odd bug in which a single extra packet gets broadcast
        # after closing a replay
        self.replayTimes = []

        # Kill server
        self.running = False

