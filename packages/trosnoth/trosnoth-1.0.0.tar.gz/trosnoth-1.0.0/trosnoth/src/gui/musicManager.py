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
import twisted

import trosnoth.data.music as music
from trosnoth.data import getPath

class MusicManager(object):
    '''Manages the music.'''

    def __init__(self):
        pygame.mixer.init()

    def playMusic(self):
        pygame.mixer.music.load(getPath(music, 'wrongdirection.ogg'))
        pygame.mixer.music.play(-1)

    def stopMusic(self):
        pygame.mixer.music.stop()

    def isMusicPlaying(self):
        return pygame.mixer.music.get_busy()
        
