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

from trosnoth.src.gui.app import Application
from trosnoth.src.gui.framework import framework, elements, scrollableCanvas
from trosnoth.src.gui.common import Location
from trosnoth.src.gui.fonts.font import Font
import pygame

class Interface(framework.CompoundElement):
    def __init__(self, app):
        super(Interface, self).__init__(app)
        backdrop = pygame.image.load('Awesome Leaders.jpg').convert()
        size = backdrop.get_size()
        sc1 = scrollableCanvas.ScrollableCanvas(app, (20,20), size, (200,200))
        sc2 = scrollableCanvas.ScrollableCanvas(app, (230,20), size, (200,size[1]+scrollableCanvas.ScrollableCanvas.ScrollBar.defaultWidth))
        sc3 = scrollableCanvas.ScrollableCanvas(app, (440,20), size, size)
        sc4 = scrollableCanvas.ScrollableCanvas(app, (20,530), size, (size[0]+scrollableCanvas.ScrollableCanvas.ScrollBar.defaultWidth, 200))
        try:
            sc5 = scrollableCanvas.ScrollableCanvas(app, (20,530), size, (size[0]+scrollableCanvas.ScrollableCanvas.ScrollBar.defaultWidth, size[1]))
        except AssertionError, e:
            print "As expected, assertion error thrown: %s" % e
        else:
            assert False, "This should have raised an exception"
        self.elements = [sc1, sc2, sc3, sc4]
        font = Font("KLEPTOCR.TTF", 30)
        for sc in self.elements:
            sc.elements = [elements.PictureElement(app, backdrop, Location((0,0), 'topleft')),
                           elements.TextButton(app, Location((20,20)), "Hello", font, (0,128,0), (0,0,128))]

size = (1200,775)

if __name__ == "__main__":
    a = Application(size, 0, "Testing", Interface)
    a.run()
