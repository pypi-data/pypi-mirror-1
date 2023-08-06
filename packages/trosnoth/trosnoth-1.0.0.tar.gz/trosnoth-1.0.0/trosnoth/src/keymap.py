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

from trosnoth.src.gui.keyboard import VirtualKeySet

# Define virtual keys and their default bindings.
defaultKeys = (
    # Movement keys.
    ('left', pygame.K_a),
    ('down', pygame.K_s),
    ('right', pygame.K_d),
    ('jump', pygame.K_w),

    # Used in replay mode.
    ('follow', pygame.K_SPACE),

    # Menu keys.
    ('menu', pygame.K_ESCAPE),

    ('buy upgrade', pygame.K_b),
    ('more actions', pygame.K_v),
    ('respawn', pygame.K_r),

    ('turret', pygame.K_F1),
    ('shield', pygame.K_F2),
    ('minimap disruption', pygame.K_F3),
    ('phase shift', pygame.K_F4),
    ('grenade', pygame.K_F5),

    ('use upgrade', pygame.K_q),
    ('add stars', pygame.K_z),
    ('abandon', pygame.K_m),
    ('chat', pygame.K_RETURN),
    ('captain', pygame.K_c),
    ('team ready', pygame.K_y),
    ('leaderboard', pygame.K_p),
    ('zone progress', pygame.K_TAB),
    ('timer', pygame.K_t),
)

default_game_keys = VirtualKeySet(defaultKeys)
