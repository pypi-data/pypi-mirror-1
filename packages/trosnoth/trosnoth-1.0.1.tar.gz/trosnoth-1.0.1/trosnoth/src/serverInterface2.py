# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2007  Joshua Bartlett
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
from time import time

# Try port=6790, command = 'GameMode=Lightning'
def main(serverIP='10.157.86.142', port=None, *params):
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
        n = s.sendto(params, (serverIP, port))

        print '%d bytes sent.' % n
        params = ''
    
def getServerList(multicastPort=5253):
    result = {}

    s = socket(AF_INET, SOCK_DGRAM)
    n = s.sendto('Trosnoth:ServerList?', ('224.0.0.1', multicastPort))

    t = time()
    while time() < t + 5:
        data = s.recv(4096)
        print 'Got:', data

    

#if __name__ == '__main__':
#    main(*sys.argv[1:])
