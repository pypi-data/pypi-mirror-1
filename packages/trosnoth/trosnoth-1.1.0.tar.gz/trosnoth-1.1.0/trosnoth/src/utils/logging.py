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
import os
import traceback

from trosnoth.data import getPath, user, makeDirs

def startLogging():
    'initialises the debug module.'
    global logFile
    global oldOut
    global oldErr

    makeDirs(getPath(user, 'logs'))

    i = 0
    while True:
        fname = 'log%03d.txt' % i
        fname = getPath(user, 'logs', fname)
        if not os.path.exists(fname):
            break
        i += 1

    logFile = file(fname, 'w')
    oldOut, oldErr = sys.stdout, sys.stderr
    sys.stdout = MultipleWriter(oldOut, logFile)
    sys.stderr = MultipleWriter(oldErr, logFile)

def endLogging():
    logFile.flush()
    logFile.close()
    sys.stdout = oldOut
    sys.stderr = oldErr

class MultipleWriter(object):
    def __init__(self, *streams):
        self.streams = streams
        
    def write(self, thing):
        for stream in self.streams:
            print >> stream, thing
        

def writeException():
    print >> sys.stderr
    tb = sys.exc_info()[2]
    print >> sys.stderr, 'Exception caught in file %r, line %d, in %s' % (tb.tb_frame.f_code.co_filename, tb.tb_frame.f_lineno, tb.tb_frame.f_code.co_name)
    traceback.print_exc()
