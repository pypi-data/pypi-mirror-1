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

'''mapLayout.py - takes care of initialising map blocks with obstacles and
 images.'''

import os, random
import sys

from trosnoth.src.utils.utils import hasher

from trosnoth.src.universe import ForwardInterfaceMapBlock, BackwardInterfaceMapBlock, \
                 TopBodyMapBlock, BottomBodyMapBlock

from trosnoth.src.universe import RoofObstacle, GroundObstacle, VerticalWall

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
        filenames = os.listdir(self.path)

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

                code = compile('addLayout(%s)' % contents,
                               fn, 'exec')

                namespace = blockFileNamespace.copy()
                namespace.update({'addLayout': self.addLayout})
                exec code in namespace

    def addLayout(self, blockType=TopBodyMapBlock, blocked=False, \
                  graphic=None, obstacles=[], platforms=[], symmetrical=False):
        '''(blockType, blocked, graphic, obstacles, symmetrical)
        Registers a layout with the given parameters.'''

        # Create the layout.
        if graphic == None:
            graphicPath = None
        else:
            graphicPath = os.path.join(self.path, graphic)
            
        newLayout = BlockLayout()
        newLayout.setProperties(graphicPath, obstacles, platforms, \
                                symmetrical, self.checksum)

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

#    def randomiseBlock(self, block):
#        '''Takes a map block (see universe.py) and gives it and the
#        corresponding opposite block a layout depending on its block type
#        and whether it has a barrier.
#
#        NOTE: This is only used server-side.'''
#
#        oppBlock = block.oppositeBlock
#        if oppBlock:
#            # The block is not symmetrical.
#            layout = random.choice(self.layouts[type(block), block.blocked])
#            layout.applyTo(block)
#            layout.mirrorLayout.applyTo(oppBlock)
#        else:
#            # The block is symmetrical.
#            layout = random.choice(self.symmetricalLayouts[type(block), \
#                                                    block.blocked])
#            layout.applyTo(block)

    def getLayout(self, filename, checksum):
        result = self.layoutsByFilename[filename]

        if result.checksum != checksum:
            raise ValueError, 'Layout checksum doesn\'t match.'

        return result
    
class BlockLayout(object):
    '''Represents the layout of a block. Saves the positions of all obstacles
    within the block as well as a graphic of the block.'''

    def __init__(self):
        '''() - initialises a blank block layout.'''
        self.graphics = None
        self.obstacles = []
        self.platforms = []
        self.mirrorLayout = self
        self.reversed = False
  
    def setProperties(self, graphicPath, obstacles, platforms, symmetrical, \
                      checksum):
        '''(graphicPath, obstacles, symmetrical) - sets the properties of
        this block layout.
        
        graphicPath     A string representing the path to the graphic file
                        which describes the background of this block, or
                        None if no graphic file should be used.
        obstacles       Should be a sequence of obstacle definitions, each of
                        which should be of the form ((x1, y1), (dx, dy)).
                        Obstacles can be passed through in one direction only.
                        A solid block should be composed of obstacles defined
                        in a clockwise direction.
        platforms       Obstacles which can be fallen through.
        symmetrical     Boolean - is this block symmetrical? If set to True,
                        this block will also create a block which is the exact
                        mirror of this block.
        '''
        self.checksum = checksum
        
        # Set up the graphic.
        if graphicPath:
            # Check that the graphic exists.
            if not os.path.exists(graphicPath):
                raise IOError, 'Graphic file does not exist: %s' % graphicPath
        self.graphics = BlockGraphics(graphicPath)

        # Record obstacles.
        self.obstacles = []
        for obstacle in obstacles:
            self.obstacles.append(obstacle)

        self.platforms = []
        for platform in platforms:
            self.platforms.append(tuple(platform))

        # If it's not symmetrical, create a mirror block.
        if symmetrical:
            self.mirrorLayout = self
        else:
            self.mirrorLayout = BlockLayout()
            self.mirrorLayout.reversed = True
            self.mirrorLayout.mirrorLayout = self
            self.mirrorLayout.checksum = checksum
            self.mirrorLayout.graphics = BlockGraphics(graphicPath, True)

            # Flip the obstacles.
            for obstacle in self.obstacles:
                mObstacle = []
                for (x, y) in obstacle:
                    mObstacle.insert(0, (-x, y))
                self.mirrorLayout.obstacles.append(tuple(mObstacle))
            for platform in self.platforms:
                x1, y1 = platform[0]
                dx = platform[1]
                x2 = x1 + dx
                self.mirrorLayout.platforms.append(((-x2, y1), dx))
                
    def applyTo(self, block):
        '''Applies this layout to the specified map block.'''

        # Go through the obstacles and append them to the block's obstacles.
        for obstacle in self.obstacles:
            block.addObstacle(obstacle, self.reversed)

        for relPos, dx in self.platforms:
            block.addPlatform(relPos, dx, self.reversed)

        block.defn.graphics = self.graphics

class BlockGraphics(object):
    '''Defers loading of graphic until needed.'''

    def __init__(self, filename, reversed=False):
        self._filename = filename
        self._graphic = None
        self._miniGraphics = {}
        self._reversed = reversed

    def _getGraphic(self):
        if self._graphic is not None:
            return self._graphic

        # Load the graphic.
        import pygame

        self._graphic = pygame.image.load(self._filename).convert()
        self._graphic.set_colorkey((255, 255, 255))

        if self._reversed:
            # Flip the graphic.
            self._graphic = \
                    pygame.transform.flip(self._graphic, True, False)
        return self._graphic
    
    def getMini(self, scale):
        try:
            result = self._miniGraphics[scale]
        except KeyError:
            width = self.graphic.get_rect().width / scale
            height = self.graphic.get_rect().height / scale

            # TODO: Perhaps put some time-limit on this cache in case
            # someone asks for many many different scales.

            import pygame
            result = pygame.transform.scale(self.graphic, (width, height))
            self._miniGraphics[scale] = result

        return result

    filename = property(lambda: self._filename)
    reversed = property(lambda: self._reversed)
    graphic = property(_getGraphic)
