from bezel.graphics.widget import Widget

from bezel.misc import InheritProperty

import pygame
from pygame.font import Font

class Text(Widget):
    """A widget which draws text onto the screen."""
    ALIGN_START, ALIGN_MIDDLE, ALIGNMENT_END = xrange(3)

    def __init__(self, text, font_name=None, font_size=24,
                 colour=(255, 255, 255), x_align=ALIGN_START,
                 y_align=ALIGN_MIDDLE, *args, **kwargs):
        super(Text, self).__init__(*args, **kwargs)

        self.x_align = x_align
        self.y_align = y_align

        self.__text = text
        self.__colour = colour
        self.font = (font_name, font_size)

        rendered = self._font.render(self.text, True, self.colour)
        self.size = rendered.get_size()

    def paint(self):
        """Renders the text onto the given surface at the correct alignment."""
        super(Text, self).paint()
        text_surface = self._font.render(self.text, True, self.colour)

        total_width, total_height = self.rect.size
        text_width, text_height = text_surface.get_size()

        if self.x_align == Text.ALIGN_START:
            x = 0
        elif self.x_align == Text.ALIGN_MIDDLE:
            x = (total_width - text_width) / 2.0
        elif self.x_align == Text.ALIGN_END:
            x = total_width - text_width

        if self.y_align == Text.ALIGN_START:
            y = 0
        elif self.y_align == Text.ALIGN_MIDDLE:
            y = (total_height - text_height) / 2.0
        elif self.y_align == Text.ALIGN_END:
            y = (total_height - text_height) / 2.0

        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.surface.blit(text_surface, (x, y))
        self.invalidate()

    # Text property.
    __text = ''
    def get_text(self):
        return self.__text
    def set_text(self, text):
        self.__text = text
        self.paint()
    text = InheritProperty(get_text, set_text)

    # Colour property.
    __colour = (255, 255, 255)
    def get_colour(self):
        return self.__colour
    get_color = get_colour
    def set_colour(self, colour):
        self.__colour = colour
        self.paint()
    set_color = set_colour
    colour = InheritProperty(get_colour, set_colour)
    color = colour

    # Font properties.
    _font = Font(None, 14)
    __font_name = None
    __font_size = 14

    def get_font_name(self):
        return self.__font_name
    def set_font_name(self, font_name):
        self.__font_name = font_name
        self.font = (self.__font_name, self.__font_size)
    font_name = InheritProperty(get_font_name, set_font_name)

    def get_font_size(self):
        return self.__font_size
    def set_font_size(self, font_size):
        self.__font_size = font_size
        self.font = (self.__font_name, self.__font_size)
    font_size = InheritProperty(get_font_size, set_font_size)

    def get_font(self):
        return (self.__font_name, self.__font_size)
    def set_font(self, (font_name, font_size)):
        self.__font_name = font_name
        self.__font_size = font_size
        self._font = Font(self.__font_name, self.__font_size)
        self.paint()
    font = InheritProperty(get_font, set_font)

