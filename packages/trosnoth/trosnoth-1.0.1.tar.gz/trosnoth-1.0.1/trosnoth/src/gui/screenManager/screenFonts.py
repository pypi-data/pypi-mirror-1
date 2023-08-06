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

from trosnoth.src.gui.fonts.font import ScaledFont

class ScreenFonts(object):
    default = ScaledFont('FreeSans.ttf', 24)
    defaultTextBoxFont = ScaledFont('FreeSans.ttf', 20)
    unobtrusivePromptFont = ScaledFont('FreeSans.ttf', 28)
    smallTransactionFont = ScaledFont('FreeSans.ttf', 14)
    midTransactionFont = ScaledFont('FreeSans.ttf', 20)
    bigTransactionFont = ScaledFont('FreeSans.ttf', 28)
    chatFont = ScaledFont('FreeSans.ttf', 25)

    hugeMenuFont = ScaledFont('JENKT___.TTF', 90)
    bigMenuFont = ScaledFont('JENKT___.TTF', 60)
    timerFont = ScaledFont('JENKT___.TTF', 53)
    ampleMenuFont = ScaledFont('JENKT___.TTF', 50)
    mediumMenuFont = ScaledFont('JENKT___.TTF', 45)
    menuFont = ScaledFont('JENKT___.TTF', 40)
    ingameMenuFont = ScaledFont('JENKT___.TTF', 20)
    titleFont = ScaledFont('JENKT___.TTF', 108)
    versionFont = ScaledFont('JENKT___.TTF', 30)
    scrollingButtonsFont = ScaledFont('JENKT___.TTF', 30)
                           
    messageFont = ScaledFont('KLEPTOCR.TTF', 20)
    
    smallNoteFont = ScaledFont('KLEPTOCR.TTF', 30)
    labelFont = ScaledFont('KLEPTOCR.TTF', 40)
    captionFont = ScaledFont('KLEPTOCR.TTF', 50)
    keymapFont = ScaledFont('KLEPTOCR.TTF', 35)

    creditsFont = ScaledFont('KLEPTOCR.TTF', 30)
    creditsH2 = ScaledFont('KLEPTOCR.TTF', 48)
    creditsH1 = ScaledFont('KLEPTOCR.TTF', 60)
    
del ScaledFont
