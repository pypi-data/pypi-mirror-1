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

defaultAnchor = 'topleft'

def uniqueColour(colours):
    '''Returns a greyish colour that is not in the given list of colour
    triples. Useful for colourkeying.'''
    result = [0, 0, 0]
    i = 0
    while True:
        result[i] += 1
        rTuple = tuple(result)
        for colour in colours:
            if colour == rTuple:
                break
        else:
            return rTuple
        i = (i + 1) % 3

def addPositions(p1, p2):
    return tuple([p1[i] + p2[i] for i in 0,1])

def _getScaledSize(app, size):
    return app.screenManager.scale(size)

class ScaledPoint(object):
    def __init__(self, x, y):
        self.val = (x, y)
    def getPoint(self, app):
        return app.screenManager.placePoint(self.val)
    def __repr__(self):
        return "Scaled Point (%d, %d)" % self.val

class FullScreenAttachedPoint(object):
    def __init__(self, distance, attachedAt = 'topleft'):
        self.val = distance
        self.attachedAt = attachedAt

    def getPoint(self, app):
        if hasattr(self.val, 'getSize'):
            val = self.val.getSize(app)
        else:
            val = self.val
        pos = getattr(app.screenManager.rect, self.attachedAt)
        return addPositions(pos, val)

class ScaledScreenAttachedPoint(object):
    def __init__(self, distance, attachedAt = 'topleft'):
        self.val = distance
        self.attachedAt = attachedAt

    def getPoint(self, app):
        if hasattr(self.val, 'getSize'):
            val = self.val.getSize(app)
        else:
            val = self.val
        pos = getattr(app.screenManager.scaledRect, self.attachedAt)
        return addPositions(pos, val)    

# @param attachedTo_Rect should be a reference to a function which
# returns a pygame.Rect
class AttachedPoint(object):
    def __init__(self, val, attachedTo_Rect, attachedAt = 'topleft'):
        self.val = val
        self.attachedAt = attachedAt
        self.attachedTo_Rect = attachedTo_Rect

    def getPoint(self, app):
        pos = getattr(self.attachedTo_Rect(), self.attachedAt)
        if hasattr(self.val, 'getSize'):
            val = self.val.getSize(app)
        else:
            val = self.val
        return addPositions(pos, val)

class ScaledSize(object):
    def __init__(self, x, y):
        self.val = (x, y)
    def getSize(self, app):
        return _getScaledSize(app, self.val)
    def __repr__(self):
        return "Scaled Size (%d, %d)" % self.val

class FullScreenSize(object):
    def getSize(self, app):
        return app.screenManager.size
    def __repr__(self):
        return "Full Screen Size"

class ScaledScreenSize(object):
    def getSize(self, app):
        return app.screenManager.scaledSize
    def __repr__(self):
        return "Scaled Screen Size"

# An image loaded from file
class NewImage(object):
    def __init__(self, nameOrImage, colourkey=True):
        if isinstance(nameOrImage, str):
            self.name = nameOrImage
            self.image = None
        else:
            assert isinstance(nameOrImage, pygame.Surface)
            self.image = nameOrImage
        self.colourkey = colourkey
    def getImage(self, app):
        if self.image is not None:
            return self.image
        self.image = pygame.image.load(self.name).convert()
        if self.colourkey:
            self.image.set_colorkey(self.image.get_at((0,0)))
        return self.image

    def getSize(self, app):
        return self.getImage(app).get_size()


class SizedImage(NewImage):
    def __init__(self, nameOrImage, size, colourkey=True):
        super(SizedImage, self).__init__(nameOrImage, colourkey)
        self.sizedImage = None
        # Keep a record of whether the size of the screen changes
        self.lastSize = None
        self.size = size

    def getImage(self, app):
        if self.sizedImage is not None and self.lastSize == self._getCurrentSize(app):
            return self.sizedImage
        img = super(SizedImage, self).getImage(app)
        self.lastSize = self._getCurrentSize(app)
        self.sizedImage = pygame.transform.scale(img, self.lastSize)
        return self.sizedImage

    def _getCurrentSize(self, app):
        if hasattr(self.size, 'getSize'):
            return self.size.getSize(app)
        else:
            return self.size


class TextImage(NewImage):
    '''Shows text at a specified screen location.'''
    
    def __init__(self, text, font, colour=(0,128,0), bgColour=None):
        self.colour = colour
        self.bgColour = bgColour
        self.text = text
        self.font = font

    def getImage(self, app):
        return self.font.render(app, self.text, False, self.colour, self.bgColour)
 

class Location(object):
    '''
    @param  point   the point that this location is attached to
    @param  anchor  a string representing the rectangle attribute which this
                    location will reposition
    '''
    def __init__(self, point, anchor=defaultAnchor):            
        if anchor == 'centre':
            anchor = 'center'
        self.point = point
        self.anchor = anchor

    def __repr__(self):
        return "Location: %s anchored at %s" % (repr(self.point), self.anchor)
    def apply(self, app, rect):
        '''Moves the rect so that it is anchored according to this anchor.'''
        point = self.point
        if hasattr(point, 'getPoint'):
            point = point.getPoint(app)
        setattr(rect, self.anchor, point)

# Location relative to another location
# @param size Can be a tuple or a ScaledPoint
class RelativeLocation(Location):
    def __init__(self, location, size):
        self.size = size
        self.location = location

    def __repr__(self):
        return "RelativeLocation: (%s plus %s)" % (repr(self.location), repr(self.size))
        
    def apply(self, app, rect):
        self.location.apply(app, rect)
        if hasattr(self.size, 'getSize'):
            diff = self.size.getSize(app)
        else:
            diff = self.size
        rect.topleft = addPositions(diff, rect.topleft)

class Area(Location):
    '''
    @param  point   the point that this area is attached to
    @param  size    the size of this area
    @param  anchor  a string representing which of the rectangle's attributes
                    the point will be attached to
    '''
    def __init__(self, point, size, anchor=defaultAnchor):
        self.point = point
        self.size = size
        self.anchor = anchor
    def apply(self, app, rect):
        '''Moves and resizes this rect so that it covers this area.'''
        if hasattr(self.size, 'getSize'):
            rect.size = self.size.getSize(app)
        else:
            rect.size = self.size
        Location.apply(self, app, rect)

    def getRect(self, app):
        result = pygame.Rect(0,0,0,0)
        self.apply(app, result)
        return result

    def __repr__(self):
        return "Area: point is %s, size is %s, anchored at %s" % (repr(self.point), repr(self.size), self.anchor)


class PygameEvent(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

def translateEvent(event, amount):
    result = PygameEvent(type=event.type, pos=(event.pos[0] - amount[0],
                                         event.pos[1] - amount[1]))
    for name in ['button', 'buttons']:
        try:
            v = getattr(event, name)
        except AttributeError:
            pass
        else:
            setattr(result, name, v)
    return result

# For ease of use    
def ScaledLocation(x, y, anchor = defaultAnchor):
    return Location(ScaledPoint(x, y), anchor)

def ScaledArea(x, y, width, height, anchor = defaultAnchor):
    return Area(ScaledPoint(x, y), ScaledSize(width, height), anchor)

def ScaledImage(name, colourkey=True):
    return FunctionOfSize_Image(name, _getScaledSize, colourkey)
