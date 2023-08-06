# Trosnoth (UberTweak Platform Game))
# Copyright (C)) 2006-2009 Joshua D Bartlett
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

from trosnoth.src.gui.fonts.font import ScaledFont
def initFonts(fontList):
    fontList.addFont('default', ScaledFont('FreeSans.ttf', 24))
    fontList.addFont('defaultTextBoxFont', ScaledFont('FreeSans.ttf', 20))
    fontList.addFont('unobtrusivePromptFont', ScaledFont('FreeSans.ttf', 28))
    fontList.addFont('smallTransactionFont', ScaledFont('FreeSans.ttf', 14))
    fontList.addFont('midTransactionFont', ScaledFont('FreeSans.ttf', 20))
    fontList.addFont('bigTransactionFont', ScaledFont('FreeSans.ttf', 28))
    fontList.addFont('chatFont', ScaledFont('FreeSans.ttf', 25))

    fontList.addFont('titleFont', ScaledFont('JENKT___.TTF', 108))

    fontList.addFont('hugeMenuFont', ScaledFont('FreeSans.ttf', 54))
    fontList.addFont('bigMenuFont', ScaledFont('FreeSans.ttf', 36))
    fontList.addFont('serverListFont', ScaledFont('FreeSans.ttf', 24))
    fontList.addFont('timerFont', ScaledFont('FreeSans.ttf', 32))
    fontList.addFont('ampleMenuFont', ScaledFont('FreeSans.ttf', 40))
    fontList.addFont('mediumMenuFont', ScaledFont('FreeSans.ttf', 36))
    fontList.addFont('menuFont', ScaledFont('FreeSans.ttf', 30))
    fontList.addFont('ingameMenuFont', ScaledFont('FreeSans.ttf', 12))
    fontList.addFont('versionFont', ScaledFont('FreeSans.ttf', 16))
    fontList.addFont('scrollingButtonsFont', ScaledFont('FreeSans.ttf', 24))
    fontList.addFont('zoneBarFont', ScaledFont('FreeSans.ttf', 24))
                           
    fontList.addFont('messageFont', ScaledFont('FreeSans.ttf', 20))
    fontList.addFont('leaderboardFont', ScaledFont('KLEPTOCR.TTF', 21))
    
    fontList.addFont('smallNoteFont', ScaledFont('FreeSans.ttf', 22))
    fontList.addFont('labelFont', ScaledFont('FreeSans.ttf', 32))
    fontList.addFont('captionFont', ScaledFont('FreeSans.ttf', 35))
    fontList.addFont('keymapFont', ScaledFont('FreeSans.ttf', 24))
    fontList.addFont('keymapInputFont', ScaledFont('FreeSans.ttf', 20))

    fontList.addFont('connectionFailedFont', ScaledFont('FreeSans.ttf', 32))

    fontList.addFont('creditsFont', ScaledFont('FreeSans.ttf', 24))
    fontList.addFont('creditsH2', ScaledFont('KLEPTOCR.TTF', 48))
    fontList.addFont('creditsH1', ScaledFont('KLEPTOCR.TTF', 60))

def initMusic(musicManager):
    for fn in 'wrongdirection.ogg', 'track1.ogg', 'track2.ogg':
        musicManager.addMusicFile(fn)

def initSound(soundPlayer):
    # TODO: actual sounds
    #soundPlayer.addSound('tag.ogg', 'tag', 1)
    #soundPlayer.addSound('shoot.ogg', 'shoot', 8)
    pass
