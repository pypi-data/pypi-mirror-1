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

'''serverLayout.py - loads the database of layout blocks without needing
any graphics.  Used by the server.  This should keep as much information
about the map layout as needed to check that all clients have the same
map layout.'''

import os, random

from trosnoth.src.utils.utils import new, hasher

from trosnoth.src.serverUniverse import ForwardInterfaceMapBlock, BackwardInterfaceMapBlock, \
                 TopBodyMapBlock, BottomBodyMapBlock

from trosnoth.src.serverUniverse import RoofObstacle, GroundObstacle, VerticalWall
from trosnoth.data import getPath
import trosnoth.data.blocks as blocks

# Namespace for interpreting block layout files.
blockFileNamespace = {'ForwardInterfaceMapBlock': ForwardInterfaceMapBlock,
                      'BackwardInterfaceMapBlock': BackwardInterfaceMapBlock,
                      'TopBodyMapBlock': TopBodyMapBlock,
                      'BottomBodyMapBlock': BottomBodyMapBlock}

class LayoutDatabase(object):
    '''Represents a database which stores information on block layouts.'''
    
    def __init__(self, path=getPath(blocks)):
        '''(path) - initialises the database and loads the blocks from the
        specified path.  path should be a sequence of strings which will
        be joined using os.path.join().'''

        # Set up database.
        self.layouts = {}
        self.layoutsByFilename = {}
        self.symmetricalLayouts = {}
        for b in True, False:
            for a in ForwardInterfaceMapBlock, BackwardInterfaceMapBlock, \
                     TopBodyMapBlock, BottomBodyMapBlock:
                self.layouts[a, b] = []
            for a in TopBodyMapBlock, BottomBodyMapBlock:
                self.symmetricalLayouts[a, b] = []

        # Read map blocks from files.
        self.path = path
        filenames = os.listdir(path)

        # Go through all files in the blocks directory.
        for fn in filenames:
            # Check for files with a .block extension.
            if os.path.splitext(fn)[1] == '.block':
                # Remember the filename.
                self.filename = fn
                
                # Read the file and create the block
                f = open(os.path.join(self.path, fn), 'rU')
                try:
                    contents = f.read()
                finally:
                    f.close()

                self.checksum = hasher(contents).hexdigest()

                try:
                    code = compile('addLayout(%s)' % contents, \
                                   fn, 'exec')
                except SyntaxError:
                    raise SyntaxError, 'invalid file format: %s' % \
                          os.path.join(self.path, fn)

                namespace = blockFileNamespace.copy()
                namespace.update({'addLayout': self.addLayout})
                exec code in namespace

    def addLayout(self, blockType=TopBodyMapBlock, blocked=False, \
                  graphic=None, obstacles=[], platforms=[], symmetrical=False):
        '''(blockType, blocked, graphic, obstacles, symmetrical)
        Registers a layout with the given parameters. The graphic is loaded
        at the time that addLayout() is called.'''

        # Create the layout.
        if graphic == None:
            graphicPath = None
        else:
            graphicPath = os.path.join(self.path, graphic)
            
        newLayout = BlockLayout(self.filename, graphicPath, symmetrical, \
                                self.checksum)

        # Add the layout to the database.
        self.layouts[blockType, blocked].append(newLayout)
        self.layoutsByFilename[self.filename] = newLayout
        if symmetrical:
            self.symmetricalLayouts[blockType, blocked].append(newLayout)
        else:
            if blockType == ForwardInterfaceMapBlock:
                blockType = BackwardInterfaceMapBlock
            elif blockType == BackwardInterfaceMapBlock:
                blockType = ForwardInterfaceMapBlock
                
            self.layouts[blockType, blocked].append(newLayout.mirrorLayout)

    def randomiseBlock(self, block):
        '''Takes a map block (see universe.py) and gives it and the
        corresponding opposite block a layout depending on its block type
        and whether it has a barrier.'''

        oppBlock = block.oppositeBlock
        if oppBlock:
            # The block is not symmetrical.
            layout = random.choice(self.layouts[type(block), block.blocked])
            layout.applyTo(block)
            layout.mirrorLayout.applyTo(oppBlock)
        else:
            # The block is symmetrical.
            layout = random.choice(self.symmetricalLayouts[type(block), \
                                                    block.blocked])
            layout.applyTo(block)

    def getLayout(self, filename, checksum):
        result = self.layoutsByFilename[filename]

        if result.checksum != checksum:
            raise ValueError, 'Layout checksum doesn\'t match.'

        return result

class BlockLayout(object):
    '''Represents the layout of a block. Saves the positions of all obstacles
    within the block as well as a graphic of the block.'''

    def __init__(self, filename, graphicPath, symmetrical, checksum, \
                 reverse=False):
        '''() - initialises a blank block layout.'''
        self.filename = filename
        self.graphicPath = graphicPath
        self.reverse = reverse
        self.symmetrical = symmetrical
        self.checksum = checksum
        self.forwardLayout = self

        if not reverse:
            # Check the graphic.
            if graphicPath:
                # Check that the graphic exists.
                if not os.path.exists(graphicPath):
                    raise IOError, 'Graphic file does not exist: %s' % graphicPath

            # If it's not symmetrical, create a mirror block.
            if symmetrical:
                self.mirrorLayout = self
            else:
                self.mirrorLayout = BlockLayout(self.filename, graphicPath, \
                                                False, self.checksum, True)
                self.mirrorLayout.mirrorLayout = self
                self.mirrorLayout.forwardLayout = self
                
    def applyTo(self, block):
        '''Applies this layout to the specified map block.'''
        block.layout = self
