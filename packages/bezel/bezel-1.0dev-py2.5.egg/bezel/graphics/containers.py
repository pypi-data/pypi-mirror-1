from copy import copy

import pygame

from bezel.graphics.widget import Widget

class BaseContainer(Widget):
    """An abstract container which holds any number of children."""

    def __init__(self, *args, **kwargs):
        super(BaseContainer, self).__init__(*args, **kwargs)

        self.children = []
        self.mouse_grab = set()

    def __iter__(self):
        return iter(self.children)

    def add(self, child):
        """Appends the child to the container."""
        self.children.append(child)

        if child.parent is not self:
            child.parent = self

        self.paint()

    def insert(self, position, child):
        """Inserts the child at the relevant position."""
        self.children.insert(position, child)

        self.paint()

    def remove(self, child):
        """Removes the child from the container."""
        self.children.remove(child)
        child.parent = None

        self.paint()

    def get_at_position(self, x, y):
        """
        Returns all children at the specified position, based on its
        position and size allocation.
        """
        for child in self.children[::-1]:
            left, top, width, height = child.rect

            right = left + width
            bottom = top + height
            if left <= x and right > x and top <= y and bottom > y:
                yield child

    def _pump(self, events):
        super(BaseContainer, self)._pump(events)
        for child in self.children:
            child._pump(events)

    # Painting events.
    def draw(self, surface, dirty):
        """Draws each of the children in the container onto the surface."""
        if not dirty:
            return

        self_rect = self.rect
        dirty = [d.clip(self_rect) for d in dirty]

        for child in self.children:
            child_rect = child.rect

            child_dirty = []
            for rect in dirty:
                if child_rect.colliderect(rect):
                    rect = rect.clip(child_rect)
                    child_dirty.append(rect)

            if child_dirty:
                child.draw(surface, child_dirty)

    def update(self, delay):
        for child in self.children:
            child.update(delay)

class Container(BaseContainer):
    def paint(self):
        super(Container, self).paint()

        x, y = self.rect.topleft
        for child in self.children:
            previous = copy(child.rect)

            child.rect.topleft = child.position
            child.rect.move_ip(x, y)
            child.rect.size = child.size

            if child.rect.size != previous.size:
                child.paint()
            elif child.rect.topleft != previous.topleft:
                self.invalidate(previous)
                self.invalidate(child.rect)

class Bin(BaseContainer):
    """A container which holds a single child."""
    def __init__(self, child=None, *args, **kwargs):
        super(Bin, self).__init__(*args, **kwargs)

        if child is not None:
            self.child = child

    def paint(self):
        super(Bin, self).paint()

        if self.child:
            x, y = map(sum, zip(self.child.position, self.rect.topleft))
            previous = copy(self.child.rect)
            self.child.rect = pygame.Rect((x, y), self.rect.size)

            if self.child.rect.size != previous.size:
                self.child.paint()
            elif self.child.rect.topleft != previous.topleft:
                self.invalidate(previous)
                self.invalidate(self.child.rect)

    def add(self, child):
        """Replaces the child of the container with a new child."""
        if self.child is not None:
            self.remove(self.child)
        self.__child = child

        super(Bin, self).add(child)

    __child = None
    set_child = add
    def get_child(self):
        return self.__child
    child = property(get_child, set_child)

    def insert(self, index, child):
        """Replaces the child of the container with a new child."""
        raise NotImplementedError

    def remove(self, child):
        """Removes the child from the container."""
        super(Bin, self).remove(child)
        self.__child = None

