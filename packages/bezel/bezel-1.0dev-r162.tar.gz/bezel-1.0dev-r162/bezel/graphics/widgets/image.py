import logging

from bezel.graphics.widget import Widget

from bezel.resources import load

import pygame
from pygame.transform import rotozoom, rotate
try:
    # New in Pygame 1.8
    from pygame.transform import smoothscale as scale
except ImportError:
    from pygame.transform import scale

class Image(Widget):
    SCALE_NONE, SCALE_ASPECT, SCALE_FIT = xrange(3)

    ALIGN_START, ALIGN_MIDDLE, ALIGN_END = xrange(3)

    def __init__(self, image, scaling=SCALE_ASPECT, x_align=ALIGN_MIDDLE,
                 y_align=ALIGN_MIDDLE, *args, **kwargs):
        if isinstance(image, str):
            image = load(image)

        try:
            self.image = image.convert_alpha()
        except pygame.error:
            logging.warn('Image could not be converted.')
            self.image = image

        self.scaling = scaling
        self.x_align = x_align
        self.y_align = y_align

        self.size = self.image.get_size()
        super(Image, self).__init__(*args, **kwargs)

    def paint(self):
        super(Image, self).paint()

        if self.scaling == Image.SCALE_ASPECT:
            # Scale image whilst keeping the right aspect ratio.
            width, height = self.rect.size
            image_width, image_height = map(float, self.image.get_size())
            zoom = min([width / image_width, height / image_height])

            surface = rotozoom(self.image, -self.rotation, zoom)
        else:
            surface = self.image
            if self.scaling == Image.SCALE_FIT:
                # Scale image to fit entire area.
                surface = scale(surface, *self.rect.size)

            surface = rotate(surface, -self.rotation)

        w1, h1 = self.size
        w2, h2 = surface.get_size()

        adjust_x = (w1 - w2) / 2.0
        adjust_y = (h1 - h2) / 2.0

        w2, h2 = self.rect.size

        if self.x_align == Image.ALIGN_START:
            x = 0
        elif self.x_align == Image.ALIGN_MIDDLE:
            x = (w2 - w1) / 2.0
        elif self.x_align == Image.ALIGN_END:
            x = w2 - w1
        else:
            raise ValueError('Incorrect x alignment: %s.' % self.x_align)

        if self.y_align == Image.ALIGN_START:
            y = 0
        elif self.y_align == Image.ALIGN_MIDDLE:
            y = (h2 - h1) / 2.0
        elif self.y_align == Image.ALIGN_END:
            y = h2 - h1
        else:
            raise ValueError('Incorrect x alignment: %s.' % self.y_align)

        self.surface = pygame.Surface(self.rect.size, 0, surface)
        self.surface.blit(surface, (x + adjust_x, y + adjust_y))
        self.invalidate()

    __rotation = 0
    def set_rotation(self, rotation):
        self.__rotation = rotation % 360
        self.paint()
    def get_rotation(self):
        return self.__rotation
    rotation = property(get_rotation, set_rotation)

