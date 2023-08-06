import pygame

from bezel.misc import InheritProperty

class Widget(object):
    """
    A widget is the base unit of graphics - all other
    graphical objects subclass Widget.

    A widget has a position and size, and a surface.
    """
    def __init__(self, *args, **kwargs):
        super(Widget, self).__init__(*args, **kwargs)

        self.surface = None

        self.rect = pygame.Rect(0, 0, 0, 0)

        self.mouse_grabbed = False
        self.mouse_inside = False

    # Event dispatcher.
    def _pump(self, events):
        for event in events:
            # Keyboard events.
            if event.type == pygame.KEYDOWN:
                # Send key_down event.
                self.key_down(event.key, event.unicode, event.mod)
            elif event.type == pygame.KEYUP:
                # Send key_down event.
                try:
                    char = chr(event.key)
                except ValueError:
                    char = ''
                self.key_up(event.key, char, event.mod)

            # Mouse events.
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Send mouse_down event.
                x, y = event.pos
                if self.rect.collidepoint(x, y):
                    x -= self.rect.x
                    y -= self.rect.y
                    self.mouse_down(x, y, event.button)
                self.mouse_grabbed = True
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if self.mouse_inside or self.mouse_grabbed or \
                   self.rect.collidepoint(x, y):
                    x -= self.rect.x
                    y -= self.rect.y
                    self.mouse_move(x, y, event.buttons)
            elif event.type == pygame.MOUSEBUTTONUP:
                # Send mouse_up event.
                x, y = event.pos
                if self.mouse_grabbed or self.rect.collidepoint(x, y):
                    x -= self.rect.x
                    y -= self.rect.y
                    self.mouse_up(x, y, event.button)
                self.mouse_grabbed = False

    # Keyboard events.
    def key_down(self, key, char, mod):
        pass

    def key_up(self, key, char, mod):
        pass

    # Mouse events.
    def mouse_down(self, x, y, button):
        pass

    def mouse_up(self, x, y, button):
        pass

    def mouse_move(self, x, y, buttons):
        width, height = self.size
        if x >= 0 and y >= 0 and x < width and y < height:
            # Inside the widget.
            if not self.mouse_inside:
                self.mouse_inside = True
                self.mouse_enter(x, y, buttons)
        else:
            # Outside the widget.
            if self.mouse_inside:
                self.mouse_inside = False
                self.mouse_leave(x, y, buttons)

    def mouse_enter(self, x, y, buttons):
        pass

    def mouse_leave(self, x, y, buttons):
        pass

    started = False
    # Drawing methods.
    def paint(self):
        """Paint the sprite onto self.surface."""
        pass

    def draw(self, surface, dirty):
        """Draws self.surface onto the surface.
        
        Note: If overriding, this method should be
        as optimised as possible."""
        if self.surface:
            widget = self.surface
            surface_blit = surface.blit
            x, y = self.rect.topleft
            for rect in dirty:
                clip = rect.move((-x, -y))
                surface_blit(widget, (rect.x, rect.y), clip)
        else:
            surface.fill((238, 238, 236), self.rect)

    def invalidate(self, rect=None):
        # Return if there is no parent.
        if self.parent is None:
            return None

        if rect is None:
            rect = self.rect
        else:
            rect = rect.clip(self.rect)

        self.parent.invalidate(rect)

    def update(self, delay):
        """Update the sprite's movement, etc. each frame.
        
        delay: The number of milliseconds since the last update.
        """
        pass

    # Sprite parent.
    __parent = None
    def get_parent(self):
        return self.__parent
    def set_parent(self, parent):
        self.__parent = parent
        if parent is not None and self not in parent:
            parent.add(self)
    parent = InheritProperty(get_parent, set_parent)

    # Sprite position.
    _position = (0, 0)
    def get_position(self):
        return self._position
    def set_position(self, position):
        previous = self._position
        self._position = position
        if self.parent is not None and previous != position:
            self.parent.paint()
    position = InheritProperty(get_position, set_position)

    # Sprite size.
    _size = (0, 0)
    def get_size(self):
        return self._size
    def set_size(self, size):
        previous = self._size
        self._size = size
        if self.parent is not None and previous != size:
#            # Redraw if size changed.
            self.parent.paint()
    size = InheritProperty(get_size, set_size)

