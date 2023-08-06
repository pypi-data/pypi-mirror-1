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

import sys
from socket import *

# Try port=6790, command = 'GameMode=Lightning'
# Also, try:
#   Outcome=blue
#   Outcome=red
#   Outcome=draw
#	NoCaptains
#   StartGame
def main(port=None, *params):
    if port == None:
        port = input('Enter port number: ')
    while True:
        params = ' '.join(params)
        if params == '':
            params = raw_input('Enter command: ')
        if params == 'exit':
            break

        print 'Sending command: ' + params

        # Create the socket.
        s = socket(AF_INET, SOCK_DGRAM)
        n = s.sendto(params, ('127.0.0.1', port))

        print '%d bytes sent.' % n
        params = ''
    

if __name__ == '__main__':
    # Best bet is to use no arguments as use with arguments has not been debugged.
    main(*sys.argv[1:])
